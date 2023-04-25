from smpplib import consts, exceptions
from smpplib.client import Client
from smpplib.command import DeliverSM

import pytest


def test_parse_deliver_sm():
    client = Client("localhost", 5679)
    pdu = DeliverSM('deliver_sm', client=client)
    pdu.parse(
        b"\x00\x00\x00\xcb\x00\x00\x00\x05\x00\x00\x00\x00\x00\x00\x00\x01\x00"
        b"\x01\x0131600000000\x00\x05\x00XXX YYYY\x00\x04\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x0e\x00\x01\x01\x00\x06\x00\x01\x01\x00\x1e\x00"
        b"\t1d305b4c\x00\x04'\x00\x01\x02\x04$\x00rid:0489708364 sub:001"
        b" dlvrd:001 submit date:1810151907 done date:1810151907 stat:DELIVRD"
        b" err:000 text:\x04\x1f\x04@\x048\x042\x045\x04B\x04&\x00\x01\x01"
    )

    assert pdu.source_addr_ton == consts.SMPP_TON_INTL
    assert pdu.source_addr_npi == consts.SMPP_NPI_ISDN
    assert pdu.source_addr == b'31600000000'
    assert pdu.destination_addr == b'XXX YYYY'
    assert pdu.receipted_message_id == b'1d305b4c'
    assert pdu.source_network_type == consts.SMPP_NETWORK_TYPE_GSM
    assert pdu.message_state == consts.SMPP_MESSAGE_STATE_DELIVERED
    assert pdu.user_message_reference is None


def test_unrecognised_optional_parameters():
    client = Client("localhost", 5679)
    pdu = DeliverSM("deliver_sm", client=client, allow_unknown_opt_params=True)
    pdu.parse(b'\x00\x00\x00\xa8\x00\x00\x00\x05\x00\x00\x00\x00/p\xc6'
              b'\x9a\x00\x00\x0022549909028\x00\x01\x00\x00\x04\x00\x00'
              b'\x00\x00\x00\x00\x00\x00iid:795920026 sub:001 dlvrd:001 '
              b'submit date:200319131913 done date:200319131913 stat:DELIVRD err:000 text:'
              b'\x14\x03\x00\x07(null)\x00\x14\x02\x00\x04612\x00'
    )

    # This is only to avoid a breaking change, at some point the other behaviour
    # should become the default.
    with pytest.raises(exceptions.UnknownCommandError):
        pdu2 = DeliverSM("deliver_sm", client=client)
        pdu2.parse(b'\x00\x00\x00\xa8\x00\x00\x00\x05\x00\x00\x00\x00/p\xc6'
                  b'\x9a\x00\x00\x0022549909028\x00\x01\x00\x00\x04\x00\x00'
                  b'\x00\x00\x00\x00\x00\x00iid:795920026 sub:001 dlvrd:001 '
                  b'submit date:200319131913 done date:200319131913 stat:DELIVRD err:000 text:'
                  b'\x14\x03\x00\x07(null)\x00\x14\x02\x00\x04612\x00'
        )
