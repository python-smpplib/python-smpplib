### 1.1 (unreleased)

* Support context manager interface, move `__del__` functionality to `__exit__`
* Change `callback_num` type to Octet String
* Add message state and network type constants
* Fix trailing NULL character in parsed octet strings
* Add optional fields for `deliver_sm` PDU (couldn't find them in specs but observed in real systems)
* Fix integers converted to strings
* Fix integer pack format for `size=4`, closes #51

### 1.0.3

* Fix UCS-2 encoding: fixes #49 and #53

### 1.0.2

* Add `tox.ini`, support `2.6`, `2.7`, `3.4`, `3.5`, `3.6` and `3.7`
* Drop Python `3.2` and `3.3` support
* Improve PEP8-compliance in a few places
* Bump version to `1.0.2` and mark it as stable
* Add classifiers to `setup.py`
* Improve `.gitignore` with standard templates for popular environments
* Remove some dead code in comments
