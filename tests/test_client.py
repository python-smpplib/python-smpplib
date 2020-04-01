import warnings

from smpplib.client import Client


def test_client_construction_allow_unknown_opt_params_warning():
    with warnings.catch_warnings(record=True) as w:
        client = Client("localhost", 5679)

    assert len(w) == 1
    assert "optional parameters" in str(w[0].message)
    assert not client.allow_unknown_opt_params
