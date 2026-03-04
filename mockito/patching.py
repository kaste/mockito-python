from __future__ import annotations

import inspect
from collections.abc import Iterable, MutableMapping
from typing import Union


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
        self.had_attribute = False
        self.active = False

    def apply(self) -> None:
        if self.active:
            return

        self.original, self.had_attribute = _get_original_attribute(
            self.obj, self.attr_name
        )
        setattr(self.obj, self.attr_name, self.replacement)
        self.active = True

    def unstub(self) -> None:
        if not self.active:
            return

        if self.had_attribute:
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


def _get_original_attribute(obj: object, attr_name: str) -> tuple[object, bool]:
    try:
        return inspect.getattr_static(obj, attr_name), True
    except AttributeError:
        return _MISSING_ATTRIBUTE, False


def _normalize_remove(remove: object | None) -> tuple[object, ...]:
    if remove is None:
        return ()

    if isinstance(remove, (str, bytes)):
        return (remove,)

    if not isinstance(remove, Iterable):
        raise TypeError("remove must be iterable, all, or None")

    return tuple(remove)


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
