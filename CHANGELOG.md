### `2.1.0`

* New: add option to not use UDHI when splitting long SMS
* New: add `query_sm` & `query_sm_resp` support
* New: argument to make automatic `enquire_link` optional
* New: make logger specific to each `Client` instance by @Lynesth
* Fix: incorrect `SMPP_UDHIEIE_PORT16` constant #81
* Fix: `enquire_link_resp` now echo original sequence
* Fix: wait for the full PDU before parsing #82
* Fix: add timeout to Client's properties #98 by @Lynesth
* Fix: `DataSM` param naming error: `alert_on_message_delivery` #108 by @nwnoga

### `2.0.1`

* Fix: don't use `%` operator in logging

### `2.0`

* Fix `TypeError` in `_generate_string_tlv` when encoding a value
* Support context manager interface, move `__del__` functionality to `__exit__`
* Change `callback_num` type to Octet String
* Add message state and network type constants
* Fix trailing NULL character in parsed octet strings
* Add optional fields for `deliver_sm` PDU (couldn't find them in specs but observed in real systems)
* Fix integers converted to strings
* Fix integer pack format for `size=4`, closes #51
* Fix typos in `SMPP_INT_NOTIFICATION_*` constants
* Raise an error if `message_payload` is used together with `short_message`

### `1.0.3`

* Fix UCS-2 encoding: fixes #49 and #53

### `1.0.2`

* Add `tox.ini`, support `2.6`, `2.7`, `3.4`, `3.5`, `3.6` and `3.7`
* Drop Python `3.2` and `3.3` support
* Improve PEP8-compliance in a few places
* Bump version to `1.0.2` and mark it as stable
* Add classifiers to `setup.py`
* Improve `.gitignore` with standard templates for popular environments
* Remove some dead code in comments
