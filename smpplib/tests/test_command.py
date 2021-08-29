from smpplib import consts, exceptions
from smpplib.command import DeliverSM, SubmitSM, SubmitSMResp

import pytest
from mock import Mock

def test_parse_submit_sm():
    # Example from smpp.org
    raw = bytes.fromhex(
        "000000480000000400000000000000020005004d656c726f73654c61627300"
        "01013434373731323334353637380000000000000100000010"
        "48656c6c6f20576f726c64201b650201"
    )
    pdu = SubmitSM('submit_sm', client=Mock())
    pdu.parse(raw)

    assert pdu.source_addr == b'MelroseLabs'
    assert pdu.destination_addr == b'447712345678'
    assert pdu.data_coding == consts.SMPP_ENCODING_DEFAULT
    assert pdu.short_message == b'Hello World \x1be\x02\x01'

    assert pdu.generate() == raw


def test_parse_submit_sm_resp():
    # Another example from smpp.org
    raw = bytes.fromhex(
        "00000051800000040000000000000002"
        "30393537326130613039626337336632653930653933386263366561386361326463663"
        "06364343562343039383165343632396638343035353534376561333100"
    )
    pdu = SubmitSMResp('submit_sm_resp', client=Mock())
    pdu.parse(raw)

    assert pdu.message_id == b'09572a0a09bc73f2e90e938bc6ea8ca2dcf0cd45b40981e4629f84055547ea31' # type: ignore

    assert pdu.generate() == raw

def test_parse_deliver_sm():
    raw = (
        b"\x00\x00\x00\xcb\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x01\x00"
        b"\x01\x0131600000000\x00\x05\x00XXX YYYY\x00\x04\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x0e\x00\x01\x01\x00\x06\x00\x01\x01\x00\x1e\x00"
        b"\t1d305b4c\x00\x04'\x00\x01\x02\x04$\x00rid:0489708364 sub:001"
        b" dlvrd:001 submit date:1810151907 done date:1810151907 stat:DELIVRD"
        b" err:000 text:\x04\x1f\x04@\x048\x042\x045\x04B\x04&\x00\x01\x01"
    )
    pdu = DeliverSM('deliver_sm')
    pdu.parse(raw)

    assert pdu.source_addr_ton == consts.SMPP_TON_INTL
    assert pdu.source_addr_npi == consts.SMPP_NPI_ISDN
    assert pdu.source_addr == b'31600000000'
    assert pdu.destination_addr == b'XXX YYYY'
    assert pdu.receipted_message_id == b'1d305b4c' # type: ignore
    assert pdu.source_network_type == consts.SMPP_NETWORK_TYPE_GSM # type: ignore
    assert pdu.message_state == consts.SMPP_MESSAGE_STATE_DELIVERED # type: ignore
    assert pdu.user_message_reference is None # type: ignore

    # TODO: not sure why this doesn't re-generate the raw input, but it seems
    # worth having this test anyway.
    assert pdu.generate() == b"\x00\x00\x00\xcb\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x0131600000000\x00\x05\x00XXX YYYY\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04$\x00rid:0489708364 sub:001 dlvrd:001 submit date:1810151907 done date:1810151907 stat:DELIVRD err:000 text:\x04\x1f\x04@\x048\x042\x045\x04B\x04'\x00\x01\x02\x00\x1e\x00\t1d305b4c\x00\x00\x0e\x00\x01\x01\x00\x06\x00\x01\x01\x04&\x00\x01\x01"

def test_unrecognised_optional_parameters():
    pdu = DeliverSM("deliver_sm", allow_unknown_opt_params=True)
    pdu.parse(b'\x00\x00\x00\xa8\x00\x00\x00\x05\x00\x00\x00\x00/p\xc6'
              b'\x9a\x00\x00\x0022549909028\x00\x01\x00\x00\x04\x00\x00'
              b'\x00\x00\x00\x00\x00\x00iid:795920026 sub:001 dlvrd:001 '
              b'submit date:200319131913 done date:200319131913 stat:DELIVRD err:000 text:'
              b'\x14\x03\x00\x07(null)\x00\x14\x02\x00\x04612\x00'
    )

    # This is only to avoid a breaking change, at some point the other behaviour
    # should become the default.
    with pytest.raises(exceptions.UnknownCommandError):
        pdu2 = DeliverSM("deliver_sm")
        pdu2.parse(b'\x00\x00\x00\xa8\x00\x00\x00\x05\x00\x00\x00\x00/p\xc6'
                  b'\x9a\x00\x00\x0022549909028\x00\x01\x00\x00\x04\x00\x00'
                  b'\x00\x00\x00\x00\x00\x00iid:795920026 sub:001 dlvrd:001 '
                  b'submit date:200319131913 done date:200319131913 stat:DELIVRD err:000 text:'
                  b'\x14\x03\x00\x07(null)\x00\x14\x02\x00\x04612\x00'
        )
