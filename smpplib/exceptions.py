#
# Exceptions
#

class UnknownCommandError(Exception):
    """Raised when unknown command ID is received"""

class ConnectionError(Exception):
    """Connection error"""

class PDUError(RuntimeError):
    """Error processing PDU"""

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
