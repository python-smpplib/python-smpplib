`python-smpplib`
================

[![Version](https://img.shields.io/pypi/v/smpplib.svg?style=flat)](https://pypi.org/project/smpplib/#history)
[![Python versions](https://img.shields.io/pypi/pyversions/smpplib.svg?style=flat)](https://pypi.org/project/smpplib/)
[![PyPI downloads](https://img.shields.io/pypi/dm/smpplib.svg?style=flat)](https://pypi.org/project/smpplib/#files)
![License](https://img.shields.io/pypi/l/smpplib.svg?style=flat)
[![CircleCI](https://circleci.com/gh/python-smpplib/python-smpplib.svg?style=svg)](https://circleci.com/gh/python-smpplib/python-smpplib)

SMPP library for Python. Forked from [Google Code](https://code.google.com/p/smpplib/).

Example:

```python
import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

# if you want to know what's happening
logging.basicConfig(level='DEBUG')

# Two parts, UCS2, SMS with UDH
parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(u'Привет мир!\n'*10)

client = smpplib.client.Client('example.com', SOMEPORTNUMBER)

# Print when obtain message_id
client.set_message_sent_handler(
    lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
client.set_message_received_handler(
    lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))

client.connect()
client.bind_transceiver(system_id='login', password='secret')

for part in parts:
    pdu = client.send_message(
        source_addr_ton=smpplib.consts.SMPP_TON_INTL,
        #source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
        # Make sure it is a byte string, not unicode:
        source_addr='SENDERPHONENUM',

        dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
        #dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
        # Make sure thease two params are byte strings, not unicode:
        destination_addr='PHONENUMBER',
        short_message=part,

        data_coding=encoding_flag,
        esm_class=msg_type_flag,
        registered_delivery=True,
    )
    print(pdu.sequence)
client.listen()
```
You also may want to listen in a thread:
```python
from threading import Thread
t = Thread(target=client.listen)
t.start()
```

A simple in memory generator that produces sequence numbers for the PDU packages is used, which is reset on (re)instantiation of the client, e.g. by an application restart. It starts by default with sequence number 0x00000001 but you may set the starting sequence yourself by declaring the generator beforehand and passing it to the Client:
```python
import smpplib.client

generator = smpplib.client.SimpleSequenceGenerator(start_sequence=1234)
client = smpplib.client.Client('example.com', SOMEPORTNUMBER, sequence_generator=generator)
...
```


The client supports setting a custom generator, so if you need more/different features associated with it, you can implement your own:
```python
import smpplib.client

import mymodule

generator = mymodule.MyAwesomeSequenceGenerator()
client = smpplib.client.Client('example.com', SOMEPORTNUMBER, sequence_generator=generator)
...
```
