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
import struct
import binascii
import logging

from . import smpp
from . import pdu
from . import command
from . import exceptions

logger = logging.getLogger('smpplib.client')

SMPP_CLIENT_STATE_CLOSED = 0
SMPP_CLIENT_STATE_OPEN = 1
SMPP_CLIENT_STATE_BOUND_TX = 2
SMPP_CLIENT_STATE_BOUND_RX = 3
SMPP_CLIENT_STATE_BOUND_TRX = 4


command_states = {
    'bind_transmitter': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transmitter_resp': (SMPP_CLIENT_STATE_OPEN,),
    'bind_receiver': (SMPP_CLIENT_STATE_OPEN,),
    'bind_receiver_resp': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transceiver': (SMPP_CLIENT_STATE_OPEN,),
    'bind_transceiver_resp': (SMPP_CLIENT_STATE_OPEN,),
    'outbind': (SMPP_CLIENT_STATE_OPEN,),
    'unbind': (SMPP_CLIENT_STATE_BOUND_TX,
               SMPP_CLIENT_STATE_BOUND_RX,
               SMPP_CLIENT_STATE_BOUND_TRX,),
    'unbind_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                    SMPP_CLIENT_STATE_BOUND_RX,
                    SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm': (SMPP_CLIENT_STATE_BOUND_TX,
                  SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                       SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_multi': (SMPP_CLIENT_STATE_BOUND_TX,
                        SMPP_CLIENT_STATE_BOUND_TRX,),
    'submit_sm_multi_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                             SMPP_CLIENT_STATE_BOUND_TRX,),
    'data_sm': (SMPP_CLIENT_STATE_BOUND_TX,
                SMPP_CLIENT_STATE_BOUND_RX,
                SMPP_CLIENT_STATE_BOUND_TRX,),
    'data_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,),
    'deliver_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                   SMPP_CLIENT_STATE_BOUND_TRX,),
    'deliver_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                        SMPP_CLIENT_STATE_BOUND_TRX,),
    'query_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                 SMPP_CLIENT_STATE_BOUND_TRX,),
    'query_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                      SMPP_CLIENT_STATE_BOUND_TRX,),
    'cancel_sm': (SMPP_CLIENT_STATE_BOUND_RX,
                  SMPP_CLIENT_STATE_BOUND_TRX,),
    'cancel_sm_resp': (SMPP_CLIENT_STATE_BOUND_RX,
                       SMPP_CLIENT_STATE_BOUND_TRX,),
    'replace_sm': (SMPP_CLIENT_STATE_BOUND_TX,),
    'replace_sm_resp': (SMPP_CLIENT_STATE_BOUND_TX,),
    'enquire_link': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,),
    'enquire_link_resp': (SMPP_CLIENT_STATE_BOUND_TX,
                          SMPP_CLIENT_STATE_BOUND_RX,
                          SMPP_CLIENT_STATE_BOUND_TRX,),
    'alert_notification': (SMPP_CLIENT_STATE_BOUND_RX,
                           SMPP_CLIENT_STATE_BOUND_TRX,),
    'generic_nack': (SMPP_CLIENT_STATE_BOUND_TX,
                     SMPP_CLIENT_STATE_BOUND_RX,
                     SMPP_CLIENT_STATE_BOUND_TRX,)
}

state_setters = {
    'bind_transmitter_resp': SMPP_CLIENT_STATE_BOUND_TX,
    'bind_receiver_resp': SMPP_CLIENT_STATE_BOUND_RX,
    'bind_transceiver_resp': SMPP_CLIENT_STATE_BOUND_TRX,
    'unbind_resp': SMPP_CLIENT_STATE_OPEN
}


def log(*msg):
    """Log message"""

    msg = map(str, msg)

    logger.debug(' '.join(msg))


class Client(object):
    """SMPP client class"""

    state = SMPP_CLIENT_STATE_CLOSED

    host = None
    port = None
    vendor = None
    _socket = None
    sequence = 0


    def __init__(self, host, port, timeout=5):
        """Initialize"""

        self.host = host
        self.port = int(port)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(timeout)
        self.receiver_mode = False


    def __del__(self):
        try:
            self.unbind()
        except (exceptions.PDUError, exceptions.ConnectionError), e:
            logger.warning(e)
            pass
        self.disconnect()


    def connect(self):
        """Connect to SMSC"""

        log('Connecting to %s:%s...' % (self.host, self.port))

        try:
            if self._socket is None:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            self.state = SMPP_CLIENT_STATE_OPEN
        except socket.error:
            raise exceptions.ConnectionError("Connection refused")


    def disconnect(self):
        """Disconnect from the SMSC"""
        log('Disconnecting...')

        self._socket.close()
        self.state = SMPP_CLIENT_STATE_CLOSED
        self._socket = None


    def _bind(self, command_name, **kwargs):
        """Send bind_transmitter command to the SMSC"""

        if command_name in ('bind_receiver', 'bind_transceiver'):
            log('I am receiver')
            self.receiver_mode = True

        #smppinst = smpp.get_instance()
        p = smpp.make_pdu(command_name, client=self, **kwargs)

        res = self.send_pdu(p)
        return self.read_pdu()


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

        res = self.send_pdu(p)
        return self.read_pdu()


    def send_pdu(self, p):
        """Send PDU to the SMSC"""

        if not self.state in command_states[p.command]:
            raise exceptions.PDUError("Command %s failed: %s" \
                % (p.command, exceptions.DESCRIPTIONS[exceptions.SMPP_ESME_RINVBNDSTS]))

        log('Sending %s PDU' % (p.command))

        generated = p.generate()

        log('>>', binascii.b2a_hex(generated), len(generated), 'bytes')
        res = self._socket.send(generated)

        return True


    def read_pdu(self):
        """Read PDU from the SMSC"""

        log('Waiting for PDU...')

        raw_len = self._socket.recv(4)
        if raw_len == 0:
            raise exceptions.ConnectionError()

        try:
            length = struct.unpack('>L', raw_len)[0]
        except struct.error:
            #raise ConnectionError("Connection to server lost")
            log('Receive broken pdu...')
            raise exceptions.PDUError()

        raw_pdu = self._socket.recv(length - 4)
        raw_pdu = raw_len + raw_pdu

        log('<<', binascii.b2a_hex(raw_pdu), len(raw_pdu), 'bytes')

        cmd = pdu.extract_command(raw_pdu)
        log('Read %s PDU' % cmd)

        p = smpp.parse_pdu(raw_pdu)

        if p.is_error():
            raise exceptions.PDUError('({}) {}: {}'.format(p.status, p.command,
                exceptions.DESCRIPTIONS[p.status]), int(p.status))
        elif p.command in state_setters.keys():
            self.state = state_setters[p.command]

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
        ler = smpp.make_pdu('enquire_link_resp', client=self)
        #, message_id=args['pdu'].sm_default_msg_id)
        self.send_pdu(ler)
        log("Link Enuiry...")

    def set_message_received_handler(self, func):
        """Set new function to handle message receive event"""
        self.message_received_handler = func

    def set_message_sent_handler(self, func):
        """Set new function to handle message sent event"""
        self.message_sent_handler = func

    @staticmethod
    def message_received_handler(pdu, **kwargs):
        """Custom handler to process received message. May be overridden"""

        log('Message received handler (Override me)')

    @staticmethod
    def message_sent_handler(pdu, **kwargs):
        """Called when SMPP server accept message (SUBMIT_SM_RESP). May be overridden"""
        log('Message sent handler (Override me)')

    def listen(self):
        """Listen for PDUs and act"""

        while True:
            try:
                p = self.read_pdu()
            except socket.timeout:
                log('Socket timeout, listening again')
                p = smpp.make_pdu('enquire_link', client=self)
                self.send_pdu(p)
                continue

            if p.command == 'unbind': #unbind_res
                log('Unbind command received')
                break
            elif p.command == 'submit_sm_resp':
                self.message_sent_handler(pdu=p)
            elif p.command == 'deliver_sm':
                self._message_received(p)
            elif p.command == 'enquire_link':
                self._enquire_link_received()
            elif p.command == 'enquire_link_resp':
                pass
            else:
                logger.warning('Unhandled SMPP command "%s"', p.command)


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

#
# Main block for testing
#
if __name__ == '__main__':

    import sys
    sys.path.insert(0, '..')
    import smpplib

    def recv_handler(**kwargs):
        p = kwargs['pdu']
        msg = p.short_message
        logger.info('Message received: %s', msg)
        logger.info('Source address: %s', p.source_addr)
        logger.info('Destination address: %s', p.destination_addr)

    client = smpplib.client.Client('localhost', 11111)
    client.connect()

    client.set_message_received_handler(recv_handler)

    try:
        client.bind_transceiver(system_id='omni', password='omni', system_type='www')
        client.listen()
    finally:
        client.unbind()
        client.disconnect()

