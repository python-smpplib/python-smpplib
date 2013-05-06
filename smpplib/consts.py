SEVENBIT_SIZE = 160
EIGHTBIT_SIZE = 140
UCS2_SIZE = 70
SEVENBIT_MP_SIZE = SEVENBIT_SIZE - 7
EIGHTBIT_MP_SIZE = EIGHTBIT_SIZE - 6
UCS2_MP_SIZE = UCS2_SIZE - 3

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
DESCRIPTIONS = {
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
    SMPP_ESME_RINVSYSID: 'Invalid System ID',
    SMPP_ESME_RCANCELFAIL: 'Cancel SM Failed',
    SMPP_ESME_RREPLACEFAIL: 'Replace SM Failed',
    SMPP_ESME_RMSGQFUL: 'Message Queue is full',
    SMPP_ESME_RINVSERTYP: 'Invalid Service Type',
    SMPP_ESME_RINVNUMDESTS: 'Invalid number of destinations',
    SMPP_ESME_RINVDLNAME: 'Invalid Distribution List name',
    SMPP_ESME_RINVDESTFLAG: 'Invalid Destination Flag (submit_multi)',
    SMPP_ESME_RINVSUBREP: 'Invalid Submit With Replace request '
                        '(replace_if_present_flag set)',
    SMPP_ESME_RINVESMCLASS: 'Invalid esm_class field data',
    SMPP_ESME_RCNTSUBDL: 'Cannot submit to Distribution List',
    SMPP_ESME_RSUBMITFAIL: 'submit_sm or submit_multi failed',
    SMPP_ESME_RINVSRCTON: 'Invalid Source address TON',
    SMPP_ESME_RINVSRCNPI: 'Invalid Source address NPI',
    SMPP_ESME_RINVDSTTON: 'Invalid Destination address TON',
    SMPP_ESME_RINVDSTNPI: 'Invalid Destination address NPI',
    SMPP_ESME_RINVSYSTYP: 'Invalid system_type field',
    SMPP_ESME_RINVREPFLAG: 'Invalid replace_if_present flag',
    SMPP_ESME_RINVNUMMSGS: 'Invalid number of messages',
    SMPP_ESME_RTHROTTLED: 'Throttling error (ESME has exceeded allowed '
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

SMPP_CLIENT_STATE_CLOSED = 0
SMPP_CLIENT_STATE_OPEN = 1
SMPP_CLIENT_STATE_BOUND_TX = 2
SMPP_CLIENT_STATE_BOUND_RX = 3
SMPP_CLIENT_STATE_BOUND_TRX = 4

#
# TON (Type Of Number) values
#
SMPP_TON_UNK = 0x00
SMPP_TON_INTL = 0x01
SMPP_TON_NATNL = 0x02
SMPP_TON_NWSPEC = 0x03
SMPP_TON_SBSCR = 0x04
SMPP_TON_ALNUM = 0x05
SMPP_TON_ABBREV = 0x06


#
# NPI (Numbering Plan Indicator) values
#
SMPP_NPI_UNK = 0x00  # Unknown
SMPP_NPI_ISDN = 0x01  # ISDN (E163/E164)
SMPP_NPI_DATA = 0x03  # Data (X.121)
SMPP_NPI_TELEX = 0x04  # Telex (F.69)
SMPP_NPI_LNDMBL = 0x06  # Land Mobile (E.212)
SMPP_NPI_NATNL = 0x08  # National
SMPP_NPI_PRVT = 0x09  # Private
SMPP_NPI_ERMES = 0x0A  # ERMES
SMPP_NPI_IP = 0x0E  # IPv4
SMPP_NPI_WAP = 0x12  # WAP


#
# Encoding Types
#
SMPP_ENCODING_DEFAULT = 0x00  # SMSC Default
SMPP_ENCODING_IA5 = 0x01  # IA5 (CCITT T.50)/ASCII (ANSI X3.4)
SMPP_ENCODING_BINARY = 0x02  # Octet unspecified (8-bit binary)
SMPP_ENCODING_ISO88591 = 0x03  # Latin 1 (ISO-8859-1)
SMPP_ENCODING_BINARY2 = 0x04  # Octet unspecified (8-bit binary)
SMPP_ENCODING_JIS = 0x05  # JIS (X 0208-1990)
SMPP_ENCODING_ISO88595 = 0x06  # Cyrillic (ISO-8859-5)
SMPP_ENCODING_ISO88598 = 0x07  # Latin/Hebrew (ISO-8859-8)
SMPP_ENCODING_ISO10646 = 0x08  # UCS2 (ISO/IEC-10646)
SMPP_ENCODING_PICTOGRAM = 0x09  # Pictogram Encoding
SMPP_ENCODING_ISO2022JP = 0x0A  # ISO-2022-JP (Music Codes)
SMPP_ENCODING_EXTJIS = 0x0D  # Extended Kanji JIS (X 0212-1990)
SMPP_ENCODING_KSC5601 = 0x0E  # KS C 5601


#
# Language Types
#
SMPP_LANG_DEFAULT = 0x00
SMPP_LANG_EN = 0x01
SMPP_LANG_FR = 0x02
SMPP_LANG_ES = 0x03
SMPP_LANG_DE = 0x04


#
# ESM class values
#
SMPP_MSGMODE_DEFAULT = 0x00  # Default SMSC mode (e.g. Store and Forward)
SMPP_MSGMODE_DATAGRAM = 0x01  # Datagram mode
SMPP_MSGMODE_FORWARD = 0x02  # Forward (i.e. Transaction) mode
SMPP_MSGMODE_STOREFORWARD = 0x03  # Store and Forward mode (use this to
                                  # select Store and Forward mode if Default
                                  # mode is not Store and Forward)


SMPP_MSGTYPE_DEFAULT = 0x00  # Default message type (i.e. normal message)
SMPP_MSGTYPE_DELIVERYACK = 0x08  # Message containts ESME Delivery
                                 # Acknowledgement
SMPP_MSGTYPE_USERACK = 0x10  # Message containts ESME Manual/User
                             # Acknowledgement

SMPP_GSMFEAT_NONE = 0x00  # No specific features selected
SMPP_GSMFEAT_UDHI = 0x40  # UDHI Indicator (only relevant for MT msgs)
SMPP_GSMFEAT_REPLYPATH = 0x80  # Set Reply Path (only relevant for GSM net)
SMPP_GSMFEAT_UDHIREPLYPATH = 0xC0  # Set UDHI and Reply Path (for GSM net)

#
# SMPP Protocol ID
#
SMPP_PID_DEFAULT = 0x00  # Default
SMPP_PID_RIP = 0x41  # Replace if present on handset

#
# SMPP User Data Header Information Element Identifier
#
SMPP_UDHIEIE_CONCATENATED = 0x00  # Concatenated short message, 8-bit ref
SMPP_UDHIEIE_SPECIAL = 0x01
SMPP_UDHIEIE_RESERVED = 0x02
SMPP_UDHIEIE_PORT8 = 0x04
SMPP_UDHIEIE_PORT16 = 0x04

#
# SMPP protocol versions
#
SMPP_VERSION_33 = 0x33
SMPP_VERSION_34 = 0x34

COMMAND_STATES = {
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

STATE_SETTERS = {
    'bind_transmitter_resp': SMPP_CLIENT_STATE_BOUND_TX,
    'bind_receiver_resp': SMPP_CLIENT_STATE_BOUND_RX,
    'bind_transceiver_resp': SMPP_CLIENT_STATE_BOUND_TRX,
    'unbind_resp': SMPP_CLIENT_STATE_OPEN
}

OPTIONAL_PARAMS = {
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
    'sc_interface_version': 0x0210,  # 0x1002,
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
