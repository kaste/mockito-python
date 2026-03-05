from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from contextlib import contextmanager
from dataclasses import dataclass
import inspect

from .utils import MISSING_ATTRIBUTE, get_original_attribute


@dataclass
class _RestoreInformation:
    obj: object
    attr_name: str
    original_value: object
    use_set_on_restore: bool


class Patcher:
    def __init__(self) -> None:
        self._patches: list[Patch] = []
        self._restore_infos: list[_RestoreInformation] = []

    def patch_attribute(
        self,
        obj: object,
        attr_name: str,
        replacement: object,
        *,
        allow_unstub_by_replacement: bool,
    ) -> _AttrPatch:
        attr_patch = _AttrPatch(
            registry=self,
            obj=obj,
            attr_name=attr_name,
            replacement=replacement,
            allow_unstub_by_replacement=allow_unstub_by_replacement,
        )
        attr_patch.apply()
        self._register_patch(attr_patch)
        return attr_patch

    def patch_dictionary(
        self,
        target: MutableMapping[object, object],
        updates: dict[object, object],
        *,
        clear: bool = False,
        remove: tuple[object, ...] = (),
    ) -> _DictPatch:
        dict_patch = _DictPatch(
            registry=self,
            target=target,
            updates=updates,
            clear=clear,
            remove=remove,
        )
        dict_patch.apply()
        self._register_patch(dict_patch)
        return dict_patch

    def unstub_matching(self, obj: object) -> None:
        matching = [
            patch for patch in self._patches
            if patch.matches_unstub_target(obj)
        ]
        for patch in reversed(matching):
            patch.restore_and_unregister()

    def unstub_all(self) -> None:
        for patch in reversed(self._patches.copy()):
            patch.restore_and_unregister()

    def apply_attribute_patch(self, patch: _AttrPatch) -> None:
        with self._capture_restore_information(patch):
            setattr(patch.obj, patch.attr_name, patch.replacement)

    def restore_attribute_patch(self, patch: _AttrPatch) -> None:
        stack = self._stack_for_attr_patch(patch)
        if not stack or stack[0] is not patch:
            return

        if len(stack) > 1:
            setattr(patch.obj, patch.attr_name, stack[1].replacement)
            return

        restore_info = self._find_restore_information(patch.obj, patch.attr_name)
        if restore_info:
            _restore_original_attribute(restore_info)
            self._remove_restore_information(restore_info)

    def unregister_patch(self, patch: Patch) -> None:
        try:
            self._patches.remove(patch)
        except ValueError:
            pass

    def _register_patch(self, patch: Patch) -> None:
        self._patches.append(patch)

    @contextmanager
    def _capture_restore_information(self, patch: _AttrPatch):
        has_restore_info = self._has_restore_information(patch.obj, patch.attr_name)

        if not has_restore_info:
            restore_info = _capture_restore_information(patch.obj, patch.attr_name)

        try:
            yield
        except Exception:
            raise
        else:
            if not has_restore_info:
                self._restore_infos.append(restore_info)

    def _stack_for_attr_patch(self, patch: _AttrPatch) -> list[_AttrPatch]:
        return [
            candidate
            for candidate in reversed(self._patches)
            if isinstance(candidate, _AttrPatch)
            if candidate.active
            if candidate.obj is patch.obj
            if candidate.attr_name == patch.attr_name
        ]

    def _has_restore_information(self, obj: object, attr_name: str) -> bool:
        return self._find_restore_information(obj, attr_name) is not None

    def _find_restore_information(
        self, obj: object, attr_name: str
    ) -> _RestoreInformation | None:
        for restore_info in self._restore_infos:
            if restore_info.obj is obj and restore_info.attr_name == attr_name:
                return restore_info
        return None

    def _remove_restore_information(self, restore_info: _RestoreInformation) -> None:
        try:
            self._restore_infos.remove(restore_info)
        except ValueError:
            pass


def _capture_restore_information(obj: object, attr_name: str) -> _RestoreInformation:
    original_value, use_set_on_restore = get_original_attribute(
        obj, attr_name, default=MISSING_ATTRIBUTE
    )

    if (
        not use_set_on_restore
        and original_value is not MISSING_ATTRIBUTE
        and _has_data_descriptor_on_type(obj, attr_name)
    ):
        use_set_on_restore = True

    return _RestoreInformation(
        obj=obj,
        attr_name=attr_name,
        original_value=original_value,
        use_set_on_restore=use_set_on_restore,
    )


def _restore_original_attribute(restore_info: _RestoreInformation) -> None:
    if restore_info.use_set_on_restore:
        setattr(
            restore_info.obj,
            restore_info.attr_name,
            restore_info.original_value
        )
        return

    try:
        delattr(restore_info.obj, restore_info.attr_name)
    except AttributeError:
        pass


class Patch(ABC):
    def __init__(self, registry: Patcher) -> None:
        self.registry = registry
        self.active = False

    @abstractmethod
    def apply(self) -> None:
        pass

    @abstractmethod
    def restore(self) -> None:
        pass

    @abstractmethod
    def matches_unstub_target(self, obj: object) -> bool:
        pass

    def restore_and_unregister(self) -> None:
        try:
            self.restore()
        finally:
            self.registry.unregister_patch(self)

    def __exit__(self, *exc_info) -> None:
        self.restore_and_unregister()


class _AttrPatch(Patch):
    def __init__(
        self,
        registry: Patcher,
        obj: object,
        attr_name: str,
        replacement: object,
        *,
        allow_unstub_by_replacement: bool,
    ):
        super().__init__(registry)
        self.obj = obj
        self.attr_name = attr_name
        self.replacement = replacement
        self.allow_unstub_by_replacement = allow_unstub_by_replacement

    def apply(self) -> None:
        if self.active:
            return

        self.registry.apply_attribute_patch(self)
        self.active = True

    def restore(self) -> None:
        if not self.active:
            return

        self.registry.restore_attribute_patch(self)
        self.active = False

    def matches_unstub_target(self, obj: object) -> bool:
        return self.obj is obj or (
            self.allow_unstub_by_replacement and self.replacement is obj
        )

    def __enter__(self):
        return self.replacement


class _DictPatch(Patch):
    def __init__(
        self,
        registry: Patcher,
        target: MutableMapping[object, object],
        updates: dict[object, object],
        *,
        clear: bool,
        remove: tuple[object, ...],
    ):
        super().__init__(registry)
        self.target = target
        self.updates = updates
        self.clear = clear
        self.remove = remove

        self.original: dict[object, object] = {}

    def apply(self) -> None:
        if self.active:
            return

        self.original = dict(self.target)

        try:
            if self.clear:
                self.target.clear()
            else:
                for key in self.remove:
                    self.target.pop(key, None)

            self.target.update(self.updates)
        except Exception:
            self.target.clear()
            self.target.update(self.original)
            raise

        self.active = True

    def restore(self) -> None:
        if not self.active:
            return

        self.target.clear()
        self.target.update(self.original)

        self.active = False

    def matches_unstub_target(self, obj: object) -> bool:
        return self.target is obj

    def __enter__(self):
        return self.target


def _has_data_descriptor_on_type(obj: object, attr_name: str) -> bool:
    if inspect.isclass(obj):
        return False

    try:
        type_attr = inspect.getattr_static(type(obj), attr_name)
    except AttributeError:
        return False

    return hasattr(type_attr, "__set__") or hasattr(type_attr, "__delete__")


patcher = Patcher()
