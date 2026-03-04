import gc
from collections.abc import MutableMapping
import os
import weakref

import pytest

from mockito import patch_dict, unstub


pytestmark = pytest.mark.usefixtures("unstub")


def test_patch_dict_updates_mapping_and_restores_on_unstub():
    config = {"user": "alice", "path": "/tmp"}

    patch_dict(config, {"user": "bob"})
    assert config == {"user": "bob", "path": "/tmp"}

    unstub(config)
    assert config == {"user": "alice", "path": "/tmp"}


def test_patch_dict_accepts_iterable_pairs_and_kwargs():
    config = {"user": "alice"}

    with patch_dict(config, [("path", "/tmp")], user="bob") as patched:
        assert patched is config
        assert config == {"user": "bob", "path": "/tmp"}

    assert config == {"user": "alice"}


def test_patch_dict_supports_dotted_path_target():
    key = "MOCKITO_PATCH_DICT_DOTTED_PATH_TEST_KEY"
    had_key = key in os.environ
    old_value = os.environ.get(key)

    with patch_dict("os.environ", {key: "set-by-mockito"}):
        assert os.environ[key] == "set-by-mockito"

    if had_key:
        assert os.environ.get(key) == old_value
    else:
        assert key not in os.environ


def test_patch_dict_remove_specific_keys():
    config = {"user": "alice", "path": "/tmp", "debug": "1"}

    with patch_dict(config, remove={"user", "path"}):
        assert config == {"debug": "1"}

    assert config == {"user": "alice", "path": "/tmp", "debug": "1"}


def test_patch_dict_remove_single_string_key():
    config = {"user": "alice", "path": "/tmp"}

    with patch_dict(config, remove="user"):
        assert config == {"path": "/tmp"}

    assert config == {"user": "alice", "path": "/tmp"}


def test_patch_dict_remove_all_with_builtin_all():
    config = {"user": "alice", "path": "/tmp"}

    with patch_dict(config, remove=all):
        assert config == {}

    assert config == {"user": "alice", "path": "/tmp"}


def test_patch_dict_clear_true_then_apply_updates():
    config = {"user": "alice", "path": "/tmp"}

    with patch_dict(config, {"user": "bob"}, clear=True):
        assert config == {"user": "bob"}

    assert config == {"user": "alice", "path": "/tmp"}


def test_patch_dict_nested_contexts_restore_in_lifo_order():
    config = {"mode": "prod"}

    with patch_dict(config, {"mode": "staging"}):
        assert config == {"mode": "staging"}

        with patch_dict(config, {"mode": "dev"}):
            assert config == {"mode": "dev"}

        assert config == {"mode": "staging"}

    assert config == {"mode": "prod"}


def test_patch_dict_rejects_non_mapping_target():
    with pytest.raises(TypeError) as exc:
        patch_dict(object(), {"user": "bob"})

    assert str(exc.value) == "target must be a mutable mapping"


class PartiallyFailingMapping(MutableMapping):
    def __init__(self, initial):
        self._store = dict(initial)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        if key == "bad":
            raise RuntimeError("boom")
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)


def test_patch_dict_failed_apply_rolls_back_partial_changes():
    target = PartiallyFailingMapping({"user": "alice", "path": "/tmp"})

    with pytest.raises(RuntimeError):
        patch_dict(target, [("user", "bob"), ("bad", "value")], clear=True)

    assert dict(target.items()) == {"user": "alice", "path": "/tmp"}


class ExplodingUpdateMapping(dict):
    def update(self, *args, **kwargs):
        raise RuntimeError("boom")


def test_patch_dict_failed_apply_does_not_keep_target_alive():
    target = ExplodingUpdateMapping()
    target_ref = weakref.ref(target)

    with pytest.raises(RuntimeError):
        patch_dict(target, {"user": "bob"})

    del target
    gc.collect()

    assert target_ref() is None
