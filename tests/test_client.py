"""Basic tests for protocol client helpers."""

from __future__ import annotations

import asyncio
import json

import pytest

from custom_components.gree_versati_extended import client as client_module
from custom_components.gree_versati_extended.client import (
    ENCRYPTION_ECB,
    ENCRYPTION_GCM,
    GreeVersatiClientError,
    GreeVersatiProtocolClient,
)


def make_client(retries: int = 2) -> GreeVersatiProtocolClient:
    return GreeVersatiProtocolClient(
        host="127.0.0.1",
        port=7000,
        device_id="502cc62fc0be",
        key="1234567890abcdef",
        timeout=1,
        retries=retries,
    )


def test_validate_key_string_accepts_16_bytes() -> None:
    assert GreeVersatiProtocolClient.validate_key_string("1234567890abcdef")


def test_validate_key_string_rejects_non_16_bytes() -> None:
    assert not GreeVersatiProtocolClient.validate_key_string("short")


def test_validate_key_string_counts_utf8_bytes() -> None:
    assert not GreeVersatiProtocolClient.validate_key_string("123456789012345é")


def test_extract_values_from_opt_and_p() -> None:
    payload = {"opt": ["Pow", "Mod"], "p": [1, 2]}
    values = GreeVersatiProtocolClient._extract_values(payload)
    assert values == {"Pow": 1, "Mod": 2}


def test_extract_values_from_cols_and_dat() -> None:
    payload = {"cols": ["HeWatOutTemSet", "Pow"], "dat": [28, 1]}
    values = GreeVersatiProtocolClient._extract_values(payload)
    assert values == {"HeWatOutTemSet": 28, "Pow": 1}


def test_encrypt_decrypt_roundtrip_ecb() -> None:
    client = GreeVersatiProtocolClient(
        host="127.0.0.1",
        port=7000,
        device_id="502cc62fc0be",
        key="1234567890abcdef",
        timeout=5,
        retries=0,
    )
    payload = {"t": "status", "cols": ["Pow"], "mac": "502cc62fc0be"}
    packed, tag = client._encrypt_pack(payload, ENCRYPTION_ECB)
    unpacked = client._decrypt_pack(packed, tag, ENCRYPTION_ECB)
    assert unpacked == payload


def test_encrypt_decrypt_roundtrip_gcm() -> None:
    client = GreeVersatiProtocolClient(
        host="127.0.0.1",
        port=7000,
        device_id="502cc62fc0be",
        key="1234567890abcdef",
        timeout=5,
        retries=0,
    )
    payload = {"t": "status", "cols": ["Pow"], "mac": "502cc62fc0be"}
    packed, tag = client._encrypt_pack(payload, ENCRYPTION_GCM)
    assert tag is not None
    unpacked = client._decrypt_pack(packed, tag, ENCRYPTION_GCM)
    assert unpacked == payload


@pytest.mark.parametrize("encryption", [ENCRYPTION_ECB, ENCRYPTION_GCM])
def test_outer_message_contains_device_envelope_and_encrypted_payload(
    encryption: str,
) -> None:
    client = make_client()
    payload = {"t": "status", "cols": ["Pow"], "mac": "502cc62fc0be"}

    message = json.loads(client._build_outer_message(payload, encryption))

    assert message["cid"] == "app"
    assert message["i"] == 0
    assert message["t"] == "pack"
    assert message["uid"] == 0
    assert message["tcid"] == "502cc62fc0be"
    assert client._decrypt_pack(
        message["pack"],
        message.get("tag"),
        encryption,
    ) == payload
    assert ("tag" in message) is (encryption == ENCRYPTION_GCM)


def test_decrypt_gcm_rejects_missing_authentication_tag() -> None:
    client = make_client()

    with pytest.raises(GreeVersatiClientError, match="Missing GCM tag"):
        client._decrypt_pack("invalid", None, ENCRYPTION_GCM)


def test_async_get_filters_requested_values_and_remembers_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client()
    requests: list[tuple[dict[str, object], str, int | None]] = []

    def build_message(payload: dict[str, object], encryption: str) -> str:
        return json.dumps(payload)

    async def request(
        message: str,
        encryption: str,
        retries: int | None = None,
    ) -> dict[str, object]:
        requests.append((json.loads(message), encryption, retries))
        return {"opt": ["Pow", "Mod"], "p": [1, 4]}

    monkeypatch.setattr(client, "_build_outer_message", build_message)
    monkeypatch.setattr(client, "_async_request", request)

    assert asyncio.run(client.async_get(["Pow"])) == {"Pow": 1}
    assert requests == [
        (
            {"t": "status", "mac": "502cc62fc0be", "cols": ["Pow"]},
            ENCRYPTION_ECB,
            0,
        )
    ]

    requests.clear()
    assert asyncio.run(client.async_get(["Pow"])) == {"Pow": 1}
    assert requests == [
        (
            {"t": "status", "mac": "502cc62fc0be", "cols": ["Pow"]},
            ENCRYPTION_ECB,
            2,
        )
    ]


def test_async_get_requests_parameters_sequentially(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client()
    requests: list[list[str]] = []

    monkeypatch.setattr(
        client,
        "_build_outer_message",
        lambda payload, encryption: json.dumps(payload),
    )

    async def request(
        message: str,
        encryption: str,
        retries: int | None = None,
    ) -> dict[str, object]:
        payload = json.loads(message)
        keys = payload["cols"]
        requests.append(keys)
        return {"cols": keys, "dat": [1 if key == "Pow" else 4 for key in keys]}

    monkeypatch.setattr(client, "_async_request", request)

    assert asyncio.run(client.async_get(["Pow", "Mod"])) == {"Pow": 1, "Mod": 4}
    assert requests == [["Pow"], ["Mod"]]


def test_async_get_falls_back_to_compatible_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client()
    requests: list[tuple[dict[str, object], str, int | None]] = []

    monkeypatch.setattr(
        client,
        "_build_outer_message",
        lambda payload, encryption: json.dumps(payload),
    )

    async def request(
        message: str,
        encryption: str,
        retries: int | None = None,
    ) -> dict[str, object]:
        payload = json.loads(message)
        requests.append((payload, encryption, retries))
        if "opt" in payload:
            return {"opt": ["Pow"], "p": [1]}
        return {}

    monkeypatch.setattr(client, "_async_request", request)

    assert asyncio.run(client.async_get(["Pow"])) == {"Pow": 1}
    assert len(requests) == 3
    assert requests[-1][0] == {
        "t": "status",
        "mac": "502cc62fc0be",
        "opt": ["Pow"],
    }


def test_async_get_does_not_repeat_retries_for_fallback_formats(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client()
    retries_per_request: list[int | None] = []
    monkeypatch.setattr(
        client,
        "_build_outer_message",
        lambda payload, encryption: json.dumps(payload),
    )

    async def request(
        message: str,
        encryption: str,
        retries: int | None = None,
    ) -> dict[str, object]:
        retries_per_request.append(retries)
        return {}

    monkeypatch.setattr(client, "_async_request", request)

    with pytest.raises(GreeVersatiClientError, match="did not include requested"):
        asyncio.run(client.async_get(["Pow"]))

    assert retries_per_request == [0] * 8


def test_async_set_remembers_successful_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client()
    requests: list[tuple[dict[str, object], str, int | None]] = []

    monkeypatch.setattr(
        client,
        "_build_outer_message",
        lambda payload, encryption: json.dumps(payload),
    )

    async def request(
        message: str,
        encryption: str,
        retries: int | None = None,
    ) -> dict[str, object]:
        requests.append((json.loads(message), encryption, retries))
        return {"r": 0}

    monkeypatch.setattr(client, "_async_request", request)

    asyncio.run(client.async_set({"Pow": 1}))
    assert requests == [
        (
            {"t": "cmd", "opt": ["Pow"], "p": [1]},
            ENCRYPTION_ECB,
            0,
        )
    ]

    requests.clear()
    asyncio.run(client.async_set({"Pow": 0}))
    assert requests == [
        (
            {"t": "cmd", "opt": ["Pow"], "p": [0]},
            ENCRYPTION_ECB,
            2,
        )
    ]


def test_async_request_sends_udp_payload_and_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client(retries=0)
    loop = asyncio.new_event_loop()
    sent: list[tuple[bytes, tuple[str, int]]] = []
    sockets: list[object] = []

    class FakeSocket:
        def __init__(self) -> None:
            self.closed = False

        def setblocking(self, blocking: bool) -> None:
            assert blocking is False

        def close(self) -> None:
            self.closed = True

    def create_socket(*args: object) -> FakeSocket:
        sock = FakeSocket()
        sockets.append(sock)
        return sock

    async def sendto(sock: object, payload: bytes, address: tuple[str, int]) -> None:
        sent.append((payload, address))

    async def recvfrom(sock: object, max_bytes: int) -> tuple[bytes, tuple[str, int]]:
        return b'{"t":"status","r":0}', ("127.0.0.1", 7000)

    monkeypatch.setattr(loop, "sock_sendto", sendto)
    monkeypatch.setattr(loop, "sock_recvfrom", recvfrom)
    monkeypatch.setattr(client_module.socket, "socket", create_socket)

    try:
        result = loop.run_until_complete(
            client._async_request('{"request":true}', ENCRYPTION_ECB)
        )
    finally:
        loop.close()

    assert result == {"t": "status", "r": 0}
    assert sent == [(b'{"request":true}', ("127.0.0.1", 7000))]
    assert len(sockets) == 1
    assert sockets[0].closed


def test_async_request_retries_timeouts_and_closes_sockets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = make_client(retries=2)
    loop = asyncio.new_event_loop()
    sockets: list[object] = []
    receive_count = 0

    class FakeSocket:
        def __init__(self) -> None:
            self.closed = False

        def setblocking(self, blocking: bool) -> None:
            assert blocking is False

        def close(self) -> None:
            self.closed = True

    def create_socket(*args: object) -> FakeSocket:
        sock = FakeSocket()
        sockets.append(sock)
        return sock

    async def sendto(sock: object, payload: bytes, address: tuple[str, int]) -> None:
        return None

    async def recvfrom(sock: object, max_bytes: int) -> tuple[bytes, tuple[str, int]]:
        nonlocal receive_count
        receive_count += 1
        raise asyncio.TimeoutError

    monkeypatch.setattr(loop, "sock_sendto", sendto)
    monkeypatch.setattr(loop, "sock_recvfrom", recvfrom)
    monkeypatch.setattr(client_module.socket, "socket", create_socket)

    try:
        with pytest.raises(GreeVersatiClientError, match="after 3 attempts"):
            loop.run_until_complete(client._async_request("request", ENCRYPTION_ECB))
    finally:
        loop.close()

    assert receive_count == 3
    assert len(sockets) == 3
    assert all(sock.closed for sock in sockets)
