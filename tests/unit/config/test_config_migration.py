"""
Config migration 单元测试

规范:
  CF-01: 旧 napcat dict → 自动迁移到 adapters + _migrated=True
  CF-02: 新 adapters 格式 → 不迁移、_migrated=False
  CF-03: 两者都无 → 默认 napcat adapter、_migrated=False
  CF-04: AdapterEntry 字段验证
  CF-05: to_dict 不含内部标记
  CF-06: bot_uin/root 整数 coerce + websocket_timeout clamp
"""

import warnings


from ncatbot.utils.config.models import AdapterEntry, Config


# ---- CF-01: 旧格式迁移 ----


def test_legacy_napcat_migrated():
    """CF-01: 旧 napcat dict 自动迁移到 adapters，_migrated=True"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cfg = Config(
            **{
                "bot_uin": "999",
                "napcat": {"ws_uri": "ws://localhost:3001", "ws_token": "tok"},
            }
        )

    assert cfg._migrated is True
    assert len(cfg.adapters) == 1
    assert cfg.adapters[0].type == "napcat"
    assert cfg.adapters[0].platform == "qq"
    assert cfg.adapters[0].config["ws_uri"] == "ws://localhost:3001"
    # 旧 napcat 键应被移除
    assert cfg.napcat is None

    # 应发出 DeprecationWarning
    deprecations = [x for x in w if issubclass(x.category, DeprecationWarning)]
    assert len(deprecations) >= 1


def test_legacy_napcat_non_dict():
    """CF-01b: napcat 值为非 dict 时也迁移，但无 config"""
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        cfg = Config(**{"napcat": True})

    assert cfg._migrated is True
    assert len(cfg.adapters) == 1
    assert cfg.adapters[0].type == "napcat"
    assert cfg.adapters[0].config == {}


# ---- CF-02: 新格式 ----


def test_new_format_no_migration():
    """CF-02: 新 adapters 格式不触发迁移"""
    cfg = Config(
        adapters=[
            AdapterEntry(
                type="napcat", platform="qq", config={"ws_uri": "ws://localhost:3001"}
            )
        ]
    )

    assert cfg._migrated is False
    assert len(cfg.adapters) == 1
    assert cfg.adapters[0].type == "napcat"


# ---- CF-03: 都不存在 ----


def test_empty_config_defaults():
    """CF-03: 无 adapters 无 napcat → 默认创建 napcat adapter，_migrated=False"""
    cfg = Config()

    assert cfg._migrated is False
    assert len(cfg.adapters) == 1
    assert cfg.adapters[0].type == "napcat"
    assert cfg.adapters[0].platform == "qq"


def test_napcat_null_treated_as_absent():
    """CF-03b: napcat: null → 视为不存在"""
    cfg = Config(**{"napcat": None})

    assert cfg._migrated is False
    assert len(cfg.adapters) == 1
    assert cfg.adapters[0].type == "napcat"


# ---- CF-04: AdapterEntry 验证 ----


def test_adapter_entry_defaults():
    """CF-04: AdapterEntry 默认值"""
    entry = AdapterEntry(type="mock")

    assert entry.platform == ""
    assert entry.enabled is True
    assert entry.config == {}


def test_adapter_entry_full():
    """CF-04b: AdapterEntry 完整字段"""
    entry = AdapterEntry(
        type="napcat",
        platform="qq",
        enabled=False,
        config={"ws_uri": "wss://custom:3002"},
    )

    assert entry.type == "napcat"
    assert entry.platform == "qq"
    assert entry.enabled is False
    assert entry.config["ws_uri"] == "wss://custom:3002"


# ---- CF-05: to_dict ----


def test_to_dict_excludes_internal():
    """CF-05: to_dict 不含 _migrated 和 __migrated_sentinel"""
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        cfg = Config(**{"napcat": {"ws_uri": "ws://localhost:3001"}})

    d = cfg.to_dict()
    assert "_migrated" not in d
    assert "__migrated_sentinel" not in d
    assert "adapters" in d
    assert len(d["adapters"]) == 1


def test_to_dict_excludes_none():
    """CF-05b: to_dict 排除 None 值"""
    cfg = Config()
    d = cfg.to_dict()
    assert "napcat" not in d  # napcat=None 被 exclude_none 排除


# ---- CF-06: 字段 coerce / clamp ----


def test_bot_uin_int_coerced_to_str():
    """CF-06: bot_uin 整数自动转字符串"""
    cfg = Config(**{"bot_uin": 12345})
    assert cfg.bot_uin == "12345"


def test_root_int_coerced_to_str():
    """CF-06b: root 整数自动转字符串"""
    cfg = Config(**{"root": 67890})
    assert cfg.root == "67890"


def test_websocket_timeout_clamped():
    """CF-06c: websocket_timeout <= 0 被 clamp 到 1"""
    cfg = Config(**{"websocket_timeout": 0})
    assert cfg.websocket_timeout == 1

    cfg2 = Config(**{"websocket_timeout": -5})
    assert cfg2.websocket_timeout == 1
