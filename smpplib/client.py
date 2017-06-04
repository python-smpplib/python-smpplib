#
# smpplib -- SMPP Library for Python
# Copyright (c) 2005 Martynas Jocius <mjoc@akl.lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's

"""SMPP client module"""

import socket
import select
import struct
import binascii
import logging

from . import smpp
from . import exceptions
from . import consts

logger = logging.getLogger('smpplib.client')

class SimpleSequenceGenerator(object):

    MIN_SEQUENCE = 0x00000001
    MAX_SEQUENCE = 0x7FFFFFFF

    def __init__(self):
        self._sequence = self.MIN_SEQUENCE

    @property
    def sequence(self):
        return self._sequence

    def next_sequence(self):
        if self._sequence == self.MAX_SEQUENCE:
            self._sequence = self.MIN_SEQUENCE
        else:
            self._sequence += 1
        return self._sequence

class Client(object):
    """SMPP client class"""

    state = consts.SMPP_CLIENT_STATE_CLOSED

    host = None
    port = None
    vendor = None
    _socket = None
    sequence_generator = None

    def __init__(self, host, port, timeout=5, sequence_generator=None):
        """Initialize"""

        self.host = host
        self.port = int(port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self.receiver_mode = False
        if sequence_generator is None:
            sequence_generator = SimpleSequenceGenerator()
        self.sequence_generator = sequence_generator

    def __del__(self):
        """Disconnect when client object is destroyed"""
        if self._socket is not None:
            try:
                self.unbind()
            except (exceptions.PDUError, exceptions.ConnectionError) as e:
                if len(getattr(e, 'args', tuple())) > 1:
                    logger.warning('(%d) %s. Ignored', e.args[1], e.args[0])
                else:
                    logger.warning('%s. Ignored', e)
            self.disconnect()

    @property
    def sequence(self):
        return self.sequence_generator.sequence

    def next_sequence(self):
        return self.sequence_generator.next_sequence()

    def connect(self):
        """Connect to SMSC"""

        logger.info('Connecting to %s:%s...', self.host, self.port)

        try:
            if self._socket is None:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            self.state = consts.SMPP_CLIENT_STATE_OPEN
        except socket.error:
            raise exceptions.ConnectionError("Connection refused")

    def disconnect(self):
        """Disconnect from the SMSC"""
        logger.info('Disconnecting...')

        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self.state = consts.SMPP_CLIENT_STATE_CLOSED

    def _bind(self, command_name, **kwargs):
        """Send bind_transmitter command to the SMSC"""

        if command_name in ('bind_receiver', 'bind_transceiver'):
            logger.debug('Receiver mode')
            self.receiver_mode = True

        #smppinst = smpp.get_instance()
        p = smpp.make_pdu(command_name, client=self, **kwargs)

        self.send_pdu(p)
        try:
            resp = self.read_pdu()
        except socket.timeout:
            raise exceptions.ConnectionError()
        if resp.is_error():
            raise exceptions.PDUError(
                '({}) {}: {}'.format(resp.status, resp.command,
                consts.DESCRIPTIONS.get(resp.status, 'Unknown code')), int(resp.status))
        return resp

    def bind_transmitter(self, **kwargs):
        """Bind as a transmitter"""
        return self._bind('bind_transmitter', **kwargs)

    def bind_receiver(self, **kwargs):
        """Bind as a receiver"""
        return self._bind('bind_receiver', **kwargs)

    def bind_transceiver(self, **kwargs):
        """Bind as a transmitter and receiver at once"""
        return self._bind('bind_transceiver', **kwargs)

    def unbind(self):
        """Unbind from the SMSC"""

        p = smpp.make_pdu('unbind', client=self)

        self.send_pdu(p)
        try:
            return self.read_pdu()
        except socket.timeout:
            raise exceptions.ConnectionError()

    def send_pdu(self, p):
        """Send PDU to the SMSC"""

        if not self.state in consts.COMMAND_STATES[p.command]:
            raise exceptions.PDUError("Command %s failed: %s" %
                (p.command, consts.DESCRIPTIONS[consts.SMPP_ESME_RINVBNDSTS]))

        logger.debug('Sending %s PDU', p.command)

        generated = p.generate()

        logger.debug('>>%s (%d bytes)', binascii.b2a_hex(generated),
            len(generated))

        sent = 0

        while sent < len(generated):
            sent_last = 0
            try:
                sent_last = self._socket.send(generated[sent:])
            except socket.error as e:
                logger.warning(e)
                raise exceptions.ConnectionError()
            if sent_last == 0:
                raise exceptions.ConnectionError()
            sent += sent_last

        return True

    def read_pdu(self):
        """Read PDU from the SMSC"""

        logger.debug('Waiting for PDU...')

        try:
            raw_len = self._socket.recv(4)
        except socket.timeout:
            raise
        except socket.error as e:
            logger.warning(e)
            raise exceptions.ConnectionError()
        if not raw_len:
            raise exceptions.ConnectionError()

        try:
            length = struct.unpack('>L', raw_len)[0]
        except struct.error:
            logger.warning('Receive broken pdu... %s', repr(raw_len))
            raise exceptions.PDUError('Broken PDU')

        raw_pdu = self._socket.recv(length - 4)
        raw_pdu = raw_len + raw_pdu

        logger.debug('<<%s (%d bytes)', binascii.b2a_hex(raw_pdu), len(raw_pdu))

        p = smpp.parse_pdu(raw_pdu, client=self)

        logger.debug('Read %s PDU', p.command)

        if p.is_error():
            return p

        elif p.command in consts.STATE_SETTERS:
            self.state = consts.STATE_SETTERS[p.command]

        return p

    def accept(self, obj):
        """Accept an object"""
        raise NotImplementedError('not implemented')

    def _message_received(self, p):
        """Handler for received message event"""
        self.message_received_handler(pdu=p)
        dsmr = smpp.make_pdu('deliver_sm_resp', client=self)
        #, message_id=args['pdu'].sm_default_msg_id)
        dsmr.sequence = p.sequence
        self.send_pdu(dsmr)

    def _enquire_link_received(self):
        """Response to enquire_link"""
        ler = smpp.make_pdu('enquire_link_resp', client=self)
        #, message_id=args['pdu'].sm_default_msg_id)
        self.send_pdu(ler)
        logger.debug("Link Enquiry...")

    def _alert_notification(self, p):
        """Handler for alert notifiction event"""
        self.message_received_handler(pdu=p)

    def set_message_received_handler(self, func):
        """Set new function to handle message receive event"""
        self.message_received_handler = func

    def set_message_sent_handler(self, func):
        """Set new function to handle message sent event"""
        self.message_sent_handler = func

    @staticmethod
    def message_received_handler(pdu, **kwargs):
        """Custom handler to process received message. May be overridden"""

        logger.warning('Message received handler (Override me)')

    @staticmethod
    def message_sent_handler(pdu, **kwargs):
        """Called when SMPP server accept message (SUBMIT_SM_RESP).
        May be overridden"""
        logger.warning('Message sent handler (Override me)')


    def read_once(self, ignore_error_codes=None):
        """Read a PDU and act"""
        try:
            try:
                p = self.read_pdu()
            except socket.timeout:
                logger.debug('Socket timeout, listening again')
                p = smpp.make_pdu('enquire_link', client=self)
                self.send_pdu(p)
                return

            if p.is_error():
                raise exceptions.PDUError(
                    '({}) {}: {}'.format(p.status, p.command,
                    consts.DESCRIPTIONS.get(p.status, 'Unknown status')), int(p.status))

            if p.command == 'unbind':  # unbind_res
                logger.info('Unbind command received')
                return
            elif p.command == 'submit_sm_resp':
                self.message_sent_handler(pdu=p)
            elif p.command == 'deliver_sm':
                self._message_received(p)
            elif p.command == 'enquire_link':
                self._enquire_link_received()
            elif p.command == 'enquire_link_resp':
                pass
            elif p.command == 'alert_notification':
                self._alert_notification(p)
            else:
                logger.warning('Unhandled SMPP command "%s"', p.command)
        except exceptions.PDUError as e:
            if ignore_error_codes \
                    and len(e.args) > 1 \
                    and e.args[1] in ignore_error_codes:
                logging.warning('(%d) %s. Ignored.' %
                    (e.args[1], e.args[0]))
            else:
                raise

    def poll(self, ignore_error_codes=None):
        '''Act on available PDUs and return'''
        while True:
            readable, writable, exceptional = select.select([self._socket], [], [], 0)
            if not readable:
                break
            self.read_once(ignore_error_codes)

    def listen(self, ignore_error_codes=None):
        """Listen for PDUs and act"""
        while True:
            self.read_once(ignore_error_codes)

    def send_message(self, **kwargs):
        """Send message

        Required Arguments:
            source_addr_ton -- Source address TON
            source_addr -- Source address (string)
            dest_addr_ton -- Destination address TON
            destination_addr -- Destination address (string)
            short_message -- Message text (string)
        """

        ssm = smpp.make_pdu('submit_sm', client=self, **kwargs)
        self.send_pdu(ssm)
        return ssm
