from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
import inspect

from .utils import MISSING_ATTRIBUTE, get_original_attribute


class Patcher:
    def __init__(self) -> None:
        self._patches: list[Patch] = []
        self._attr_stacks: list[_AttributeStack] = []

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
        attr_stack, created = self._get_or_create_attr_stack(patch.obj, patch.attr_name)
        try:
            attr_stack.apply_patch(patch)
        except Exception:
            if created and attr_stack.is_empty():
                self._remove_attr_stack(attr_stack)
            raise

    def restore_attribute_patch(self, patch: _AttrPatch) -> None:
        attr_stack = self._find_attr_stack(patch.obj, patch.attr_name)
        if attr_stack is None:
            return

        attr_stack.restore_patch(patch)
        if attr_stack.is_empty():
            self._remove_attr_stack(attr_stack)

    def unregister_patch(self, patch: Patch) -> None:
        try:
            self._patches.remove(patch)
        except ValueError:
            pass

    def _register_patch(self, patch: Patch) -> None:
        self._patches.append(patch)

    def _get_or_create_attr_stack(
        self,
        obj: object,
        attr_name: str,
    ) -> tuple[_AttributeStack, bool]:
        attr_stack = self._find_attr_stack(obj, attr_name)
        if attr_stack is not None:
            return attr_stack, False

        attr_stack = _AttributeStack(obj, attr_name)
        self._attr_stacks.append(attr_stack)
        return attr_stack, True

    def _find_attr_stack(
        self,
        obj: object,
        attr_name: str,
    ) -> _AttributeStack | None:
        for attr_stack in self._attr_stacks:
            if attr_stack.matches(obj, attr_name):
                return attr_stack
        return None

    def _remove_attr_stack(self, attr_stack: _AttributeStack) -> None:
        try:
            self._attr_stacks.remove(attr_stack)
        except ValueError:
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


class _AttributeStack:
    def __init__(self, obj: object, attr_name: str) -> None:
        self.obj = obj
        self.attr_name = attr_name

        self.base_restore_target = MISSING_ATTRIBUTE
        self.base_restore_via_setattr = False
        self._base_captured = False
        self.patches: list[_AttrPatch] = []

    def matches(self, obj: object, attr_name: str) -> bool:
        return self.obj is obj and self.attr_name == attr_name

    def is_empty(self) -> bool:
        return not self.patches

    def apply_patch(self, patch: _AttrPatch) -> None:
        if not self._base_captured:
            self._capture_base_state()

        setattr(self.obj, self.attr_name, patch.replacement)
        self.patches.append(patch)

    def restore_patch(self, patch: _AttrPatch) -> None:
        try:
            patch_index = self.patches.index(patch)
        except ValueError:
            return

        was_top_patch = patch_index == len(self.patches) - 1
        del self.patches[patch_index]

        if not was_top_patch:
            return

        if self.patches:
            setattr(self.obj, self.attr_name, self.patches[-1].replacement)
            return

        if self.base_restore_via_setattr:
            setattr(self.obj, self.attr_name, self.base_restore_target)
            return

        try:
            delattr(self.obj, self.attr_name)
        except AttributeError:
            pass

    def _capture_base_state(self) -> None:
        (
            self.base_restore_target,
            self.base_restore_via_setattr,
        ) = get_original_attribute(self.obj, self.attr_name, default=MISSING_ATTRIBUTE)

        if (
            not self.base_restore_via_setattr
            and self.base_restore_target is not MISSING_ATTRIBUTE
            and _has_data_descriptor_on_type(self.obj, self.attr_name)
        ):
            self.base_restore_via_setattr = True

        self._base_captured = True


def _has_data_descriptor_on_type(obj: object, attr_name: str) -> bool:
    if inspect.isclass(obj):
        return False

    try:
        type_attr = inspect.getattr_static(type(obj), attr_name)
    except AttributeError:
        return False

    return hasattr(type_attr, "__set__") or hasattr(type_attr, "__delete__")


patcher = Patcher()
