"""The client, driven against a fake stove — no hardware, no network beyond the loopback."""

import asyncio

import pytest

from pyhaseiq import (
    Client,
    ConnectionFailedError,
    Phase,
    ProtocolError,
    ResponseTimeoutError,
)

from .fake import fake_stove, unreachable_port


async def test_the_context_manager_opens_and_closes_the_connection():
    async with fake_stove() as stove:
        client = Client(stove.host, stove.port)
        async with client as connected:
            assert connected is client
            assert await connected.get_phase() is Phase.NOMINAL
        # Once the block is left the socket is gone, and the client says so.
        with pytest.raises(ConnectionFailedError, match="not connected"):
            await client.get_phase()


async def test_every_typed_reading_parses_what_the_stove_answers():
    async with fake_stove() as stove, Client(stove.host, stove.port) as client:
        assert await client.get_temperature() == 163.3
        assert await client.get_phase() is Phase.NOMINAL
        assert await client.get_performance() == 69.0
        assert await client.get_heat_up_percent() == 53.5


async def test_a_raw_request_reaches_anything_the_protocol_documents():
    async with fake_stove() as stove, Client(stove.host, stove.port) as client:
        assert await client.get("_wversion") == "1.4"
        assert await client.get("_oemver") == "AAF_5815=9"
        assert await client.get("appP30Tx") == "30"


async def test_concurrent_readings_are_serialised_and_never_swap_answers():
    # The protocol has no request id: without the lock these would race and each await could
    # return the neighbour's frame.
    async with fake_stove() as stove, Client(stove.host, stove.port) as client:
        results = await asyncio.gather(
            *(client.get(name) for name in ("appT", "appPhase", "appP", "appAufheiz") * 5)
        )
    assert results == ["163.3", "2", "69", "53.5"] * 5


async def test_connecting_to_a_closed_port_fails_as_a_connection_error():
    port = await unreachable_port()
    with pytest.raises(ConnectionFailedError, match="cannot connect"):
        await Client("127.0.0.1", port).connect()


async def test_a_silent_stove_times_out():
    async with fake_stove() as stove:
        client = Client(stove.host, stove.port, timeout=0.2)
        async with client:
            # The fake never answers a name it does not know.
            with pytest.raises(ResponseTimeoutError, match="no answer"):
                await client.get("appUnknown")


async def test_an_unknown_phase_is_reported_rather_than_guessed():
    async with fake_stove({"appPhase": "9"}) as stove, Client(stove.host, stove.port) as client:
        with pytest.raises(ProtocolError, match="unknown phase"):
            await client.get_phase()


async def test_an_unreadable_frame_is_a_protocol_error():
    async with (
        fake_stove({"appT": "not base64 at all"}, encode=False) as stove,
        Client(stove.host, stove.port) as client,
    ):
        with pytest.raises(ProtocolError, match="not valid base64"):
            await client.get_temperature()


async def test_a_non_numeric_temperature_is_a_protocol_error():
    async with fake_stove({"appT": "warm"}) as stove, Client(stove.host, stove.port) as client:
        with pytest.raises(ProtocolError, match="expected a number"):
            await client.get_temperature()


async def test_connect_and_close_are_both_idempotent():
    async with fake_stove() as stove:
        client = Client(stove.host, stove.port)
        await client.connect()
        await client.connect()
        assert await client.get_phase() is Phase.NOMINAL
        await client.close()
        await client.close()


async def test_the_url_is_plain_websocket_on_the_configured_port():
    assert Client("192.168.1.165").url == "ws://192.168.1.165:8080"
    assert Client("stove.lan", 9000).url == "ws://stove.lan:9000"
