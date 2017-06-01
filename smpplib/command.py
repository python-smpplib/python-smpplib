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
# Modified by Yusuf Kaka <yusufk at gmail>
# Added support for Optional TLV's


"""SMPP Commands module"""

import struct
import logging
import six

from . import pdu
from . import exceptions
from . import consts
from .ptypes import ostr, flag

logger = logging.getLogger('smpplib.command')


def factory(command_name, **kwargs):
    """Return instance of a specific command class"""

    try:
        return {
            'bind_transmitter': BindTransmitter,
            'bind_transmitter_resp': BindTransmitterResp,
            'bind_receiver': BindReceiver,
            'bind_receiver_resp': BindReceiverResp,
            'bind_transceiver': BindTransceiver,
            'bind_transceiver_resp': BindTransceiverResp,
            'data_sm': DataSM,
            'data_sm_resp': DataSMResp,
            'generic_nack': GenericNAck,
            'submit_sm': SubmitSM,
            'submit_sm_resp': SubmitSMResp,
            'deliver_sm': DeliverSM,
            'deliver_sm_resp': DeliverSMResp,
            'unbind': Unbind,
            'unbind_resp': UnbindResp,
            'enquire_link': EnquireLink,
            'enquire_link_resp': EnquireLinkResp,
            'alert_notification': AlertNotification,
        }[command_name](command_name, **kwargs)
    except KeyError:
        raise exceptions.UnknownCommandError(
            'Command "%s" is not supported' % command_name)


def get_optional_name(code):
    """Return optional_params name by given code. If code is unknown, raise
    UnkownCommandError exception"""

    for key, value in six.iteritems(consts.OPTIONAL_PARAMS):
        if value == code:
            return key

    raise exceptions.UnknownCommandError(
        'Unknown SMPP command code "0x%x"' % code)


def get_optional_code(name):
    """Return optional_params code by given command name. If name is unknown,
    raise UnknownCommandError exception"""

    try:
        return consts.OPTIONAL_PARAMS[name]
    except KeyError:
        raise exceptions.UnknownCommandError(
            'Unknown SMPP command name "%s"' % name)


def unpack_short(data, pos):
    return struct.unpack('>H', data[pos:pos+2])[0], pos + 2


class Command(pdu.PDU):
    """SMPP PDU Command class"""

    params = {}

    def __init__(self, command, need_sequence=True, **kwargs):
        """Initialize"""

        super(Command, self).__init__(**kwargs)

        self.command = command
        if need_sequence and (kwargs.get('sequence') is None):
            self.sequence = self._next_seq()

        self.status = consts.SMPP_ESME_ROK

        #if self.is_vendor() and self.vdefs:
        #    self.defs = self.defs + self.vdefs

        #self.__dict__.update(**(args))
        self._set_vars(**kwargs)

    def _set_vars(self, **kwargs):
        """set attributes accordingly to kwargs"""
        for key, value in six.iteritems(kwargs):
            if not hasattr(self, key) or getattr(self, key) is None:
                setattr(self, key, value)

    def generate_params(self):
        """Generate binary data from the object"""

        if hasattr(self, 'prep') and callable(self.prep):
            self.prep()

        body = consts.EMPTY_STRING

        for field in self.params_order:
            #print field
            param = self.params[field]
            #print param
            if self.field_is_optional(field):
                if param.type is int:
                    value = self._generate_int_tlv(field)
                    if value:
                        body += value
                elif param.type is str:
                    value = self._generate_string_tlv(field)
                    if value:
                        body += value
                elif param.type is ostr:
                    value = self._generate_ostring_tlv(field)
                    if value:
                        body += value
            else:
                if param.type is int:
                    value = self._generate_int(field)
                    body += value
                elif param.type is str:
                    value = self._generate_string(field)
                    body += value
                elif param.type is ostr:
                    value = self._generate_ostring(field)
                    if value:
                        body += value
            #print value
        return body

    def _generate_opt_header(self, field):
        """Generate a header for an optional parameter"""

        raise NotImplementedError('Vendors not supported')

    def _generate_int(self, field):
        """Generate integer value"""

        fmt = self._pack_format(field)
        data = getattr(self, field)
        if data:
            return struct.pack(fmt, data)
        else:
            return consts.NULL_STRING

    def _generate_string(self, field):
        """Generate string value"""

        field_value = getattr(self, field)

        if hasattr(self.params[field], 'size'):
            size = self.params[field].size
            value = field_value.ljust(size, chr(0))
        elif hasattr(self.params[field], 'max'):
            if len(field_value or '') > self.params[field].max:
                field_value = field_value[0:self.params[field].max - 1]

            if field_value:
                value = field_value + chr(0)
            else:
                value = chr(0)

        setattr(self, field, field_value)
        return six.b(value)

    def _generate_ostring(self, field):
        """Generate octet string value (no null terminator)"""

        value = getattr(self, field)
        if value:
            return value
        else:
            return None  # chr(0)

    def _generate_int_tlv(self, field):
        """Generate integer value"""
        fmt = self._pack_format(field)
        data = getattr(self, field)
        field_code = get_optional_code(field)
        field_length = self.params[field].size
        value = None
        if data:
            value = struct.pack(">HH" + fmt, field_code, field_length, data)
            #print binascii.b2a_hex(value)
        return value

    def _generate_string_tlv(self, field):
        """Generate string value"""

        field_value = getattr(self, field)
        field_code = get_optional_code(field)

        if hasattr(self.params[field], 'size'):
            size = self.params[field].size
            fvalue = field_value.ljust(size, chr(0))
            value = struct.pack(">HH", field_code, size) + fvalue
        elif hasattr(self.params[field], 'max'):
            if len(field_value or '') > self.params[field].max:
                field_value = field_value[0:self.params[field].max - 1]

            if field_value:
                field_length = len(field_value)
                fvalue = field_value + chr(0)
                value = struct.pack(">HH", field_code, field_length) + fvalue
                #print binascii.b2a_hex(value)
            else:
                value = None  # chr(0)
        #setattr(self, field, field_value)
        return value

    def _generate_ostring_tlv(self, field):
        """Generate octet string value (no null terminator)"""
        try:
            field_value = getattr(self, field)
        except:
            return None
        field_code = get_optional_code(field)

        value = None
        if field_value:
            field_length = len(field_value)
            value = struct.pack(">HH", field_code, field_length) + field_value
            #print binascii.b2a_hex(value)
        return value

    def _pack_format(self, field):
        """Return format type"""

        if self.params[field].size == 1:
            return 'B'
        elif self.params[field].size == 2:
            return 'H'
        elif self.params[field].size == 3:
            return 'L'
        return None

    def _parse_int(self, field, data, pos):
        """Parse fixed-length chunk from a PDU.
        Return (data, pos) tuple."""

        size = self.params[field].size
        field_value = getattr(self, field)
        unpacked_data = self._unpack(self._pack_format(field),
            data[pos:pos + size])
        field_value = ''.join(map(str, unpacked_data))
        setattr(self, field, field_value)
        pos += size

        return data, pos

    def _parse_string(self, field, data, pos):
        """Parse variable-length string from a PDU.
        Return (data, pos) tuple."""

        end = data.find(consts.NULL_STRING, pos)
        length = end - pos

        field_value = data[pos:pos + length]
        setattr(self, field, field_value)
        pos += length + 1

        return data, pos

    def _parse_ostring(self, field, data, pos, length=None):
        """Parse an octet string from a PDU.
        Return (data, pos) tuple."""

        if length is None:
            length_field = self.params[field].len_field
            length = int(getattr(self, length_field))
            #print length_field, type(length_field), length, type(length_field)

        setattr(self, field, data[pos:pos + length])
        pos += length

        return data, pos

    def is_fixed(self, field):
        """Return True if field has fixed length, False otherwise"""

        if hasattr(self.params[field], 'size'):
            return True
        return False

    def parse_params(self, data):
        """Parse data into the object structure"""

        pos = 0
        dlen = len(data)

        for field in self.params_order:
            param = self.params[field]
            if pos == dlen or self.field_is_optional(field):
                break

            if param.type is int:
                data, pos = self._parse_int(field, data, pos)
            elif param.type is str:
                data, pos = self._parse_string(field, data, pos)
            elif param.type is ostr:
                data, pos = self._parse_ostring(field, data, pos)
        #print pos,field,data
        if pos < dlen:
            #None
            self.parse_optional_params(data[pos:])

    def parse_optional_params(self, data):
        """Parse optional parameters.

        Optional parameters have the following format:
            * type (2 bytes)
            * length (2 bytes)
            * value (variable, <length> bytes)
        """
        dlen = len(data)
        pos = 0

        while pos < dlen:
            type_code, pos = unpack_short(data, pos)
            field = get_optional_name(type_code)
            length, pos = unpack_short(data, pos)

            param = self.params[field]
            if param.type is int:
                data, pos = self._parse_int(field, data, pos)
            elif param.type in (str, ostr):
                data, pos = self._parse_ostring(field, data, pos, length)

    def field_exists(self, field):
        """Return True if field exists, False otherwise"""
        return hasattr(self.params, field)

    def field_is_optional(self, field):
        """Return True if field is optional, False otherwise"""

        if field in consts.OPTIONAL_PARAMS:
            return True
        elif self.is_vendor():
            # FIXME: No vendor support yet
            return False

        return False


class Param(object):
    """Command parameter info class"""

    def __init__(self, **kwargs):
        """Initialize"""

        if 'type' not in kwargs:
            raise KeyError('Parameter Type not defined')

        if kwargs.get('type') not in (int, str, ostr, flag):
            raise ValueError("Invalid parameter type: %s"
                % kwargs.get('type'))

        valid_keys = ('type', 'size', 'min', 'max', 'len_field')
        for k in kwargs:
            if k not in valid_keys:
                raise KeyError("Key '%s' not allowed here" % k)

        self.type = kwargs.get('type')

        for param in ('size', 'min', 'max', 'len_field'):
            if param in kwargs:
                setattr(self, param, kwargs[param])

    def __repr__(self):
        """Shows type of Param in console"""
        return ''.join(('<Param of ', str(self.type), '>'))


class BindTransmitter(Command):
    """Bind as a transmitter command"""

    params = {
        'system_id': Param(type=str, max=16),
        'password': Param(type=str, max=9),
        'system_type': Param(type=str, max=13),
        'interface_version': Param(type=int, size=1),
        'addr_ton': Param(type=int, size=1),
        'addr_npi': Param(type=int, size=1),
        'address_range': Param(type=str, max=41),
    }

    # Order is important, but params dictionary is unordered
    params_order = ('system_id', 'password', 'system_type',
        'interface_version', 'addr_ton', 'addr_npi', 'address_range')

    def __init__(self, command, **kwargs):
        """Initialize"""

        super(BindTransmitter, self).__init__(command, need_sequence=False,
            **kwargs)

        self._set_vars(**(dict.fromkeys(self.params)))
        self.interface_version = consts.SMPP_VERSION_34


class BindReceiver(BindTransmitter):
    """Bind as a receiver command"""
    def __init__(self, command, **kwargs):
        """Initialize"""
        super(BindReceiver, self).__init__(command, **kwargs)


class BindTransceiver(BindTransmitter):
    """Bind as reciever and transmitter command"""
    def __init__(self, command, **kwargs):
        """Initialize"""
        super(BindTransceiver, self).__init__(command, **kwargs)


class BindTransmitterResp(Command):
    """Response for bind as a transmitter command"""

    params = {
        'system_id': Param(type=str),
        'sc_interface_version': Param(type=int, size=1),
    }

    params_order = ('system_id', 'sc_interface_version')

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(BindTransmitterResp, self).__init__(command, need_sequence=False,
                                                                    **kwargs)

        self._set_vars(**(dict.fromkeys(self.params)))


class BindReceiverResp(BindTransmitterResp):
    """Response for bind as a reciever command"""
    def __init__(self, command, **kwargs):
        """Initialize"""
        super(BindReceiverResp, self).__init__(command, **kwargs)


class BindTransceiverResp(BindTransmitterResp):
    """Response for bind as a transceiver command"""
    def __init__(self, command, **kwargs):
        """Initialize"""
        super(BindTransceiverResp, self).__init__(command, **kwargs)


class DataSM(Command):
    """data_sm command is used to transfer data between SMSC and the ESME"""

    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'registered_delivery': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),

        # Optional params:
        'source_port': Param(type=int, size=2),
        'source_addr_subunit': Param(type=int, size=1),
        'source_network_type': Param(type=int, size=1),
        'source_bearer_type': Param(type=int, size=1),
        'source_telematics_id': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'dest_addr_subunit': Param(type=int, size=1),
        'dest_network_type': Param(type=int, size=1),
        'dest_bearer_type': Param(type=int, size=1),
        'dest_telematics_id': Param(type=int, size=2),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'more_messages_to_send': Param(type=int, size=1),
        'qos_time_to_live': Param(type=int, size=4),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'receipted_message_id': Param(type=str, max=65),
        'message_state': Param(type=int, size=1),
        'network_error_code': Param(type=ostr, size=3),
        'user_message_reference': Param(type=int, size=2),
        'privacy_indicator': Param(type=int, size=1),
        'callback_num': Param(type=str, min=4, max=19),
        'callback_num_pres_ind': Param(type=int, size=1),
        'callback_num_atag': Param(type=str, max=65),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'user_response_code': Param(type=int, size=1),
        'display_time': Param(type=int, size=1),
        'sms_signal': Param(type=int, size=2),
        'ms_validity': Param(type=int, size=1),
        'ms_msg_wait_facilities': Param(type=int, size=1),
        'number_of_messages': Param(type=int, size=1),
        'alert_on_msg_delivery': Param(type=flag),
        'language_indicator': Param(type=int, size=1),
        'its_reply_type': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2)
    }

    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi', 'destination_addr',
        'esm_class', 'registered_delivery', 'data_coding'

        # Optional params:
        'source_port', 'source_addr_subunit', 'source_network_type',
        'source_bearer_type', 'source_telematics_id', 'destination_port',
        'dest_addr_subunit', 'dest_network_type', 'dest_bearer_type',
        'dest_telematics_id', 'sar_msg_ref_num', 'sar_total_segments',
        'sar_segment_seqnum', 'more_messages_to_send', 'qos_time_to_live',
        'payload_type', 'message_payload', 'receipted_message_id',
        'message_state', 'network_error_code', 'user_message_reference',
        'privacy_indicator', 'callback_num', 'callback_num_pres_ind',
        'callback_num_atag', 'source_subaddress', 'dest_subaddress',
        'user_response_code', 'display_time', 'sms_signal',
        'ms_validity', 'ms_msg_wait_facilities', 'number_of_messages',
        'alert_on_message_delivery', 'language_indicator', 'its_reply_type',
        'its_session_info')

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(DataSM, self).__init__(command, **kwargs)
        self._set_vars(**(dict.fromkeys(self.params)))


class DataSMResp(Command):
    """Reponse command for data_sm"""

    message_id = None
    delivery_failure_reason = None
    network_error_code = None
    additional_status_info_text = None
    dpf_result = None

    def __init__(self, command, **kwargs):
        """Initialize"""

        super(DataSMResp, self).__init__(command, **kwargs)


class GenericNAck(Command):
    """General Negative Acknowledgement class"""

    _defs = []

    def __init__(self, command, **kwargs):
        """Initialize"""

        super(GenericNAck, self).__init__(command, need_sequence=False,
            **kwargs)


class SubmitSM(Command):
    """submit_sm command class

    This command is used by an ESME to submit short message to the SMSC.
    submit_sm PDU does not support the transaction mode."""

    #
    # Service type
    # The following generic service types are defined:
    #   '' -- default
    #   'CMT' -- Cellural Messaging
    #   'CPT' -- Cellural Paging
    #   'VMN' -- Voice Mail Notification
    #   'VMA' -- Voice Mail Alerting
    #   'WAP' -- Wireless Application Protocol
    #   'USSD' -- Unstructured Supplementary Services Data
    service_type = None

    # Type of Number for source address
    source_addr_ton = None

    # Numbering Plan Indicator for source address
    source_addr_npi = None

    # Address of SME which originated this message
    source_addr = None

    # TON for destination
    dest_addr_ton = None

    # NPI for destination
    dest_addr_npi = None

    # Destination address for this message
    destination_addr = None

    # Message mode and message type
    esm_class = None  # SMPP_MSGMODE_DEFAULT

    # Protocol Identifier
    protocol_id = None

    # Priority level of this message
    priority_flag = None

    # Message is to be scheduled by the SMSC for delivery
    schedule_delivery_time = None

    # Validity period of this message
    validity_period = None

    # Indicator to signify if an SMSC delivery receipt or and SME
    # acknowledgement is required.
    registered_delivery = None

    # This flag indicates if submitted message should replace an existing
    # message
    replace_if_present_flag = None

    # Encoding scheme of the short messaege data
    data_coding = None  # SMPP_ENCODING_DEFAULT#ISO10646

     # Indicates the short message to send from a list of predefined
    # ('canned') short messages stored on the SMSC
    sm_default_msg_id = None

    # Message length in octets
    sm_length = 0

    # Up to 254 octets of short message user data
    short_message = None

    # Optional are taken from params list and are set dynamically when
    # __init__ is called.
    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'protocol_id': Param(type=int, size=1),
        'priority_flag': Param(type=int, size=1),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'replace_if_present_flag': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=ostr, max=254,
                               len_field='sm_length'),
        # Optional params
        'user_message_reference': Param(type=int, size=2),
        'source_port': Param(type=int, size=2),
        'source_addr_subunit': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'dest_addr_subunit': Param(type=int, size=1),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'more_messages_to_send': Param(type=int, size=1),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'privacy_indicator': Param(type=int, size=1),
        'callback_num': Param(type=str, min=4, max=19),
        'callback_num_pres_ind': Param(type=int, size=1),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'user_response_code': Param(type=int, size=1),
        'display_time': Param(type=int, size=1),
        'sms_signal': Param(type=int, size=2),
        'ms_validity': Param(type=int, size=1),
        'ms_msg_wait_facilities': Param(type=int, size=1),
        'number_of_messages': Param(type=int, size=1),
        'alert_on_message_delivery': Param(type=flag),
        'language_indicator': Param(type=int, size=1),
        'its_reply_type': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2),
        'ussd_service_op': Param(type=int, size=1),
    }

    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi',
        'destination_addr', 'esm_class', 'protocol_id', 'priority_flag',
        'schedule_delivery_time', 'validity_period', 'registered_delivery',
        'replace_if_present_flag', 'data_coding', 'sm_default_msg_id',
        'sm_length', 'short_message',

        # Optional params
        'user_message_reference', 'source_port', 'source_addr_subunit',
        'destination_port', 'dest_addr_subunit', 'sar_msg_ref_num',
        'sar_total_segments', 'sar_segment_seqnum', 'more_messages_to_send',
        'payload_type', 'message_payload', 'privacy_indicator',
        'callback_num', 'callback_num_pres_ind', 'source_subaddress',
        'dest_subaddress', 'user_response_code', 'display_time',
        'sms_signal', 'ms_validity', 'ms_msg_wait_facilities',
        'number_of_messages', 'alert_on_message_delivery',
        'language_indicator', 'its_reply_type', 'its_session_info',
        'ussd_service_op')

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(SubmitSM, self).__init__(command, **kwargs)
        self._set_vars(**(dict.fromkeys(self.params)))

    def prep(self):
        """Prepare to generate binary data"""

        if self.short_message:
            self.sm_length = len(self.short_message)
            if hasattr(self, 'message_payload'):
                delattr(self, 'message_payload')
        else:
            self.sm_length = 0


class SubmitSMResp(Command):
    """Response command for submit_sm"""

    params = {
        'message_id': Param(type=str, max=65)
    }

    params_order = ('message_id',)

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(SubmitSMResp, self).__init__(command, need_sequence=False,
                                                                    **kwargs)
        self._set_vars(**(dict.fromkeys(self.params)))


class DeliverSM(SubmitSM):
    """deliver_sm command class, similar to submit_sm
    but has different optional params"""

    params = {
        'service_type': Param(type=str, max=6),
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'dest_addr_ton': Param(type=int, size=1),
        'dest_addr_npi': Param(type=int, size=1),
        'destination_addr': Param(type=str, max=21),
        'esm_class': Param(type=int, size=1),
        'protocol_id': Param(type=int, size=1),
        'priority_flag': Param(type=int, size=1),
        'schedule_delivery_time': Param(type=str, max=17),
        'validity_period': Param(type=str, max=17),
        'registered_delivery': Param(type=int, size=1),
        'replace_if_present_flag': Param(type=int, size=1),
        'data_coding': Param(type=int, size=1),
        'sm_default_msg_id': Param(type=int, size=1),
        'sm_length': Param(type=int, size=1),
        'short_message': Param(type=ostr, max=254,
                               len_field='sm_length'),

        # Optional params
        'user_message_reference': Param(type=int, size=2),
        'source_port': Param(type=int, size=2),
        'destination_port': Param(type=int, size=2),
        'sar_msg_ref_num': Param(type=int, size=2),
        'sar_total_segments': Param(type=int, size=1),
        'sar_segment_seqnum': Param(type=int, size=1),
        'user_response_code': Param(type=int, size=1),
        'privacy_indicator': Param(type=int, size=1),
        'payload_type': Param(type=int, size=1),
        'message_payload': Param(type=ostr, max=260),
        'callback_num': Param(type=str, min=4, max=19),
        'source_subaddress': Param(type=str, min=2, max=23),
        'dest_subaddress': Param(type=str, min=2, max=23),
        'language_indicator': Param(type=int, size=1),
        'its_session_info': Param(type=int, size=2),
        'network_error_code': Param(type=ostr, size=3),
        'message_state': Param(type=int, size=1),
        'receipted_message_id': Param(type=str, max=65),
        }

    params_order = ('service_type', 'source_addr_ton', 'source_addr_npi',
        'source_addr', 'dest_addr_ton', 'dest_addr_npi',
        'destination_addr', 'esm_class', 'protocol_id', 'priority_flag',
        'schedule_delivery_time', 'validity_period', 'registered_delivery',
        'replace_if_present_flag', 'data_coding', 'sm_default_msg_id',
        'sm_length', 'short_message',

        # Optional params
        'user_message_reference', 'source_port', 'destination_port',
        'sar_msg_ref_num', 'sar_total_segments', 'sar_segment_seqnum',
        'user_response_code', 'privacy_indicator',
        'payload_type', 'message_payload',
        'callback_num', 'source_subaddress',
        'dest_subaddress', 'language_indicator', 'its_session_info',
        'network_error_code', 'message_state', 'receipted_message_id')

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(DeliverSM, self).__init__(command, need_sequence=False, **kwargs)
        self._set_vars(**(dict.fromkeys(self.params)))


class DeliverSMResp(SubmitSMResp):
    """deliver_sm_response response class, same as submit_sm"""
    message_id = None

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(DeliverSMResp, self).__init__(command, **kwargs)


class Unbind(Command):
    """Unbind command"""

    params = {}
    params_order = ()

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(Unbind, self).__init__(command, need_sequence=False, **kwargs)


class UnbindResp(Command):
    """Unbind response command"""

    params = {}
    params_order = ()

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(UnbindResp, self).__init__(command, need_sequence=False,
            **kwargs)


class EnquireLink(Command):
    """Enquire link command"""
    params = {}
    params_order = ()

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(EnquireLink, self).__init__(command, need_sequence=False,
            **kwargs)


class EnquireLinkResp(Command):
    """Enquire link command response"""
    params = {}
    params_order = ()

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(EnquireLinkResp, self).__init__(command, need_sequence=False,
            **kwargs)

class AlertNotification(Command):
    """alert_notification command class
    """


    # Type of Number for source address
    source_addr_ton = None

    # Numbering Plan Indicator for source address
    source_addr_npi = None

    # Address of SME which originated this message
    source_addr = None

    # TON for destination
    esme_addr_ton = None

    # NPI for destination
    esme_addr_npi = None

    # Destination address for this message
    esme_addr = None

    # Optional are taken from params list and are set dynamically when
    # __init__ is called.
    params = {
        'source_addr_ton': Param(type=int, size=1),
        'source_addr_npi': Param(type=int, size=1),
        'source_addr': Param(type=str, max=21),
        'esme_addr_ton': Param(type=int, size=1),
        'esme_addr_npi': Param(type=int, size=1),
        'esme_addr': Param(type=str, max=21),

        # Optional params
        'ms_availability_status' : Param(type=int, size=1),
    }

    params_order = ('source_addr_ton', 'source_addr_npi',
        'source_addr', 'esme_addr_ton', 'esme_addr_npi',
        'esme_addr',

        # Optional params
        'ms_availability_status')

    def __init__(self, command, **kwargs):
        """Initialize"""
        super(AlertNotification, self).__init__(command, **kwargs)
        self._set_vars(**(dict.fromkeys(self.params)))
