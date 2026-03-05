from __future__ import annotations

from collections.abc import Iterable, MutableMapping
import inspect
from typing import Union

from .utils import get_original_attribute


_Patch = Union["_AttrPatch", "_DictPatch"]

_MISSING_ATTRIBUTE = object()
_PATCHES: list[_Patch] = []


def patch_attribute(obj: object, attr_name: str, replacement: object) -> _AttrPatch:
    attr_patch = _AttrPatch(obj, attr_name, replacement)
    attr_patch.apply()
    _register_patch(attr_patch)
    return attr_patch


def patch_dictionary(
    target: MutableMapping[object, object],
    updates: dict[object, object],
    *,
    clear: bool = False,
    remove: object | None = None,
) -> _DictPatch:
    if not isinstance(target, MutableMapping):
        raise TypeError("target must be a mutable mapping")

    if remove is all:
        clear = True
        remove = None

    normalized_remove = _normalize_remove(remove)
    dict_patch = _DictPatch(target, updates, clear=clear, remove=normalized_remove)
    dict_patch.apply()
    _register_patch(dict_patch)
    return dict_patch


def unstub_patches_matching(obj: object) -> None:
    matching = [
        patch
        for patch in _PATCHES
        if patch.matches(obj)
    ]
    for patch in reversed(matching):
        _unstub_and_unregister_patch(patch)


def unstub_all_patches() -> None:
    for patch in reversed(_PATCHES.copy()):
        _unstub_and_unregister_patch(patch)


class _AttrPatch:
    def __init__(self, obj: object, attr_name: str, replacement: object):
        self.obj = obj
        self.attr_name = attr_name
        self.replacement = replacement

        self.original = _MISSING_ATTRIBUTE
        self.restore_via_setattr = False
        self.active = False

    def apply(self) -> None:
        if self.active:
            return

        self.original, self.restore_via_setattr = get_original_attribute(
            self.obj, self.attr_name, default=_MISSING_ATTRIBUTE
        )
        if (
            not self.restore_via_setattr
            and self.original is not _MISSING_ATTRIBUTE
            and _has_data_descriptor_on_type(self.obj, self.attr_name)
        ):
            self.restore_via_setattr = True

        setattr(self.obj, self.attr_name, self.replacement)
        self.active = True

    def unstub(self) -> None:
        if not self.active:
            return

        if self.restore_via_setattr:
            setattr(self.obj, self.attr_name, self.original)
        else:
            try:
                delattr(self.obj, self.attr_name)
            except AttributeError:
                pass

        self.active = False

    def matches(self, obj: object) -> bool:
        return self.obj is obj or self.replacement is obj

    def __enter__(self):
        return self.replacement

    def __exit__(self, *exc_info) -> None:
        _unstub_and_unregister_patch(self)


class _DictPatch:
    def __init__(
        self,
        target: MutableMapping[object, object],
        updates: dict[object, object],
        *,
        clear: bool,
        remove: tuple[object, ...],
    ):
        self.target = target
        self.updates = updates
        self.clear = clear
        self.remove = remove

        self.original: dict[object, object] = {}
        self.active = False

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

    def unstub(self) -> None:
        if not self.active:
            return

        self.target.clear()
        self.target.update(self.original)

        self.active = False

    def matches(self, obj: object) -> bool:
        return self.target is obj

    def __enter__(self):
        return self.target

    def __exit__(self, *exc_info) -> None:
        _unstub_and_unregister_patch(self)


def _normalize_remove(remove: object | None) -> tuple[object, ...]:
    if remove is None:
        return ()

    if isinstance(remove, (str, bytes)):
        return (remove,)

    if not isinstance(remove, Iterable):
        raise TypeError("remove must be iterable, all, or None")

    return tuple(remove)


def _has_data_descriptor_on_type(obj: object, attr_name: str) -> bool:
    if inspect.isclass(obj):
        return False

    try:
        type_attr = inspect.getattr_static(type(obj), attr_name)
    except AttributeError:
        return False

    return hasattr(type_attr, "__set__") or hasattr(type_attr, "__delete__")


def _unstub_and_unregister_patch(patch: _Patch) -> None:
    try:
        patch.unstub()
    finally:
        _unregister_patch(patch)


def _register_patch(patch: _Patch) -> None:
    _PATCHES.append(patch)


def _unregister_patch(patch: _Patch) -> None:
    try:
        _PATCHES.remove(patch)
    except ValueError:
        pass
