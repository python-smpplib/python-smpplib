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

"""SMPP client module"""

import binascii
import logging
import select
import socket
import struct
import warnings

from smpplib import consts, exceptions, smpp


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
    _ssl_context = None
    sequence_generator = None

    def __init__(
        self,
        host,
        port,
        timeout=5,
        sequence_generator=None,
        logger_name=None,
        ssl_context=None,
        allow_unknown_opt_params=None,
    ):
        self.host = host
        self.port = int(port)
        self._ssl_context = ssl_context
        self.timeout = timeout
        self.logger = logging.getLogger(logger_name or 'smpp.Client.{}'.format(id(self)))
        if sequence_generator is None:
            sequence_generator = SimpleSequenceGenerator()
        self.sequence_generator = sequence_generator

        if allow_unknown_opt_params is None:
            warnings.warn(
                "Unknown optional parameters during PDU parsing will stop "
                "causing an exception in a future smpplib version "
                "(in order to comply with the SMPP spec). To switch behavior "
                "now set allow_unknown_opt_params to True.",
                DeprecationWarning,
            )
            self.allow_unknown_opt_params = False
        else:
            self.allow_unknown_opt_params = allow_unknown_opt_params


        self._socket = self._create_socket()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._socket is not None:
            try:
                self.unbind()
            except (exceptions.PDUError, exceptions.ConnectionError) as e:
                if len(getattr(e, 'args', tuple())) > 1:
                    self.logger.warning('(%d) %s. Ignored', e.args[1], e.args[0])
                else:
                    self.logger.warning('%s. Ignored', e)
            self.disconnect()

    def __del__(self):
        if self._socket is not None:
            self.logger.warning('%s was not closed', self)

    @property
    def sequence(self):
        return self.sequence_generator.sequence

    def next_sequence(self):
        return self.sequence_generator.next_sequence()

    def _create_socket(self):
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.settimeout(self.timeout)

        if self._ssl_context is None:
            return raw_socket

        return self._ssl_context.wrap_socket(raw_socket)

    def connect(self):
        """Connect to SMSC"""

        self.logger.info('Connecting to %s:%s...', self.host, self.port)

        try:
            if self._socket is None:
                self._socket = self._create_socket()
            self._socket.connect((self.host, self.port))
            self.state = consts.SMPP_CLIENT_STATE_OPEN
        except socket.error:
            raise exceptions.ConnectionError("Connection refused")

    def disconnect(self):
        """Disconnect from the SMSC"""
        self.logger.info('Disconnecting...')

        if self.state != consts.SMPP_CLIENT_STATE_OPEN:
            self.logger.warning('%s is disconnecting in the bound state', self)
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self.state = consts.SMPP_CLIENT_STATE_CLOSED

    def _bind(self, command_name, **kwargs):
        """Send bind_transmitter command to the SMSC"""

        if command_name in ('bind_receiver', 'bind_transceiver'):
            self.logger.debug('Receiver mode')

        p = smpp.make_pdu(command_name, client=self, **kwargs)

        self.send_pdu(p)
        try:
            resp = self.read_pdu()
        except socket.timeout:
            raise exceptions.ConnectionError()
        if resp.is_error():
            raise exceptions.PDUError('({}) {}: {}'.format(
                resp.status,
                resp.command,
                consts.DESCRIPTIONS.get(resp.status, 'Unknown code')),
                int(resp.status),
            )
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

        if self.state not in consts.COMMAND_STATES[p.command]:
            raise exceptions.PDUError("Command %s failed: %s" % (
                p.command,
                consts.DESCRIPTIONS[consts.SMPP_ESME_RINVBNDSTS],
            ))

        self.logger.debug('Sending %s PDU', p.command)
        generated = p.generate()
        self.logger.debug('>>%s (%d bytes)', binascii.b2a_hex(generated), len(generated))

        try:
            self._socket.sendall(generated)
        except socket.error as e:
            self.logger.warning(e)
            raise exceptions.ConnectionError()

        return True

    def _recv_exact(self, exact_size):
        """
        Keep reading from self._socket until exact_size bytes have been read
        """
        parts = []
        received = 0
        while received < exact_size:
            try:
                part = self._socket.recv(exact_size - received)
            except socket.timeout:
                raise
            except socket.error as e:
                self.logger.warning(e)
                raise exceptions.ConnectionError()
            if not part:
                raise exceptions.ConnectionError()
            received += len(part)
            parts.append(part)
        return b"".join(parts)
    
    def read_pdu(self):
        """Read PDU from the SMSC"""

        self.logger.debug('Waiting for PDU...')

        raw_len = self._recv_exact(4)

        try:
            length = struct.unpack('>L', raw_len)[0]
        except struct.error:
            self.logger.warning('Receive broken pdu... %s', repr(raw_len))
            raise exceptions.PDUError('Broken PDU')

        raw_pdu = raw_len + self._recv_exact(length - 4)

        self.logger.debug('<<%s (%d bytes)', binascii.b2a_hex(raw_pdu), len(raw_pdu))

        pdu = smpp.parse_pdu(
            raw_pdu,
            client=self,
            allow_unknown_opt_params=self.allow_unknown_opt_params,
        )

        self.logger.debug('Read %s PDU', pdu.command)

        if pdu.is_error():
            return pdu

        elif pdu.command in consts.STATE_SETTERS:
            self.state = consts.STATE_SETTERS[pdu.command]

        return pdu
    
    def read_rawpdu(self):
        """Read PDU from the SMSC"""

        raw_len = self._recv_exact(4)

        try:
            length = struct.unpack('>L', raw_len)[0]
        except struct.error:
            self.logger.warning('Receive broken pdu... %s', repr(raw_len))
            raise exceptions.PDUError('Broken PDU')

        raw_pdu = raw_len + self._recv_exact(length - 4)
        raw_pdu = binascii.b2a_hex(raw_pdu)

        return raw_pdu

    def accept(self, obj):
        """Accept an object"""
        raise NotImplementedError('not implemented')

    def _message_received(self, pdu):
        """Handler for received message event"""
        status = self.message_received_handler(pdu=pdu)
        if status is None:
            status = consts.SMPP_ESME_ROK
        dsmr = smpp.make_pdu('deliver_sm_resp', client=self, status=status)
        dsmr.sequence = pdu.sequence
        self.send_pdu(dsmr)

    def _enquire_link_received(self, pdu):
        """Response to enquire_link"""
        ler = smpp.make_pdu('enquire_link_resp', client=self)
        ler.sequence = pdu.sequence
        self.send_pdu(ler)

    def _alert_notification(self, pdu):
        """Handler for alert notification event"""
        self.message_received_handler(pdu=pdu)

    def set_message_received_handler(self, func):
        """Set new function to handle message receive event"""
        self.message_received_handler = func

    def set_message_sent_handler(self, func):
        """Set new function to handle message sent event"""
        self.message_sent_handler = func
        
    def set_query_resp_handler(self, func):
        """Set new function to handle query resp event"""
        self.query_resp_handler = func

    def set_error_pdu_handler(self, func):
        """Set new function to handle PDUs with an error status"""
        self.error_pdu_handler = func

    def message_received_handler(self, pdu, **kwargs):
        """Custom handler to process received message. May be overridden"""
        self.logger.warning('Message received handler (Override me)')

    def message_sent_handler(self, pdu, **kwargs):
        """
        Called when SMPP server accept message (SUBMIT_SM_RESP).
        May be overridden
        """
        self.logger.warning('Message sent handler (Override me)')

    def query_resp_handler(self, pdu, **kwargs):
        """Custom handler to process response to queries. May be overridden"""
        self.logger.warning('Query resp handler (Override me)')

    def error_pdu_handler(self, pdu):
        raise exceptions.PDUError('({}) {}: {}'.format(
            pdu.status,
            pdu.command,
            consts.DESCRIPTIONS.get(pdu.status, 'Unknown status')),
            int(pdu.status),
        )
    
    def read_once_rawpdu(self, ignore_error_codes=None, auto_send_enquire_link=True):

        if ignore_error_codes is not None:
            warnings.warn(
                "ignore_error_codes is deprecated, use set_error_pdu_handler to "
                "configure a custom error PDU handler instead.",
                DeprecationWarning,
            )


        try:
            ascii_pdu = self.read_rawpdu()
        except socket.timeout:
            if not auto_send_enquire_link:
                raise
            self.logger.debug('Socket timeout, listening again')
            pdu = smpp.make_pdu('enquire_link', client=self)
            self.send_pdu(pdu)
            return
            
        return ascii_pdu
    
    def read_once(self, ignore_error_codes=None, auto_send_enquire_link=True):
        """Read a PDU and act"""

        if ignore_error_codes is not None:
            warnings.warn(
                "ignore_error_codes is deprecated, use set_error_pdu_handler to "
                "configure a custom error PDU handler instead.",
                DeprecationWarning,
            )

        try:
            try:
                pdu = self.read_pdu()
            except socket.timeout:
                if not auto_send_enquire_link:
                    raise
                self.logger.debug('Socket timeout, listening again')
                pdu = smpp.make_pdu('enquire_link', client=self)
                self.send_pdu(pdu)
                return

            if pdu.is_error():
                self.error_pdu_handler(pdu)

            if pdu.command == 'unbind':  # unbind_res
                self.logger.info('Unbind command received')
                return
            elif pdu.command == 'submit_sm_resp':
                self.message_sent_handler(pdu=pdu)
            elif pdu.command == 'deliver_sm':
                self._message_received(pdu)
            elif pdu.command == 'query_sm_resp':
                self.query_resp_handler(pdu)
            elif pdu.command == 'enquire_link':
                self._enquire_link_received(pdu)
            elif pdu.command == 'enquire_link_resp':
                pass
            elif pdu.command == 'alert_notification':
                self._alert_notification(pdu)
            else:
                self.logger.warning('Unhandled SMPP command "%s"', pdu.command)
        except exceptions.PDUError as e:
            if ignore_error_codes and len(e.args) > 1 and e.args[1] in ignore_error_codes:
                self.logger.warning('(%d) %s. Ignored.', e.args[1], e.args[0])
            else:
                raise

    def poll(self, ignore_error_codes=None, auto_send_enquire_link=True):
        """Act on available PDUs and return"""
        while True:
            readable, _writable, _exceptional = select.select([self._socket], [], [], 0)
            if not readable:
                break
            self.read_once(ignore_error_codes, auto_send_enquire_link)

    def listen(self, ignore_error_codes=None, auto_send_enquire_link=True):
        """Listen for PDUs and act"""
        while True:
            self.read_once(ignore_error_codes, auto_send_enquire_link)

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
    
    def send_message_rawpdu(self, **kwargs):
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
        
        try:
            ascii_pdu = self.read_rawpdu()
        except socket.timeout:
            raise exceptions.ConnectionError()
        
        return ssm, ascii_pdu

    def query_message(self, **kwargs):
        """Query message state

        Required Arguments:
            message_id -- SMSC assigned Message ID
            source_addr_ton -- Original source address TON
            source_addr_npi -- Original source address NPI
            source_addr -- Original source address (string)
        """

        qsm = smpp.make_pdu('query_sm', client=self, **kwargs)
        self.send_pdu(qsm)
        return qsm
