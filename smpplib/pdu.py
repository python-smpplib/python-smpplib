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

"""PDU module"""

import struct
import binascii

from . import command_codes
from . import exceptions

SMPP_ESME_ROK = 0x00000000

#
# Optional parameters map
#
optional_params = {
    'dest_addr_subunit': 0x0005,
    'dest_network_type': 0x0006,
    'dest_bearer_type': 0x0007,
    'dest_telematics_id': 0x0008,
    'source_addr_subunit': 0x000D,
    'source_network_type': 0x000E,
    'source_bearer_type': 0x000F,
    'source_telematics_id': 0x010,
    'qos_time_to_live': 0x0017,
    'payload_type': 0x0019,
    'additional_status_info_text': 0x01D,
    'receipted_message_id': 0x001E,
    'ms_msg_wait_facilities': 0x0030,
    'privacy_indicator': 0x0201,
    'source_subaddress': 0x0202,
    'dest_subaddress': 0x0203,
    'user_message_reference': 0x0204,
    'user_response_code': 0x0205,
    'source_port': 0x020A,
    'destination_port': 0x020B,
    'sar_msg_ref_num': 0x020C,
    'language_indicator': 0x020D,
    'sar_total_segments': 0x020E,
    'sar_segment_seqnum': 0x020F,
    'sc_interface_version': 0x0210,#0x1002,
    'callback_num_pres_ind': 0x0302,
    'callback_num_atag': 0x0303,
    'number_of_messages': 0x0304,
    'callback_num': 0x0381,
    'dpf_result': 0x0420,
    'set_dpf': 0x0421,
    'ms_availability_status': 0x0422,
    'network_error_code': 0x0423,
    'message_payload': 0x0424,
    'delivery_failure_reason': 0x0425,
    'more_messages_to_send': 0x0426,
    'message_state': 0x0427,
    'ussd_service_op': 0x0501,
    'display_time': 0x1201,
    'sms_signal': 0x1203,
    'ms_validity': 0x1204,
    'alert_on_message_delivery': 0x130C,
    'its_reply_type': 0x1380,
    'its_session_info': 0x1383
}

sequence = 0


def extract_command(pdu):
    """Extract command from a PDU"""

    code = struct.unpack('>L', pdu[4:8])[0]

    return command_codes.get_command_name(code)


class default_client:
    """Dummy client"""
    sequence = 0

class PDU:
    """PDU class"""

    length = 0
    command = None
    status = None


    def __init__(self, client=default_client(), **kwargs):
        """Singleton dummy client will be used if ommited"""
        if client is None:
            self._client = default_client()


    def get_sequence(self):
        """Return global sequence number"""
        return self._client.sequence

    sequence = property(get_sequence)

    def _next_seq():
        """Return next sequence number"""
        self._client.sequence += 1

        return self._client.sequence

    def is_vendor(self):
        """Return True if this is a vendor PDU, False otherwise"""

        return hasattr(self, 'vendor')


    def is_request(self):
        """Return True if this is a request PDU, False otherwise"""

        return not self.is_response()


    def is_response(self):
        """Return True if this is a response PDU, False otherwise"""

        if command_codes.get_command_code(self.command) & 0x80000000:
            return True

        return False


    def is_error(self):
        """Return True if this is an error response, False otherwise"""

        if self.status != SMPP_ESME_ROK:
            return True

        return False


    def get_status_desc(self, status=None):
        """Return status description"""

        if status is None:
            status = self.status

        try:
            desc = exceptions.DESCRIPTIONS[status]
        except KeyError:
            return "Description for status 0x%x not found!" % status

        return desc

    def parse(self, data):
        """Parse raw PDU"""

        #
        # PDU format:
        #
        # Header (16 bytes)
        #   command_length: 4 bytes
        #   command_id: 4 bytes
        #   command_status: 4 bytes
        #   sequence_number: 4 bytes
        # Body (variable length)
        #   parameter
        #   parameter
        #   ...

        header = data[0:16]
        chunks = struct.unpack('>LLLL', header)
        self.length = chunks[0]
        self.command = extract_command(data)
        self.status = chunks[2]
        self.sequence = chunks[3]

        if len(data) > 16:
            self.parse_params(data[16:])


    def _unpack(self, format, data):
        """Unpack values. Uses struct.unpack. TODO: remove this"""

        return struct.unpack(format, data)


    def generate(self):
        """Generate raw PDU"""

        body = self.generate_params()

        self._length = len(body) + 16

        command_code = command_codes.get_command_code(self.command)

        header = struct.pack(">LLLL", self._length, command_code,
                             self.status, self.sequence)

        return header + body

