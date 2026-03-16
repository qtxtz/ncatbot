"""
API 错误层级规范测试

规范:
  E-01: APIError 可用 retcode / message / wording 构造
  E-02: raise_for_retcode 在 retcode=0 时不抛异常
  E-03: raise_for_retcode 在 retcode=1400 时抛 APIRequestError
  E-04: raise_for_retcode 在 retcode=1401 时抛 APIPermissionError
  E-05: raise_for_retcode 在 retcode=1404 时抛 APINotFoundError
  E-06: raise_for_retcode 在未知 retcode 时抛 APIError
  E-07: APIError 子类是 APIError 的实例
"""

import pytest

from ncatbot.api.errors import (
    APIError,
    APIRequestError,
    APIPermissionError,
    APINotFoundError,
    raise_for_retcode,
)


# ---- E-01: 构造 ----


def test_api_error_construction():
    """E-01: APIError 可用 retcode / message 构造"""
    e = APIError(retcode=100, message="test", wording="hint")
    assert e.retcode == 100
    assert e.message == "test"
    assert e.wording == "hint"


# ---- E-02: retcode=0 不抛异常 ----


def test_raise_for_retcode_ok():
    """E-02: retcode=0 时 raise_for_retcode 不抛异常"""
    resp = {"status": "ok", "retcode": 0, "data": {"message_id": "1"}}
    raise_for_retcode(resp)  # 不应抛异常


def test_raise_for_retcode_missing_retcode():
    """E-02: 没有 retcode 字段时不抛异常"""
    raise_for_retcode({})  # 不应抛异常


# ---- E-03 ~ E-05: 特定 retcode ----


def test_raise_for_retcode_1400():
    """E-03: retcode=1400 抛 APIRequestError"""
    resp = {"status": "failed", "retcode": 1400, "message": "bad request"}
    with pytest.raises(APIRequestError) as exc_info:
        raise_for_retcode(resp)
    assert exc_info.value.retcode == 1400


def test_raise_for_retcode_1401():
    """E-04: retcode=1401 抛 APIPermissionError"""
    resp = {"status": "failed", "retcode": 1401, "message": "no permission"}
    with pytest.raises(APIPermissionError):
        raise_for_retcode(resp)


def test_raise_for_retcode_1404():
    """E-05: retcode=1404 抛 APINotFoundError"""
    resp = {"status": "failed", "retcode": 1404, "message": "not found"}
    with pytest.raises(APINotFoundError):
        raise_for_retcode(resp)


# ---- E-06: 未知 retcode ----


def test_raise_for_retcode_unknown():
    """E-06: 未知非零 retcode 抛基类 APIError"""
    resp = {"status": "failed", "retcode": 9999, "message": "unknown"}
    with pytest.raises(APIError) as exc_info:
        raise_for_retcode(resp)
    assert exc_info.value.retcode == 9999


# ---- E-07: 继承关系 ----


def test_subclass_is_api_error():
    """E-07: 所有子类都是 APIError 的实例"""
    assert issubclass(APIRequestError, APIError)
    assert issubclass(APIPermissionError, APIError)
    assert issubclass(APINotFoundError, APIError)
