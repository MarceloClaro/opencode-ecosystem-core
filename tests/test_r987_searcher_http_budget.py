from __future__ import annotations

import datetime as dt
import email.utils
import io
import urllib.error

import pytest

from research import searchers


class _Response:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self._body


def _http_error(code: int, headers: dict[str, str] | None = None):
    return urllib.error.HTTPError(
        "https://example.test/resource", code, "temporary test response",
        headers or {}, io.BytesIO(b"discarded fixture body"),
    )


def _patch_sleep(monkeypatch):
    delays = []
    monkeypatch.setattr(searchers.time, "sleep", delays.append)
    return delays


def test_retries_503_then_returns_success(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise _http_error(503)
        return _Response(b"ok")

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    assert searchers._http_get("https://example.test/resource") == "ok"
    assert len(calls) == 2
    assert sleeps == [pytest.approx(0.25)]


def test_respects_numeric_retry_after_within_budget(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise _http_error(429, {"Retry-After": "1.25"})
        return _Response(b"ok")

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    assert searchers._http_get("https://example.test/resource") == "ok"
    assert len(calls) == 2
    assert sleeps == [pytest.approx(1.25)]


def test_retry_after_http_date_in_the_past_causes_no_wait(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []
    retry_after = email.utils.format_datetime(
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1), usegmt=True,
    )

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise _http_error(503, {"Retry-After": retry_after})
        return _Response(b"ok")

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    assert searchers._http_get("https://example.test/resource") == "ok"
    assert len(calls) == 2
    assert sleeps == []


def test_retry_after_above_budget_fails_without_sleep(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        raise _http_error(429, {"Retry-After": "60"})

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(urllib.error.HTTPError) as caught:
        searchers._http_get("https://example.test/resource")

    assert caught.value.code == 429
    assert len(calls) == 1
    assert sleeps == []


def test_retry_wait_is_cumulative_not_reset_for_each_response(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        raise _http_error(429, {"Retry-After": "1.25"})

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(urllib.error.HTTPError) as caught:
        searchers._http_get("https://example.test/resource")

    assert caught.value.code == 429
    assert len(calls) == 2
    assert sleeps == [pytest.approx(1.25)]


def test_non_retryable_http_error_is_not_retried(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        raise _http_error(404)

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(urllib.error.HTTPError) as caught:
        searchers._http_get("https://example.test/resource")

    assert caught.value.code == 404
    assert len(calls) == 1
    assert sleeps == []


def test_persistent_503_stops_after_three_attempts(monkeypatch):
    sleeps = _patch_sleep(monkeypatch)
    calls = []

    def fake_urlopen(_request, timeout):
        calls.append(timeout)
        raise _http_error(503)

    monkeypatch.setattr(searchers.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(urllib.error.HTTPError) as caught:
        searchers._http_get("https://example.test/resource")

    assert caught.value.code == 503
    assert len(calls) == 3
    assert sleeps == [pytest.approx(0.25), pytest.approx(0.5)]


def test_json_wrapper_and_base_searcher_keep_their_contract(monkeypatch):
    monkeypatch.setattr(
        searchers.urllib.request,
        "urlopen",
        lambda _request, timeout: _Response(b'{"records": [1]}'),
    )
    assert searchers._http_get_json("https://example.test/resource") == {"records": [1]}

    class _FixtureSearcher(searchers.BaseSearcher):
        name = "fixture"

        def _search(self, query, limit):
            raise _http_error(503)

    assert _FixtureSearcher().search("query") == []
