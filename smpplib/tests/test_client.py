import time
import warnings

import pytest
from mock import call, Mock
from monotonic import monotonic

from smpplib import consts
from smpplib import exceptions
from smpplib.client import Client, ThreadSafeClient
from smpplib.smpp import make_pdu


def test_client_construction_allow_unknown_opt_params_warning():
    with warnings.catch_warnings(record=True) as w:
        client = Client("localhost", 5679)

    assert len(w) == 1
    assert "optional parameters" in str(w[0].message)
    assert not client.allow_unknown_opt_params


def test_client_error_pdu_default():
    client = Client("localhost", 5679)
    error_pdu = make_pdu("submit_sm_resp")
    error_pdu.status = consts.SMPP_ESME_RINVMSGLEN
    client.read_pdu = Mock(return_value=error_pdu)

    with pytest.raises(exceptions.PDUError) as exec_info:
        client.read_once()

    assert exec_info.value.args[1] == consts.SMPP_ESME_RINVMSGLEN

    # Should not raise
    client.read_once(ignore_error_codes=[consts.SMPP_ESME_RINVMSGLEN])


def test_client_error_pdu_custom_handler():
    client = Client("localhost", 5679)
    error_pdu = make_pdu("submit_sm_resp")
    error_pdu.status = consts.SMPP_ESME_RINVMSGLEN
    client.read_pdu = Mock(return_value=error_pdu)

    mock_error_pdu_handler = Mock()
    client.set_error_pdu_handler(mock_error_pdu_handler)

    client.read_once()

    assert mock_error_pdu_handler.mock_calls == [call(error_pdu)]


def test_prolongation():
    client = ThreadSafeClient("localhost", 5679)
    client._last_active_time = monotonic()
    assert not client._should_prolong_session()

    time.sleep(client.timeout - client._select_timeout)

    assert client._should_prolong_session()
