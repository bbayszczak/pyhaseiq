"""The encoding layer, checked against payloads captured from a real stove."""

import base64

import pytest

from pyhaseiq.exceptions import ProtocolError
from pyhaseiq.protocol import decode_response, encode_request, parse_float


def b64(text):
    return base64.b64encode(text.encode()).decode()


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        # Exact payloads read off the captures in records/.
        ("appPhase", "X3JlcT1hcHBQaGFzZQ=="),
        ("appErr", "X3JlcT1hcHBFcnI="),
        ("_oemdev", "X3JlcT1fb2VtZGV2"),
        ("_oemver", "X3JlcT1fb2VtdmVy"),
        ("_wversion", "X3JlcT1fd3ZlcnNpb24="),
    ],
)
def test_requests_are_encoded_exactly_as_the_vendor_app_does(name, expected):
    assert encode_request(name) == expected


def test_a_response_is_decoded_and_its_echoed_name_stripped():
    assert decode_response(b64("appT=163.3"), "appT") == "163.3"


def test_only_the_first_equals_sign_is_stripped():
    # _oemver really answers "_oemver=AAF_5815=9": the value carries its own '='.
    assert decode_response(b64("_oemver=AAF_5815=9"), "_oemver") == "AAF_5815=9"


def test_the_prefix_is_removed_as_a_prefix_not_as_a_character_set():
    # The regression this guards: lstrip("appT=") would eat the leading 'a', 'p' and 'T' of
    # the value too, and return "" here instead of "appT".
    assert decode_response(b64("appT=appT"), "appT") == "appT"


def test_a_request_name_holding_brackets_round_trips():
    name = "appP30T[15;29]"
    value = "41;40;40;40;40;39;39;39;39;39;38;38;38;70;13"
    assert decode_response(b64(f"{name}={value}"), name) == value


def test_a_frame_that_is_not_base64_is_a_protocol_error():
    with pytest.raises(ProtocolError, match="not valid base64"):
        decode_response("this is not base64!", "appT")


def test_a_frame_that_does_not_echo_the_request_is_a_protocol_error():
    with pytest.raises(ProtocolError, match="does not echo"):
        decode_response(b64("appPhase=2"), "appT")


def test_parse_float_reports_a_protocol_error_rather_than_a_value_error():
    assert parse_float("163.3", "appT") == 163.3
    with pytest.raises(ProtocolError, match="expected a number"):
        parse_float("warm", "appT")
