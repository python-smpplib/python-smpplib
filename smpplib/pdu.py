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

#
# SMPP error codes:
#
SMPP_ESME_ROK = 0x00000000
SMPP_ESME_RINVMSGLEN = 0x00000001
SMPP_ESME_RINVCMDLEN = 0x00000002
SMPP_ESME_RINVCMDID = 0x00000003
SMPP_ESME_RINVBNDSTS = 0x00000004
SMPP_ESME_RALYBND = 0x00000005
SMPP_ESME_RINVPRTFLG = 0x00000006
SMPP_ESME_RINVREGDLVFLG = 0x00000007
SMPP_ESME_RSYSERR = 0x00000008
SMPP_ESME_RINVSRCADR = 0x0000000A
SMPP_ESME_RINVDSTADR = 0x0000000B
SMPP_ESME_RINVMSGID = 0x0000000C
SMPP_ESME_RBINDFAIL = 0x0000000D
SMPP_ESME_RINVPASWD = 0x0000000E
SMPP_ESME_RINVSYSID = 0x0000000F
SMPP_ESME_RCANCELFAIL = 0x00000011
SMPP_ESME_RREPLACEFAIL = 0x00000013
SMPP_ESME_RMSGQFUL = 0x00000014
SMPP_ESME_RINVSERTYP = 0x00000015
SMPP_ESME_RINVNUMDESTS = 0x00000033
SMPP_ESME_RINVDLNAME = 0x00000034
SMPP_ESME_RINVDESTFLAG = 0x00000040
SMPP_ESME_RINVSUBREP = 0x00000042
SMPP_ESME_RINVESMCLASS = 0x00000043
SMPP_ESME_RCNTSUBDL = 0x00000044
SMPP_ESME_RSUBMITFAIL = 0x00000045
SMPP_ESME_RINVSRCTON = 0x00000048
SMPP_ESME_RINVSRCNPI = 0x00000049
SMPP_ESME_RINVDSTTON = 0x00000050
SMPP_ESME_RINVDSTNPI = 0x00000051
SMPP_ESME_RINVSYSTYP = 0x00000053
SMPP_ESME_RINVREPFLAG = 0x00000054
SMPP_ESME_RINVNUMMSGS = 0x00000055
SMPP_ESME_RTHROTTLED = 0x00000058
SMPP_ESME_RINVSCHED = 0x00000061
SMPP_ESME_RINVEXPIRY = 0x00000062
SMPP_ESME_RINVDFTMSGID = 0x00000063
SMPP_ESME_RX_T_APPN = 0x00000064
SMPP_ESME_RX_P_APPN = 0x00000065
SMPP_ESME_RX_R_APPN = 0x00000066
SMPP_ESME_RQUERYFAIL = 0x00000067
SMPP_ESME_RINVOPTPARSTREAM = 0x000000C0
SMPP_ESME_ROPTPARNOTALLWD = 0x000000C1
SMPP_ESME_RINVPARLEN = 0x000000C2
SMPP_ESME_RMISSINGOPTPARAM = 0x000000C3
SMPP_ESME_RINVOPTPARAMVAL = 0x000000C4
SMPP_ESME_RDELIVERYFAILURE = 0x000000FE
SMPP_ESME_RUNKNOWNERR = 0x000000FF


#
# Status description strings:
#
descs = {
    SMPP_ESME_ROK: 'No Error',
    SMPP_ESME_RINVMSGLEN: 'Message Length is invalid',
    SMPP_ESME_RINVCMDLEN: 'Command Length is invalid',
    SMPP_ESME_RINVCMDID: 'Invalid Command ID',
    SMPP_ESME_RINVBNDSTS: 'Incorrect BIND Status for given command',
    SMPP_ESME_RALYBND: 'ESME Already in Bound State',
    SMPP_ESME_RINVPRTFLG: 'Invalid Priority Flag',
    SMPP_ESME_RINVREGDLVFLG: '<Desc Not Set>',
    SMPP_ESME_RSYSERR: 'System Error',
    SMPP_ESME_RINVSRCADR: 'Invalid Source Address',
    SMPP_ESME_RINVDSTADR: 'Invalid Destination Address',
    SMPP_ESME_RINVMSGID: 'Invalid Message ID',
    SMPP_ESME_RBINDFAIL: 'Bind Failed',
    SMPP_ESME_RINVPASWD: 'Invalid Password',
    SMPP_ESME_RINVSYSID : 'Invalid System ID',
    SMPP_ESME_RCANCELFAIL: 'Cancel SM Failed',
    SMPP_ESME_RREPLACEFAIL: 'Replace SM Failed',
    SMPP_ESME_RMSGQFUL: 'Message Queue is full',
    SMPP_ESME_RINVSERTYP: 'Invalid Service Type',
    SMPP_ESME_RINVNUMDESTS: 'Invalid number of destinations',
    SMPP_ESME_RINVDLNAME: 'Invalid Distribution List name',
    SMPP_ESME_RINVDESTFLAG: 'Invalid Destination Flag (submit_multi)',
    SMPP_ESME_RINVSUBREP: 'Invalid Submit With Replace request (replace_if_present_flag set)',
    SMPP_ESME_RINVESMCLASS: 'Invalid esm_class field data',
    SMPP_ESME_RCNTSUBDL: 'Cannot submit to Distribution List',
    SMPP_ESME_RSUBMITFAIL: 'submit_sm or submit_multi failed',
    SMPP_ESME_RINVSRCTON: 'Invalid Source address TON',
    SMPP_ESME_RINVSRCNPI: 'Invalid Source address NPI',
    SMPP_ESME_RINVDSTTON: 'Invalid Destination address TON',
    SMPP_ESME_RINVDSTNPI: 'Invalid Destination address NPI',
    SMPP_ESME_RINVSYSTYP: 'Invalid system_type field',
    SMPP_ESME_RINVREPFLAG: 'Invalid replace_if_present flag',
    SMPP_ESME_RINVNUMMSGS : 'Invalid number of messages',
    SMPP_ESME_RTHROTTLED: 'Throttling error (ESME has exceeded allowed ' \
                          'message limits)',
    SMPP_ESME_RINVSCHED: 'Invalid Scheduled Delivery Time',
    SMPP_ESME_RINVEXPIRY: 'Invalid message validity period (Expiry Time)',
    SMPP_ESME_RINVDFTMSGID: 'Predefined Message is invalid or not found',
    SMPP_ESME_RX_T_APPN: 'ESME received Temporary App Error Code',
    SMPP_ESME_RX_P_APPN: 'ESME received Permanent App Error Code',
    SMPP_ESME_RX_R_APPN: 'ESME received Reject Message Error Code',
    SMPP_ESME_RQUERYFAIL: 'query_sm request failed',
    SMPP_ESME_RINVOPTPARSTREAM: 'Error in the optional part of the PDU body',
    SMPP_ESME_ROPTPARNOTALLWD: 'Optional Parameter not allowed',
    SMPP_ESME_RINVPARLEN: 'Invalid Parameter Length',
    SMPP_ESME_RMISSINGOPTPARAM: 'Expected Optional Parameter missing',
    SMPP_ESME_RINVOPTPARAMVAL: 'Invalid Optional Parameter Value',
    SMPP_ESME_RDELIVERYFAILURE: 'Delivery Failure (used data_sm_resp)',
    SMPP_ESME_RUNKNOWNERR: 'Unknown Error'
}


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


class PDU:
    """PDU class"""

    length = 0
    command = None
    status = None


    def __init__(self, **args):

        self.__dict__.update(**(args))

    def get_sequence(self):
        """Return global sequence number"""

        global sequence

        return sequence

    sequence = property(get_sequence)

    def _next_seq():
        """Return next sequence number"""
        global sequence

        sequence += 1

        return sequence

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
            desc = descs[status]
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
        self.command = self.extract_command(data)
        self.status = chunks[2]
        self.sequence = chunks[3]

        if len(data) > 16:
            self.parse_params(data[16:])

    @staticmethod
    def extract_command(pdu):
        """Extract command from a PDU"""

        code = struct.unpack('>L', pdu[4:8])[0]

        return command_codes.get_command_name(code)


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

