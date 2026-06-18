#!/usr/bin/python3
# $Revision: 61905 $ !! do not change or remove this line !!
# -*- coding: utf-8 -*-


# module 'six' for portability Python2 and Python3
from __future__ import unicode_literals
import six
from ctypes import *
import os, platform, numbers, sys, inspect, ctypes
from enum import Enum


def create_BabyLIN():
    """ """

    # @six.python_2_unicode_compatible
    class _BabyLIN(type):
        """A custom metaclass that adds the following functionality:
           It reads the BabyLIN-library, and tries to find the names of the
           contained functions (works with BabyLIN.dll as well).
           If found, it saves the names in the dictionary _libNames."
           The classmethods in class BabyLIN will use this dictionary as lookup
           table.
        """

        # everything happend relative to the directory of this file
        BABYLIN_DLL_WRAPPER_DIRECTORY = property(lambda self:
                                           os.path.join(
                                             os.path.abspath(
                                               os.path.dirname(__file__))))
        @classmethod
        def _getSharedObjectDirectory(cls):
            """Return the location of the BabyLIN shared object to be loaded
               by Python via ctypes.

            :rtype: string
            :return: directory of BabyLIN.dll/libBabyLIN.so
            """
            d = cls.BABYLIN_DLL_WRAPPER_DIRECTORY.__get__(cls)

            # man koennte auch 'dpkg --print-architecture' benutzen:
            # 32-bit: Ausgabe: armhf
            # 64-bit: arm64

            if platform.uname()[0].lower().startswith("linux"):
                if platform.uname()[4].lower().startswith("armv7"):
                    # linux based system on raspberry pi
                    if platform.architecture()[0] == '32bit':
                        return os.path.join(d, 'BabyLIN library',
                                                    'Linux_RaspberryPi',
                                                        'BabyLIN-Lib-32')

                elif platform.uname()[4].lower().startswith("aarch64"):
                    if platform.architecture()[0] == '64bit':
                        return os.path.join(d, 'BabyLIN library',
                                                    'Linux_RaspberryPi',
                                                        'BabyLIN-Lib-64')
                    elif platform.architecture()[0] == '32bit':
                        return os.path.join(d, 'BabyLIN library',
                                                    'Linux_RaspberryPi',
                                                        'BabyLIN-Lib-32')
                else:
                    # generic linux system
                    if platform.architecture()[0] == '32bit':
                        return os.path.join(d, 'BabyLIN library',
                                                    'Linux_PC',
                                                        'BabyLIN-Lib-32')
                    elif platform.architecture()[0] == '64bit':
                        return os.path.join(d, 'BabyLIN library',
                                                    'Linux_PC',
                                                        'BabyLIN-Lib-64')

            elif platform.uname()[0].lower().startswith(("win", "microsoft")):

                if platform.architecture()[0].lower().startswith('32bit'):
                    return os.path.join(d, 'BabyLIN library',
                                                'Windows_PC',
                                                    'BabyLIN-DLL x86')

                elif platform.architecture()[0].lower().startswith('64bit'):
                    return os.path.join(d, 'BabyLIN library',
                                                'Windows_PC',
                                                    'BabyLIN-DLL x64')

        BABYLIN_DLL_DIRECTORY           = property(lambda self:
                                            self._getSharedObjectDirectory())
        BABYLIN_DLL_PATH_NAME           = property(lambda self:
            os.path.join(
                self._getSharedObjectDirectory(),
                    'libBabyLIN.so' \
                        if platform.uname()[0].lower().startswith("linux") \
                            else 'BabyLIN.dll'))

        BL_OK                               = property(lambda self:        0)
        BL_PC_SIDE_ERRORS                   = property(lambda self:  -100000)
        BL_RESOURCE_ERROR                   = property(lambda self:  -100001)
        BL_HANDLE_INVALID                   = property(lambda self:  -100002)
        BL_NO_CONNECTION                    = property(lambda self:  -100003)
        BL_SERIAL_PORT_ERROR                = property(lambda self:  -100004)
        BL_CMD_SYNTAX_ERROR                 = property(lambda self:  -100005)
        BL_NO_ANSWER                        = property(lambda self:  -100006)
        BL_FILE_ERROR                       = property(lambda self:  -100007)
        BL_WRONG_PARAMETER                  = property(lambda self:  -100008)
        BL_NO_DATA                          = property(lambda self:  -100009)
        BL_NO_SDF                           = property(lambda self:  -100010)
        BL_DP_MSG_ERROR                     = property(lambda self:  -100011)
        BL_SIGNAL_NOT_EXISTENT              = property(lambda self:  -100012)
        BL_SIGNAL_IS_SCALAR                 = property(lambda self:  -100013)
        BL_SIGNAL_IS_ARRAY                  = property(lambda self:  -100014)
        BL_SDF_INSUFFICIENT_FIRMWARE        = property(lambda self:  -100015)
        BL_ENCODING_NOT_EXISTENT            = property(lambda self:  -100016)
        BL_BUFFER_TOO_SMALL                 = property(lambda self:  -100017)
        BL_NO_ANSWER_DATA                   = property(lambda self:  -100018)
        BL_ANSWER_DATA_NOT_EXISTENT         = property(lambda self:  -100019)
        BL_NO_CHANNELS_AVAILABLE            = property(lambda self:  -100020)
        BL_UNKNOWN_COMMAND                  = property(lambda self:  -100021)
        BL_TIMEOUT                          = property(lambda self:  -100022)
        BL_DOWNLOAD_IN_PROGRESS             = property(lambda self:  -100026)
        BL_NOT_RESOLVABLE_ENTRY000          = property(lambda self:  -100100)
        BL_NOT_RESOLVABLE_ENTRY100          = property(lambda self:  -100200)

        BL_ANSWER_TYPE_INT                  = property(lambda self:        0)
        BL_ANSWER_TYPE_STR                  = property(lambda self:        1)
        BL_ANSWER_TYPE_BIN                  = property(lambda self:        2)
        BL_ANSWER_TYPE_INT64                = property(lambda self:        3)
        BL_ANSWER_TYPE_FLOAT                = property(lambda self:        4)
        BL_ANSWER_TYPE_UNKNOWN              = property(lambda self:        5)

        SDF_OK                              = property(lambda self:        0)
        SDF_HANDLE_INVALID                  = property(lambda self:  -100024)
        SDF_IN_USE                          = property(lambda self:  -100025)

        BL_MACRO_FINISHED                   = property(lambda self:        0)
        BL_MACRO_STILL_RUNNING              = property(lambda self:      150)
        BL_MACRO_SAME_RUNNING               = property(lambda self:      151)
        BL_MACRO_OTHER_RUNNING              = property(lambda self:      152)
        BL_MACRO_START_FAIL                 = property(lambda self:      153)
        BL_MACRO_NEVER_EXECUTED             = property(lambda self:      154)
        BL_MACRO_ERRCODE_IN_RESULT          = property(lambda self:      155)
        BL_MACRO_EXCEPTIONCODE_IN_RESULT    = property(lambda self:      156)

        BLC_UA_INVALID_PARAMETER            = property(lambda self:  -100096)
        BLC_UA_NO_GETTER_DEFINED            = property(lambda self:  -100097)
        BLC_UA_NO_SETTER_DEFINED            = property(lambda self:  -100098)
        BLC_UA_SET_VALUE_REJECTED           = property(lambda self:  -100099)
        BLC_UA_NOT_RESOLVABLE_TAG_FIRST     = property(lambda self:  -100100)
        BLC_UA_NOT_RESOLVABLE_TAG_MAX       = property(lambda self:  -100200)

        @classmethod
        def _rev(cls):
            """ """
            with open(os.path.join(
                        cls.BABYLIN_DLL_WRAPPER_DIRECTORY.__get__(cls),
                            __file__)) as f:
                for line in f.readlines():
                    if line.find('Revision') != -1:
                        return line.split()[2]

            return ""

        BABYLIN_DLL_MAJOR             = property(lambda self:           2)
        BABYLIN_DLL_MINOR             = property(lambda self:           6)
        BABYLIN_DLL_BUILD             = property(lambda self:           3)
        BABYLIN_DLL_REV               = property(lambda self: self._rev())

        # this is actually not quite true. it's the platform of the
        # python interpreter, but because python32 only loads 32-bit shared
        # libs and python64 only loads 64-bit shared libs, it should be ok.
        BABYLIN_DLL_ARCH              = property(lambda self:
                                            platform.architecture()[0])

        BABYLIN_DLL_WRAPPER_VERSION   = property(lambda self:
            "BabyLIN-DLL Python Wrapper v{0}.{1}.{2}"\
                .format(_BabyLIN.BABYLIN_DLL_MAJOR.__get__(self),
                        _BabyLIN.BABYLIN_DLL_MINOR.__get__(self),
                        _BabyLIN.BABYLIN_DLL_BUILD.__get__(self)))

        WIN32_CHECK_FAILURE             = property(lambda self:     -2)
        LINUX_CHECK_FAILURE             = property(lambda self:     -3)
        UNSUPPORTED_PLATFORM_FAILURE    = property(lambda self:     -4)
        UNSUPPORTED_ARCH_FAILURE        = property(lambda self:     -5)
        PYTHON_CHECK_FAILURE            = property(lambda self:     -6)

        # some commands sent via BLC_sendCommand return a proper value, which
        # should not be interpreted as error code, but as result value
        COMMANDS_RETURNING_VALUES       = property(lambda self:
                                            ['hwtype',\
                                             'status',\
                                             'readspeed',\
                                             'version',\
                                             'persistent_rd',\
                                             'hwstate',\
                                             'macro_result',\
                                             'getnodesimu'])

        @classmethod
        def _findNames(cls, names):
            """Find BabyLIN function names in shared object.

            The shared object contains function names, which are needed for
            calling into the shared object via ctypes.

            :type cls: class _BabyLIN
            :param cls: class instance of _BabyLIN

            :type names: list of strings
            :param names: list of BabyLIN names

            :rtype: dictionary.
            :return: dictionary with BabyLIN fucntion names as keys, values
                     are the in the shared object contained function names
            """
            libNames = {}

            if platform.uname()[0].lower().startswith("linux"):
                for name in names:
                    libNames[name] = name
            elif platform.uname()[0].lower().startswith(("win", "microsoft")):
                if platform.architecture()[0].lower().startswith('64bit'):
                    for name in names:
                        libNames[name] = name
                elif platform.architecture()[0].lower().startswith('32bit'):
                    libNames = {
                        'BLC_Reset'                                : 'BLC_Reset',
                        'BLC_SDF_getFrameNr'                       : 'BLC_SDF_getFrameNr',
                        'BLC_SDF_getMacroNr'                       : 'BLC_SDF_getMacroNr',
                        'BLC_SDF_getNodeNr'                        : 'BLC_SDF_getNodeNr',
                        'BLC_SDF_getNumSchedules'                  : 'BLC_SDF_getNumSchedules',
                        'BLC_SDF_getScheduleName'                  : 'BLC_SDF_getScheduleName',
                        'BLC_SDF_getScheduleNr'                    : 'BLC_SDF_getScheduleNr',
                        'BLC_SDF_getSignalNr'                      : 'BLC_SDF_getSignalNr',
                        'BLC_close'                                : 'BLC_close',
                        'BLC_closeAll'                             : 'BLC_closeAll',
                        'BLC_convertUrl'                           : 'BLC_convertUrl',
                        'BLC_dmDelay'                              : 'BLC_dmDelay',
                        'BLC_dmPrepare'                            : 'BLC_dmPrepare',
                        'BLC_dmPulse'                              : 'BLC_dmPulse',
                        'BLC_dmRead'                               : 'BLC_dmRead',
                        'BLC_dmReadTimeout'                        : 'BLC_dmReadTimeout',
                        'BLC_dmReportConfig'                       : 'BLC_dmReportConfig',
                        'BLC_dmStart'                              : 'BLC_dmStart',
                        'BLC_dmStop'                               : 'BLC_dmStop',
                        'BLC_dmWrite'                              : 'BLC_dmWrite',
                        'BLC_downloadSDF'                          : 'BLC_downloadSDF',
                        'BLC_encodeSignal'                         : 'BLC_encodeSignal',
                        'BLC_flush'                                : 'BLC_flush',
                        'BLC_getAnswerByIndex'                     : 'BLC_getAnswerByIndex',
                        'BLC_getAnswerByName'                      : 'BLC_getAnswerByName',
                        'BLC_getAnswerNameByIndex'                 : 'BLC_getAnswerNameByIndex',
                        'BLC_getAnswerTypeByIndex'                 : 'BLC_getAnswerTypeByIndex',
                        'BLC_getAnswerTypeByName'                  : 'BLC_getAnswerTypeByName',
                        'BLC_getBabyLinPorts'                      : 'BLC_getBabyLinPorts',
                        'BLC_getBabyLinPortsTimout'                : 'BLC_getBabyLinPortsTimout',
                        'BLC_getChannelCount'                      : 'BLC_getChannelCount',
                        'BLC_getChannelHandle'                     : 'BLC_getChannelHandle',
                        'BLC_getChannelInfo'                       : 'BLC_getChannelInfo',
                        'BLC_getChannelSectionDescription'         : 'BLC_getChannelSectionDescription',
                        'BLC_getDTLRequestStatus'                  : 'BLC_getDTLRequestStatus',
                        'BLC_getDTLResponseStatus'                 : 'BLC_getDTLResponseStatus',
                        'BLC_getErrorString'                       : 'BLC_getErrorString',
                        'BLC_getExtendedVersion'                   : 'BLC_getExtendedVersion',
                        'BLC_getFrameCount'                        : 'BLC_getFrameCount',
                        'BLC_getFrameDetails'                      : 'BLC_getFrameDetails',
                        'BLC_getFrameIdForFrameNr'                 : 'BLC_getFrameIdForFrameNr',
                        'BLC_getFrameName'                         : 'BLC_getFrameName',
                        'BLC_getFrameNrForFrameId'                 : 'BLC_getFrameNrForFrameId',
                        'BLC_getHWType'                            : 'BLC_getHWType',
                        'BLC_getLastError'                         : 'BLC_getLastError',
                        'BLC_getDetailedErrorString'               : 'BLC_getDetailedErrorString',
                        'BLC_getLastFrame'                         : 'BLC_getLastFrame',
                        'BLC_getNextBusError'                      : 'BLC_getNextBusError',
                        'BLC_getNextDTLRequest'                    : 'BLC_getNextDTLRequest',
                        'BLC_getNextDTLResponse'                   : 'BLC_getNextDTLResponse',
                        'BLC_getNextFrame'                         : 'BLC_getNextFrame',
                        'BLC_getNextJumboFrame'                    : 'BLC_getNextJumboFrame',
                        'BLC_getNextFrameTimeout'                  : 'BLC_getNextFrameTimeout',
                        'BLC_getNextJumboFrameTimeout'             : 'BLC_getNextJumboFrameTimeout',
                        'BLC_getNextFrames'                        : 'BLC_getNextFrames',
                        'BLC_getNextJumboFrames'                   : 'BLC_getNextJumboFrames',
                        'BLC_getNextFramesTimeout'                 : 'BLC_getNextFramesTimeout',
                        'BLC_getNextJumboFramesTimeout'            : 'BLC_getNextJumboFramesTimeout',
                        'BLC_getNextSignal'                        : 'BLC_getNextSignal',
                        'BLC_getNextSignals'                       : 'BLC_getNextSignals',
                        'BLC_getNextSignalsForNumber'              : 'BLC_getNextSignalsForNumber',
                        'BLC_getNodeCount'                         : 'BLC_getNodeCount',
                        'BLC_getNodeForSignal'                     : 'BLC_getNodeForSignal',
                        'BLC_getNodeName'                          : 'BLC_getNodeName',
                        'BLC_getMacroResultString'                 : 'BLC_getMacroResultString',
                        'BLC_varRead'                              : 'BLC_varRead',
                        'BLC_varWrite'                             : 'BLC_varWrite',
                        'BLC_AdHoc_DefaultProtocol'                : 'BLC_AdHoc_DefaultProtocol',
                        'BLC_AdHoc_DefaultService'                 : 'BLC_AdHoc_DefaultService',
                        'BLC_AdHoc_DefaultExecute'                 : 'BLC_AdHoc_DefaultExecute',
                        'BLC_getRawSlaveResponse'                  : 'BLC_getRawSlaveResponse',
                        'BLC_getSDFInfo'                           : 'BLC_getSDFInfo',
                        'BLC_getSectionInfo'                       : 'BLC_getSectionInfo',
                        'BLC_getSignalArray'                       : 'BLC_getSignalArray',
                        'BLC_getSignalArrayByName'                 : 'BLC_getSignalArrayByName',
                        'BLC_getSignalArrayWithTimestamp'          : 'BLC_getSignalArrayWithTimestamp',
                        'BLC_getSignalCount'                       : 'BLC_getSignalCount',
                        'BLC_getSignalInFrame'                     : 'BLC_getSignalInFrame',
                        'BLC_getSignalName'                        : 'BLC_getSignalName',
                        'BLC_getSignalSize'                        : 'BLC_getSignalSize',
                        'BLC_getSignalValue'                       : 'BLC_getSignalValue',
                        'BLC_getSignalValueByName'                 : 'BLC_getSignalValueByName',
                        'BLC_getSignalValueWithTimestamp'          : 'BLC_getSignalValueWithTimestamp',
                        'BLC_getSignalsInFrame'                    : 'BLC_getSignalsInFrame',
                        'BLC_getSignalsInFrameCount'               : 'BLC_getSignalsInFrameCount',
                        'BLC_getTargetID'                          : 'BLC_getTargetID',
                        'BLC_getVersion'                           : 'BLC_getVersion',
                        'BLC_getVersionString'                     : 'BLC_getVersionString',
                        'BLC_getWrapperVersion'                    : 'BLC_getWrapperVersion',
                        'BLC_isSignalArray'                        : 'BLC_isSignalArray',
                        'BLC_isSignalEmulated'                     : 'BLC_isSignalEmulated',
                        'BLC_lastAnswerHasData'                    : 'BLC_lastAnswerHasData',
                        'BLC_loadLDF'                              : 'BLC_loadLDF',
                        'BLC_loadSDF'                              : 'BLC_loadSDF',
                        'BLC_macro_result'                         : 'BLC_macro_result',
                        'BLC_mon_set'                              : 'BLC_mon_set',
                        'BLC_mon_set_xmit'                         : 'BLC_mon_set_xmit',
                        'BLC_mon_xmit'                             : 'BLC_mon_xmit',
                        'BLC_open'                                 : 'BLC_open',
                        'BLC_openNet'                              : 'BLC_openNet',
                        'BLC_openPort'                             : 'BLC_openPort',
                        'BLC_openUSB'                              : 'BLC_openUSB',
                        'BLC_registerDTLRequestCallback'           : 'BLC_registerDTLRequestCallback',
                        'BLC_registerDTLResponseCallback'          : 'BLC_registerDTLResponseCallback',
                        'BLC_registerDebugCallback'                : 'BLC_registerDebugCallback',
                        'BLC_registerErrorCallback'                : 'BLC_registerErrorCallback',
                        'BLC_registerEventCallback'                : 'BLC_registerEventCallback',
                        'BLC_registerFrameCallback'                : 'BLC_registerFrameCallback',
                        'BLC_registerJumboFrameCallback'           : 'BLC_registerJumboFrameCallback',
                        'BLC_registerMacroStateCallback'           : 'BLC_registerMacroStateCallback',
                        'BLC_registerSignalCallback'               : 'BLC_registerSignalCallback',
                        'BLC_registerUserDataDTLRequestCallback'   : 'BLC_registerUserDataDTLRequestCallback',
                        'BLC_registerUserDataDTLResponseCallback'  : 'BLC_registerUserDataDTLResponseCallback',
                        'BLC_registerUserDataDebugCallback'        : 'BLC_registerUserDataDebugCallback',
                        'BLC_registerUserDataErrorCallback'        : 'BLC_registerUserDataErrorCallback',
                        'BLC_registerUserDataEvent'                : 'BLC_registerUserDataEvent',
                        'BLC_registerUserDataEventCallback'        : 'BLC_registerUserDataEventCallback',
                        'BLC_registerUserDataFrameCallback'        : 'BLC_registerUserDataFrameCallback',
                        'BLC_registerUserDataJumboFrameCallback'   : 'BLC_registerUserDataJumboFrameCallback',
                        'BLC_registerUserDataMacroStateCallback'   : 'BLC_registerUserDataMacroStateCallback',
                        'BLC_registerUserDataSignalCallback'       : 'BLC_registerUserDataSignalCallback',
                        'BLC_sendCommand'                          : 'BLC_sendCommand',
                        'BLC_decodeSignal'                         : 'BLC_decodeSignal',
                        'BLC_sendDTLRequest'                       : 'BLC_sendDTLRequest',
                        'BLC_sendDTLResponse'                      : 'BLC_sendDTLResponse',
                        'BLC_sendRaw'                              : 'BLC_sendRaw',
                        'BLC_sendRawMasterRequest'                 : 'BLC_sendRawMasterRequest',
                        'BLC_sendRawSlaveResponse'                 : 'BLC_sendRawSlaveResponse',
                        'BLC_setDTLMode'                           : 'BLC_setDTLMode',
                        'BLC_setsig'                               : 'BLC_setsig',
                        'BLC_updRawSlaveResponse'                  : 'BLC_updRawSlaveResponse',
                        'SDF_close'                                : 'SDF_close',
                        'SDF_downloadSectionToChannel'             : 'SDF_downloadSectionToChannel',
                        'SDF_downloadToDevice'                     : 'SDF_downloadToDevice',
                        'SDF_getSectionCount'                      : 'SDF_getSectionCount',
                        'SDF_getSectionHandle'                     : 'SDF_getSectionHandle',
                        'SDF_getSectionInfo'                       : 'SDF_getSectionInfo',
                        'SDF_open'                                 : 'SDF_open',
                        'SDF_openLDF'                              : 'SDF_openLDF',
                        'BLC_createHandle'                         : 'BLC_createHandle',
                        'BLC_destroy'                              : 'BLC_destroy',
                        'BLC_releaseHandle'                        : 'BLC_releaseHandle',
                        'BLC_discover'                             : 'BLC_discover',
                        'BLC_getSignedNumber'                      : 'BLC_getSignedNumber',
                        'BLC_getUnsignedNumber'                    : 'BLC_getUnsignedNumber',
                        'BLC_getBinary'                            : 'BLC_getBinary',
                        'BLC_setSignedNumber'                      : 'BLC_setSignedNumber',
                        'BLC_setUnsignedNumber'                    : 'BLC_setUnsignedNumber',
                        'BLC_setBinary'                            : 'BLC_setBinary',
                        'BLC_execute'                              : 'BLC_execute',
                        'BLC_execute_async'                        : 'BLC_execute_async',
                        'BLC_setCallback'                          : 'BLC_setCallback'}

            return libNames


        def __new__(cls, name, bases, attrs):
            """Set attributes of client class BabyLIN_library.

            :type name: string
            :param name: name of client class, i.e. BabyLIN_library

            :type bases: types of base classes
            :param bases: list of base classes

            :type attrs: dictionary
            :param attrs: dictionary of BabyLIN_library's attributes
            """
            names = []
            # first we read the classmethods of BabyLIN_library starting with BLC_.
            # These are the names we are looking for in the shared object
            # (BabyLIN.dll or libBabyLIN.so)
            for k,v in attrs.items():
                if isinstance(v, classmethod) and \
                    (k.startswith('BLC_') or k.startswith('SDF_')):
                    names.append(k)

            # set the attribute _libNames in BabyLIN_library
            attrs['_libNames'] = _BabyLIN._findNames(names)
            return super(_BabyLIN, cls).__new__(cls, name, bases, attrs)



    @six.add_metaclass(_BabyLIN)
    class BabyLIN(object):

        # when registering callbacks, keep a reference to them so that
        # python does not remove them from memory, which would have bad
        # effects inside the BabyLIN-dll.
        _frame_callback        = dict()
        _signal_callback       = dict()
        _macro_state_callback  = dict()
        _jumbo_frame_callback  = dict()
        _event_callback        = dict()
        _error_callback        = dict()
        _debug_callback        = dict()
        _dtl_response_callback = dict()
        _dtl_request_callback  = dict()

        _frame_cb_user         = None
        _signal_cb_user        = None
        _macrostate_cb_user    = None
        _jumboframe_cb_user    = None
        _event_cb_user         = None
        _error_cb_user         = None
        _debug_cb_user         = None
        _dtl_response_cb_user  = None
        _dtl_request_cb_user   = None

        _libNames = {}

        @six.python_2_unicode_compatible
        class BabyLINException(Exception):
            """ """
            def __init__(self, code, msg):
                """Initialize a BabyLINException.

                :type self: BabyLINException
                :param self: instance of BabyLINException

                :type code: integer
                :param code: returned integer value of underlying BabyLIN
                             function called by ctypes.
                :type msg: string
                :param msg: optional additional error message
                """
                self.code = code
                self.msg = msg
                self.caller = inspect.stack()[1][3]

            def __str__(self):
                return "{} exit code {} {}".format(
                    self.caller, self.code, self.msg)
        
        class BLC_ADHOC_PROTOCOL_TYPE(Enum):
            TYPE_RAW = 0
            TYPE_DTL_ISOTP = 1
            TYPE_ISOTP_WITHOUT_NAD = 2
            TYPE_WEBASTO_UHW2 = 3
            TYPE_WEBASTO_STD = 5
            TYPE_KLINE_RAW = 6

        class BLC_ADHOC_PROTOCOL(ctypes.Structure):
            class ADHOC_PROTOCOL_FLAGS(ctypes.Union):
                class ADHOC_PROTOCOL_FLAGS_GENERIC(ctypes.Structure):
                    _fields_ = [
                        ("protocoltype", ctypes.c_uint, 6),
                        ("unused_1", ctypes.c_uint, 5),
                        ("tx_shortensf", ctypes.c_uint, 1),
                        ("tx_shortenlcf", ctypes.c_uint, 1),
                        ("unused_2", ctypes.c_uint, 3),
                        ("use_std_posresp", ctypes.c_uint, 1),
                        ("use_std_negresp", ctypes.c_uint, 1),
                        ("slaveprotocol", ctypes.c_uint, 1),
                        ("expect_shortenedsf", ctypes.c_uint, 2),
                        ("expect_shortenedlcf", ctypes.c_uint, 2),
                        ("unused_3", ctypes.c_uint, 5),
                        ("accept_any_csize", ctypes.c_uint, 1),
                        ("xmit_shortenflowctrl", ctypes.c_uint, 1)
                    ]

                class ADHOC_PROTOCOL_FLAGS_LIN(ctypes.Structure):
                    _fields_ = [
                        ("protocoltype", ctypes.c_uint, 6),
                        ("unused_1", ctypes.c_uint, 2),
                        ("xmit_chksumtype", ctypes.c_uint, 1),
                        ("expect_chksumtype", ctypes.c_uint, 2),
                        ("xmit_shortensf", ctypes.c_uint, 1),
                        ("xmit_shortenlcf", ctypes.c_uint, 1),
                        ("unused_2", ctypes.c_uint, 3),
                        ("use_std_posresp", ctypes.c_uint, 1),
                        ("use_std_negresp", ctypes.c_uint, 1),
                        ("slaveprotocol", ctypes.c_uint, 1),
                        ("expect_shortenedsf", ctypes.c_uint, 2),
                        ("expect_shortenedlcf", ctypes.c_uint, 2),
                        ("unused_3", ctypes.c_uint, 5),
                        ("accept_any_csize", ctypes.c_uint, 1),
                        ("xmit_shortenflowctrl", ctypes.c_uint, 1)
                    ]
                class ADHOC_PROTOCOL_FLAGS_CAN(ctypes.Structure):
                    _fields_ = [
                        ("protocoltype", ctypes.c_uint, 6),
                        ("xmit_canfd_switch", ctypes.c_uint, 1),
                        ("xmit_canfd_frame", ctypes.c_uint, 1),
                        ("xmit_can_11_29bit", ctypes.c_uint, 1),
                        ("expect_can_11_29bit", ctypes.c_uint, 2),
                        ("xmit_shortensf", ctypes.c_uint, 1),
                        ("xmit_shortenlcf", ctypes.c_uint, 1),
                        ("unused_1", ctypes.c_uint, 3),
                        ("use_std_posresp", ctypes.c_uint, 1),
                        ("use_std_negresp", ctypes.c_uint, 1),
                        ("slaveprotocol", ctypes.c_uint, 1),
                        ("expect_shortenedsf", ctypes.c_uint, 2),
                        ("expect_shortenedlcf", ctypes.c_uint, 2),
                        ("expect_canfd_switch", ctypes.c_uint, 2),
                        ("expect_canfd_frame", ctypes.c_uint, 2),
                        ("xmit_no_flowctrl_wait", ctypes.c_uint, 1),
                        ("accept_any_csize", ctypes.c_uint, 1),
                        ("xmit_shortenflowctrl", ctypes.c_uint, 1)]
                _fields_ = [
                    ("generic", ADHOC_PROTOCOL_FLAGS_GENERIC),
                    ("lin", ADHOC_PROTOCOL_FLAGS_LIN),
                    ("can", ADHOC_PROTOCOL_FLAGS_CAN)
                ]

            _fields_ = [
                ("name", ctypes.c_char_p),
                ("flags", ADHOC_PROTOCOL_FLAGS),
                ("active", ctypes.c_ubyte),
                ("req_slot_time", ctypes.c_int),
                ("rsp_slot_time", ctypes.c_int),
                ("rsp_delay", ctypes.c_int),
                ("fill_byte", ctypes.c_ubyte)
            ]

        
        class BLC_ADHOC_SERVICE(ctypes.Structure):
            class ADHOC_SERVICE_FLAGS(ctypes.Union):
                class ADHOC_SERVICE_FLAGS_GENERIC(ctypes.Structure):
                    _fields_ = [
                        ("unused_1", ctypes.c_uint, 2),
                        ("unused_2", ctypes.c_uint, 2),
                        ("shortensf_txd", ctypes.c_uint, 2),
                        ("shortensf_rcv", ctypes.c_uint, 2),
                        ("shortenlcf_txd", ctypes.c_uint, 2),
                        ("shortenlcf_rcv", ctypes.c_uint, 2),
                        ("unused_3", ctypes.c_uint, 8),
                        ("use_std_posresp", ctypes.c_uint, 2),
                        ("use_std_negresp", ctypes.c_uint, 2),
                        ("requestonly", ctypes.c_uint, 1),
                        ("unused_4", ctypes.c_uint, 2),
                        ("accept_any_csize", ctypes.c_uint, 2),
                        ("unused_5", ctypes.c_uint, 3)
                    ]

                class ADHOC_SERVICE_FLAGS_LIN(ctypes.Structure):
                    _fields_ = [
                        ("checksum_txd", ctypes.c_uint, 2),
                        ("checksum_rcv", ctypes.c_uint, 2),
                        ("shortensf_txd", ctypes.c_uint, 2),
                        ("shortensf_rcv", ctypes.c_uint, 2),
                        ("shortenlcf_txd", ctypes.c_uint, 2),
                        ("shortenlcf_rcv", ctypes.c_uint, 2),
                        ("unused_1", ctypes.c_uint, 8),
                        ("use_std_posresp", ctypes.c_uint, 2),
                        ("use_std_negresp", ctypes.c_uint, 2),
                        ("requestonly", ctypes.c_uint, 1),
                        ("unused_2", ctypes.c_uint, 2),
                        ("accept_any_csize", ctypes.c_uint, 2),
                        ("unused_3", ctypes.c_uint, 3)
                    ]

                class ADHOC_SERVICE_FLAGS_CAN(ctypes.Structure):
                    _fields_ = [
                        ("id_11_29_txd", ctypes.c_uint, 2),
                        ("id_11_29_rcv", ctypes.c_uint, 2),
                        ("shortensf_txd", ctypes.c_uint, 2),
                        ("shortensf_rcv", ctypes.c_uint, 2),
                        ("shortenlcf_txd", ctypes.c_uint, 2),
                        ("shortenlcf_rcv", ctypes.c_uint, 2),
                        ("fdbaudswitch_txd", ctypes.c_uint, 2),
                        ("fdbaudswitch_rcv", ctypes.c_uint, 2),
                        ("fdframe_txd", ctypes.c_uint, 2),
                        ("fdframe_rcv", ctypes.c_uint, 2),
                        ("use_std_posresp", ctypes.c_uint, 2),
                        ("use_std_negresp", ctypes.c_uint, 2),
                        ("requestonly", ctypes.c_uint, 1),
                        ("no_flowctrl_wait", ctypes.c_uint, 2),
                        ("accept_any_csize", ctypes.c_uint, 2),
                        ("unused_1", ctypes.c_uint, 3)
                    ]
                _fields_ = [
                    ("generic", ADHOC_SERVICE_FLAGS_GENERIC),
                    ("lin", ADHOC_SERVICE_FLAGS_LIN),
                    ("can", ADHOC_SERVICE_FLAGS_CAN)
                ]
            _fields_ = [
                ("name", ctypes.c_char_p),
                ("flags", ADHOC_SERVICE_FLAGS),
                ("req_frame_id", ctypes.c_int),
                ("req_container_size", ctypes.c_longlong),
                ("req_payload_size", ctypes.c_longlong),
                ("req_slot_time", ctypes.c_int),
                ("rsp_frame_id", ctypes.c_int),
                ("rsp_container_size", ctypes.c_longlong),
                ("rsp_payload_size", ctypes.c_longlong),
                ("rsp_slot_time", ctypes.c_int),
                ("rsp_delay", ctypes.c_int)
            ]

        class BLC_ADHOC_EXECUTE(ctypes.Structure):
            _fields_ = [
                ("nad", ctypes.c_int),
                ("p2_extended", ctypes.c_int),
                ("flow_control_st_min", ctypes.c_int),
                ("flow_control_block_size", ctypes.c_int)
            ]

        # @six.python_2_unicode_compatible
        class BLC_PORTINFO(ctypes.Structure):
            _fields_ = [("portNr",                  c_int),
                        ("type",                    c_int),
                        ("name",                    c_char * 256),
                        ("device",                  c_char * 256)]

            def __str__(self):
                return \
                    "name={} port={} type={} port={}"\
                        .format(self.name.decode('utf-8'), self.portNr,
                                self.type, self.device.decode('utf-8'))


        # @six.python_2_unicode_compatible
        class BLC_TARGETID(Structure):
            _fields_ = [("type",                    c_ushort),
                        ("version",                 c_ushort),
                        ("build",                   c_ushort),
                        ("flags",                   c_ushort),
                        ("serial",                  c_long),
                        ("heapsize",                c_long),
                        ("numofchannels",           c_long),
                        ("name",                    c_char * 128)]

            def __str__(self):
                s =  "type={} version={} build={} flags={} serial={} "
                s += "heapsize={} numofchannels={} name={}"
                return s.format(self.type, self.version, self.build,
                                self.flags, self.serial, self.heapsize,
                                self.numofchannels, self.name.decode('utf-8'))


        # @six.python_2_unicode_compatible
        class BLC_CHANNELINFO(Structure):
            _fields_ = [("id",                      c_ushort),
                        ("type",                    c_ushort),
                        ("name",                    c_char * 128),
                        ("maxbaudrate",             c_long),
                        ("reserved1",               c_long),
                        ("reserved2",               c_long),
                        ("reserved3",               c_long),
                        ("associatedWithSectionNr", c_int)]

            def __str__(self):
                s =  "id={} type={} name={} maxbaudrate={} reserved1={} "
                s += "reserved2={} reserved3={} associatedWithSectionNr={}"
                return s.format(self.id, self.type, self.name.decode('utf-8'),
                                self.maxbaudrate, self.reserved1,
                                self.reserved2, self.reserved3,
                                self.associatedWithSectionNr)


        # @six.python_2_unicode_compatible
        class BLC_SDFINFO(Structure):
            _fields_ = [("filename",                c_char * 256),
                        ("sectionCount",            c_short),
                        ("version_major",          c_short),
                        ("version_minor",           c_short)]

            def __str__(self):
                s =  "filename={} sectionCount={} version_major={} "
                s += "version_minor"
                return s.format(self.filename.decode('utf-8'),
                                self.sectionCount, self.version_major,
                                self.version_major)


        # @six.python_2_unicode_compatible
        class BLC_SECTIONINFO(Structure):
            _fields_ = [("name",                    c_char * 128),
                        ("type",                    c_int),
                        ("nr",                      c_short)]

            def __str__(self):
                s =  "name={} type={} nr={}"
                return s.format(self.name.decode('utf-8'), self.type, self.nr)


        # @six.python_2_unicode_compatible
        class BLC_FRAME(Structure):
            _fields_ = [("chId",                    c_ulong),
                        ("timestamp",               c_ulong),
                        ("intime",                  c_long),
                        ("frameId",                 c_ulong),
                        ("lenOfData",               c_ubyte),
                        ("frameData",               c_ubyte * 8),
                        ("frameFlags",              c_short),
                        ("busFlags",                c_short),
                        ("checksum",                c_ubyte)]

            def __str__(self):
                fData = ["0x{:02x}".format(d) for d in
                            self.frameData[:self.lenOfData]]
                for d in range(self.lenOfData, 8):
                    fData.append("0x**")

                s =  "chId={} timestamp={} intime={} frameId={} "
                s += "lenOfData={} frameData={} frameFlags={} "
                s += "busFlags={} checksum={}"
                return s.format(self.chId, self.timestamp, self.intime,
                                self.frameId, self.lenOfData, fData,
                                hex(self.frameFlags), hex(self.busFlags),
                                hex(self.checksum))

            def __bool__(self):
                """ """
                return not (self.frameFlags & 0x08 == 0x08)

            def __eq__(self, other):
                """ Check for equivalence of two frames."""
                if self.frameId != other.frameId: return False
                if self.lenOfData != other.lenOfData: return False
                if self.busFlags != other.busFlags: return False
                if self.frameFlags != other.frameFlags: return False
                if [hex(d) for d in self.frameData[:self.lenOfData]] != \
                   [hex(d) for d in other.frameData[:other.lenOfData]]:
                       return False
                return True


        # @six.python_2_unicode_compatible
        class BLC_JUMBO_FRAME(ctypes.Structure):
            _fields_ = [("chId",                    c_ulong),
                        ("timestamp",               c_ulong),
                        ("intime",                  c_long),
                        ("frameId",                 c_ulong),
                        ("lenOfData",               c_int),
                        ("frameData",               c_ubyte * 1024),
                        ("frameFlags",              c_short),
                        ("busFlags",                c_short),
                        ("checksum",                c_ubyte)]

            def __str__(self):
                fData = [hex(d) for d in self.frameData[:self.lenOfData]] if \
                        self.lenOfData > 0 else []
                s =  "chId = {} timestamp={} intime={} frameId={} "
                s += "lenOfData={} frameData={} frameFlags={} "
                s += "busFlags={} checksum={}"
                return s.format(self.chId, self.timestamp, self.intime,
                                self.frameId, self.lenOfData, fData,
                                hex(self.frameFlags), hex(self.busFlags),
                                hex(self.checksum))

            def __bool__(self):
                """ """
                return not (self.frameFlags & 0x08 == 0x08)

            def __eq__(self, other):
                """ Check for equivalence of two frames."""
                if self.frameId != other.frameId: return False
                if self.lenOfData != other.lenOfData: return False
                if self.busFlags != other.busFlags: return False
                if self.frameFlags != other.frameFlags: return False
                if [hex(d) for d in self.frameData[:self.lenOfData]] != \
                   [hex(d) for d in other.frameData[:other.lenOfData]]:
                       return False
                return True


        # @six.python_2_unicode_compatible
        class BLC_MACRO_STATE(Structure):
            _fields_ = [("channelid",               c_int),
                        ("macronr",                 c_int),
                        ("cmdnr",                   c_int),
                        ("state",                   c_int),
                        ("timestamp",               c_ulong)]

            def __str__(self):
                s =  "channelid={} macronr={} cmdnr={} state={} timestamp={}"
                return s.format(self.channelid, self.macronr, self.cmdnr,
                                self.state, self.timestamp)


        # @six.python_2_unicode_compatible
        class BLC_SIGNAL(Structure):
            _fields_ = [("index",                   c_int),
                        ("isArray",                 c_int),
                        ("value",                   c_ulonglong),
                        ("arrayLength",             c_int),
                        ("array",                   c_ubyte * 8),
                        ("timestamp",               c_ulong),
                        ("chId",                    c_ushort)]

            def __str__(self):
                array = [hex(d) for d in self.array[:self.arrayLength]] if \
                            self.arrayLength > 0 else []
                s =  "index={} isArray={} value={} arrayLength={} "
                s += "array={} timestamp={} chId={}"
                return s.format(self.index, self.isArray, self.value,
                                self.arrayLength, array, self.timestamp,
                                self.chId)


        # @six.python_2_unicode_compatible
        class BLC_ERROR(Structure):
            _fields_ = [("timestamp",               c_ulong),
                        ("type",                    c_ushort),
                        ("status",                  c_ushort)]

            def __str__(self):
                s = "timestamp={} type={} status={}"
                return s.format(self.timestamp, self.type, self.status)


        # @six.python_2_unicode_compatible
        class BLC_DTL(Structure):
            _fields_ = [("status",                  c_int),
                        ("nad",                     c_ubyte),
                        ("length",                  c_int),
                        ("data",                    c_ubyte * 4096)]

            def __str__(self):
                data = [hex(d) for d in self.data[:self.length]] if \
                        self.length > 0 else []
                s = "status={} nad={} length={} data={}"
                return s.format(self.status, self.nad, self.length, data)


        # @six.python_2_unicode_compatible
        class BLC_EVENT(Structure):
            _fields_ = [("timestamp",               c_uint),
                        ("pc_timestamp",            c_uint),
                        ("event",                   c_int),
                        ("data",                    c_longlong)]

            def __str__(self):
                s = "timestamp={} pc_timestamp={} event={} data={}"
                return s.format(self.timestamp, self.pc_timestamp,
                                self.event, self.data)


        # @six.python_2_unicode_compatible
        class SDF_SECTIONINFO(Structure):
            _fields_ = [("sectionNr",               c_int),
                        ("type",                    c_int),
                        ("name",                    c_char * 64),
                        ("description",             c_char * 4096)]

            def __str__(self):
                s = "sectionNr={} type={} name={} description={}"
                return s.format(self.sectionNr, self.type,
                                self.name.decode('utf-8'),
                                self.description.decode('utf-8'))


        @classmethod
        def _win_check(cls):
            """ """
            # python (32-bit) can only load 32-bit DLLs
            # python (64-bit) can only load 64-bit DLLs
            if not platform.uname()[0].lower().startswith(("win", "microso")):
                return False

            with open(cls.BABYLIN_DLL_PATH_NAME, 'rb') as f:
                # the DLL has definitely such a size. The version
                # information can be found at offset [128:134].
                data = f.read(134)
                if len(data) < 134:
                    raise cls.BabyLINException(cls.WIN32_CHECK_FAILURE,
                        "{}: invalid file size ({})".format(cls._library_name,
                                                            len(data)))
                if platform.architecture()[0] == '32bit':
                    # python is 32-Bit
                    if data[128:134] == b'\x50\x45\x00\x00\x64\x86':
                        # but the DLL is 64-Bit
                        raise cls.BabyLINException(cls.WIN32_CHECK_FAILURE,
                                        "Python(32-bit) can not load {}(64bit)"
                                            .format(cls._library_name))

                elif platform.architecture()[0] == '64bit':
                    # python is 64-Bit
                    if data[128:134] == b'\x50\x45\x00\x00\x4c\x01':
                        # but the DLL is 32-Bit
                        raise cls.BabyLINException(cls.WIN32_CHECK_FAILURE,
                                    "Python(64-bit) can not load {}(32bit)"
                                        .format(cls._library_name))

                else:
                    raise cls.BabyLINException(cls.UNSUPPORTED_ARCH_FAILURE,
                        "{}: unknown architecture {}"
                            .format(cls.BABYLIN_DLL_PATH_NAME,
                                platform.architecture()[0]))

            return True


        @classmethod
        def _linux_check(cls):
            """ """
            if not platform.uname()[0].lower().startswith("linux"):
                return False

            # TODO
            return True


        @classmethod
        def BLC_getWrapperVersion(cls):
            """ """
            return cls.BABYLIN_DLL_WRAPPER_VERSION


        @classmethod
        def config(cls):
            """ """

            # check python version
            if (six.PY2 and sys.version_info <= (2,6)) or \
               (six.PY3 and sys.version_info <= (3,4)):
                if six.PY3:
                    raise cls.BabyLINException(cls.PYTHON_CHECK_FAILURE,
                        "wrong Python version {}. At least 3.5 or above needed."
                            .format(sys.version_info))
                if six.PY2:
                    raise cls.BabyLINException(cls.PYTHON_CHECK_FAILURE,
                        "wrong Python version {}. At least 2.7 or above needed."
                            .format(sys.version_info))
            try:
                # load the shared object
                if cls._linux_check():
                    cls._lib_babylin = CDLL(cls.BABYLIN_DLL_PATH_NAME)

                elif cls._win_check():
                    cls._lib_babylin = ctypes.WinDLL(cls.BABYLIN_DLL_PATH_NAME)
                else:
                    raise cls.BabyLINException(cls.UNSUPPORTED_PLATFORM_FAILURE,
                        "Unsupported platform {}".format(platform.uname()))

            except cls.BabyLINException as e:
                six.print_(e)
                sys.exit(cls.UNSUPPORTED_PLATFORM_FAILURE)

            return cls


        # @six.python_2_unicode_compatible
        class ForeignFunctionParameterTypes(object):
            """ """
            def __init__(self, cls, restype, argtypes, lev=1):
                assert inspect.stack()[lev][3] in cls._libNames
                self.lib_func = \
                    getattr(cls._lib_babylin,
                            cls._libNames[inspect.stack()[lev][3]])
                self.lib_func.restype = restype
                self.lib_func.argtypes = argtypes

            def __enter__(self):
                return self.lib_func

            def __exit__(self, exc_type, exc_instance, traceback):
                return False
        #
        # Auxiliary
        #
        @staticmethod
        def _create_string_buffer(s):
            """ """
            if isinstance(s, six.text_type):
                s = s.encode('utf-8')
                # create_string_buffer from ctypes
            return create_string_buffer(s)


        #
        # Version
        #

        @classmethod
        def BLC_getVersion(cls):
            """This function retreives the version in the given parameter
               variables of the library.

               It returns the major/minor part of version number as integer tuple.

            :rtype: tuple
            :return: (major, minor)
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, None, [c_void_p, c_void_p]) as lib_func:
                    major, minor = c_int(-1), c_int(-1)
                    lib_func(byref(major), byref(minor))
                    return major.value, minor.value


        @classmethod
        def BLC_getExtendedVersion(cls):
            """This function retreives the version in the given parameter
               variables of the library.

               It returns the major/minor/patch/build part of version number
               as integer tuple.

            :rtype: tuple
            :return: (major, minor, build, patch)
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_void_p, c_void_p, c_void_p]) \
                        as lib_func:
                            major, minor = c_int(-1), c_int(-1)
                            patch, build = c_int(-1), c_int(-1)
                            lib_func(byref(major), byref(minor),
                                     byref(patch), byref(build))
                            return major.value, minor.value, \
                                   patch.value, build.value


        @classmethod
        def BLC_getVersionString(cls):
            """Get the version string of the library.

            :rtype: string
            :return: a string with the version information.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_char_p, []) as lib_func:
                    return lib_func().decode('utf-8')

        #
        # Open/Close
        #

        @classmethod
        def BLC_open(cls, port):
            """Open a connection to a BabyLIN USB-Serial device.

            This function tries to open the designated port and to start
            communication with the device.

            :type port: integer or string
            :param port: the BabyLIN is connected to. On Windows it uses
                         Windows-style numbering, which means it starts
                         with '1' for the first serial port. '0' is reserved.

                         On Linux systems, the port is represented by the path
                         to the device file (e.g. '/dev/ttyUSB0')

            :raise BabyLINException: if port cannot be opened

            :rtype: integer
            :return: connectionHandle to device.
            """
            assert isinstance(port, numbers.Integral) or \
                   isinstance(port, str) or isinstance(port, six.binary_type)
            arg_types, p = \
                ([c_int], c_int(port)) if isinstance(port, numbers.Integral) \
                else ([c_char_p], c_char_p(port.encode('utf-8')))
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, arg_types) as lib_func:
                    bh = lib_func(p)
                    if not bh:
                        raise cls.BabyLINException(-1, "")
                    return bh


        @classmethod
        def BLC_openNet(cls, ip, port):
            """
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_char_p, c_int]) as lib_func:
                    bh = lib_func(c_char_p(ip.encode('utf-8')),
                                  c_int(port))
                    if not bh:
                        raise cls.BabyLINException(-1, "")
                    return bh


        @classmethod
        def BLC_openPort(cls, portInfo):
            """Open a connection to a BabyLIN device using BLC_PORTINFO
               information.

            This function tries to open the BabyLIN device of the
            BLC_PORTINFO information, i.e. works as a wrapper for
            BLC_open and BLC_openNet which automatically decides which
            connection to establish.

            Platform independent way of connecting to BabyLIN-devices
            found by BLC_getBabyLinPorts or BLC_getBabyLinPortsTimout.

            :type portInfo: BLC_PORTINFO structure
            :param portInfo: the BLC_PORTINFO-structure of the BabyLIN to
                        connect to. (see BLC_getBabyLinPorts)

            :raise BabyLINException: if port cannot be opened

            :rtype: integer
            :return: a handle for the BabyLIN-connection.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [cls.BLC_PORTINFO]) as lib_func:
                    bh = lib_func(portInfo)
                    if not bh:
                        raise cls.BabyLINException(-1, six.text_type(portInfo))
                    return bh


        @classmethod
        def BLC_openUSB(cls, device):
            """Open a connection to a BabyLIN USB device.

               This function tries to open the designated port and to
               start communication with the device.

               Deprecated: use BLC_openPort() together with BLC_convertUrl().

               :type device: string
               :param device: the usb device string, the BabyLIN is connected to

               :raise BabyLINException: if device cannot be opened

               :rtype:
               :return: handle for the BabyLIN-connection
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_char_p]) as lib_func:
                    bh = lib_func(c_char_p(device.encode('utf-8')))
                    if not bh:
                        raise cls.BabyLINException(-1, device)
                    return bh


        @classmethod
        def BLC_convertUrl(cls, url):
            """Convert a device url to BLC_PORTINFO to use in BLC_openPort.

               This function tries to convert a given url to a complete
               struct of type BLC_PORTINFO.

               :type url: string
               :param url: the device url to convert might be a system
                           path (serial:///dev/ttyUSB1) for unix based systems,
                           a comport (serial://COM1) as is used for windows
                           or a network address (tcp://127.0.0.1:2048) to
                           connect to a network device.

               :raise BabyLINException: if url can not be converted

               :rtype: BLC_PORTINFO structure
               :return: portInfo BLC_PORTINFO instance.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_char_p, POINTER(cls.BLC_PORTINFO)]) as lib_func:
                    portInfo = cls.BLC_PORTINFO()
                    url_ = BabyLIN._create_string_buffer(url)
                    rv = lib_func(url_, byref(portInfo))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "error conv. " + url)
                    return portInfo


        @classmethod
        def BLC_close(cls, connectionHandle):
            """Close connection to device.

            :type connectionHandle: integer
            :param connectioinHandle: handle representing device connection

            :raise BabyLINException: if connection cannot be closed.

            :rtype: integer
            "return: 0 on success. Raises BabyLINException on error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(connectionHandle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_closeAll(cls):
            """Closes all open device connections.

            returns  -- On success 0. Raises BabyLINException on error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, []) as lib_func:
                    rv = lib_func()
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv

        #
        # Info
        #

        @classmethod
        def BLC_getBabyLinPorts(cls, max_devs):
            """Retrieve a list of ports a BabyLIN is connected to.

               The function doesn't try to connect to the found ports
               This function will not find any network-devices.

            max_devs -- maximal number of ports to scan for, must be > 0.
            returns  -- a list of found BabyLIN ports
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [POINTER(cls.BLC_PORTINFO), c_void_p]) \
                    as lib_func:
                        ports = (cls.BLC_PORTINFO * max_devs)()
                        found = c_int(max_devs)
                        rv = lib_func(byref(ports[0]), byref(found))
                        if rv < 0 or rv > max_devs:
                            raise cls.BabyLINException(rv, "")
                        return ports[:rv]


        @classmethod
        def BLC_getBabyLinPortsTimout(cls, max_devs,
                                      timeOutInMilliSeconds):
            """Retrieve a list of ports a BabyLIN is connected to.

               The function doesn't try to connect to the found ports.

               You can not connect to UDP network devices they are only listed
               FYI and have to be configured in SimpleMenu mode first.

               Network devices of type TCP will have the default port
               configured(2048) for connection. If the device's
               simplemenu-tcp-com-port configuration value was changed,
               you will have to change the BLC_PORTINFO.port prior to
               connecting via BLC_openPort(...).

            max_devs              -- maximal number of ports to scan for
            timeOutInMilliSeconds -- a timeout value in ms to wait for replies
                                     of network devices.
            returns               -- a list of found BabyLIN ports
                                     Raises a BabyLINException in case of error
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [POINTER(cls.BLC_PORTINFO), c_void_p, c_int]) \
                    as lib_func:
                        ports = (cls.BLC_PORTINFO * max_devs)()
                        found = c_int(max_devs)
                        rv = lib_func(byref(ports[0]),
                                      byref(found),
                                      c_int(timeOutInMilliSeconds))
                        if rv < 0 or rv > max_devs:
                            raise cls.BabyLINException(rv, "")
                        return ports[:rv]


        @classmethod
        def BLC_getChannelCount(cls, connectionHandle):
            """Get number of channels provided the BabyLIN device.

            connectionHandle -- Handle representing the connection
                                (see BLC_openPort/BLC_open)
            returns          -- number of channels.
                                Raises a BabyLINException in case of error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(connectionHandle))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_getChannelHandle(cls, connectionHandle, chId):
            """Retrieve a handle to the specified channel.

               This function returns a channel-handle for the specified
               channelId. A channel-handle is used to control a LIN- or CAN-BUS
               on the BabyLIN-device.

               Note: such a handle must not be closed like a connectionHandle
                     (returned by BLC_open/BLC_openPort).

               connectionHandle -- handle representing a device connection
                                   (see BLC_openPort/BLC_open)
               chId             -- identifier for the channel to get the
                                   handle for. Ranges from 0 to the number
                                   of channels supported by the device.
               returns          -- handle to the channel. None on error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_void_p, c_int]) as lib_func:
                    return lib_func(c_void_p(connectionHandle), c_int(chId))


        @classmethod
        def BLC_getChannelInfo(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_CHANNELINFO)]) \
                    as lib_func:
                        channelInfo = cls.BLC_CHANNELINFO()
                        rv = lib_func(c_void_p(handle), byref(channelInfo))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return channelInfo


        @classmethod
        def BLC_getChannelSectionDescription(cls, channelHandle):
            """Retrieve description string of a SDF-Section from a loaded SDF.

            channelHandle -- handle of the channel to get the sdf section
                             description of

            returns       -- the channel description as string
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_char_p, [c_void_p]) as lib_func:
                return lib_func(c_void_p(channelHandle)).decode('utf-8')


        @classmethod
        def BLC_getHWType(cls, handle):
            """Get the hardware type of BabyLIN device.

            Arguments:
            cls -- reference to surrounding class
            handle -- device handle (see BLC_openPort/BLC_open)
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                return lib_func(c_void_p(handle))


        @classmethod
        def BLC_getTargetID(cls, handle):
            """Get (target) information of BabyLIN device.

            Arguments:
            cls -- reference to surrounding class
            handle -- device handle (see BLC_openPort/BLC_open)

            Raises an exception of type BabyLIN.BabyLINException is case
            of error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_TARGETID)]) \
                    as lib_func:
                        targetID = cls.BLC_TARGETID()
                        rv = lib_func(c_void_p(handle), byref(targetID))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return targetID


        @classmethod
        def BLC_getSDFInfo(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_SDFINFO)]) \
                    as lib_func:
                        sdfInfo = cls.BLC_SDFINFO()
                        rv = lib_func(c_void_p(handle), byref(sdfInfo))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return sdfInfo


        @classmethod
        def BLC_getSectionInfo(cls, handle, infoAboutSectionNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, POINTER(cls.BLC_SECTIONINFO)]) \
                    as lib_func:
                        sectionInfo = cls.BLC_SECTIONINFO()
                        rv = lib_func(c_void_p(handle),
                                      c_int(infoAboutSectionNr),
                                      byref(sectionInfo))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return sectionInfo

        #
        # Loading
        #

        @classmethod
        def BLC_loadLDF(cls, handle, fname, mode):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(handle),
                                  c_char_p(fname.encode('utf-8')), c_int(mode))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_loadSDF(cls, connectionHandle, fname, mode):
            """Loads the specified SDF-file into library and optionally into
               the BabyLIN device.

               The SDF is generated by LINWorks/SessionConf from a LDF file.
               NOTE: this resets the device upon download.

               :type connectionHandle: integer
               :param connectionHandle: handle represeting the connection
                                        (see BLC_openPort/BLC_open)
               :type fname: string
               :param fname: filename of file to load

               :type mode: integer
               :param mode: boolean value, determines if the SDF profile gets
                            downloaded into the BabyLIN device (!=0) or only
                            used in the library (=0).

               :raise BabyLINException: if sdf file does not exist or can not
                                        be loaded

               :rtype: integer
               :return: Status of operation; '=0' means successful, '!=0' error.
            """
            if not os.path.exists(fname):
                raise cls.BabyLINException(-1,
                        "sdf-file {} does not exist".format(fname))
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(connectionHandle),
                                  c_char_p(fname.encode('utf-8')), c_int(mode))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_downloadSDF(cls, handle, mode):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                    return lib_func(c_void_p(handle), c_int(mode))


        @classmethod
        def BLC_Reset(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    return lib_func(c_void_p(handle))


        @classmethod
        def BLC_flush(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    return lib_func(c_void_p(handle))


        #
        # Commands
        #

        @classmethod
        def BLC_sendCommand(cls, handle, cmd):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    if isinstance(cmd, six.binary_type):
                        cmd = cmd.decode('utf-8')
                    cmd_ = BabyLIN._create_string_buffer(cmd)
                    rv = lib_func(c_void_p(handle), cmd_)

                    # if cmd is returning proper values, do not raise an ex.
                    if [c for c in cls.COMMANDS_RETURNING_VALUES if c in cmd]:
                        return rv

                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "'%s'" % cmd)
                    return rv
        #
        # callbacks
        #

        @classmethod
        def _registerCallback(cls, handle, cb, cb_t, name):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, cb_t], lev=2) \
                    as lib_func:
                        # generate a unique key for the callback
                        key = '%x%s' % (handle, name)
                        if not cb:
                            # NOTE: workaround for deregistering a callback
                            # we have to set argtypes to nothing, otherwise
                            # ctypes will throw an exception or even crash
                            lib_func.argtypes = [c_void_p, c_void_p]
                            attr = getattr(cls, name, None)
                            if attr is not None and key in attr:
                                # remove the callback from memory
                                del attr[key]
                            return lib_func(c_void_p(handle), c_void_p(cb))

                        # 'attr' is a dictionary. it will store a reference
                        # of the callback under the generated 'key' so that
                        # python does not remove it from memory.
                        attr = getattr(cls, name, None)
                        if attr is not None:
                            attr[key] = cb_t(cb)
                            return lib_func(c_void_p(handle), attr[key])

        @classmethod
        def _registerCallbackUser(cls, handle, cb, cb_t, userdata, name):
            """ """
            # TODO
            return cls.BL_OK

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, cb_t, c_void_p], lev=2) \
                    as lib_func:
                        if not cb:
                            # NOTE: workaround for deregistering a callback
                            # we have to set argtypes to nothing, otherwise
                            # ctypes will throw an exception or even crash
                            lib_func.argtypes = [c_void_p, c_void_p, c_void_p]
                            setattr(cls, name, None)
                            return lib_func(c_void_p(handle),
                                            c_void_p(cb),
                                            byref(userdata))

                        setattr(cls, name, cb_t(cb))
                        return lib_func(c_void_p(handle),
                                        getattr(cls, name),
                                        byref(userdata))


        @classmethod
        def BLC_registerDTLRequestCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_DTL)
            rv = cls._registerCallback(handle, cb,
                                       cb_t, '_dtl_request_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerDTLResponseCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_DTL)
            rv = cls._registerCallback(handle, cb,
                                       cb_t, '_dtl_response_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerDebugCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, c_char_p)
            rv = cls._registerCallback(handle, cb, cb_t, '_debug_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerErrorCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_ERROR)
            rv = cls._registerCallback(handle, cb, cb_t, '_error_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataEvent(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_EVENT, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t,
                                           c_void_p(userdata),
                                           '_event_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerEventCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_EVENT)
            rv = cls._registerCallback(handle, cb, cb_t, '_event_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerFrameCallback(cls, handle, cb):
            """Registers a callback function, which is called on every
               reception of (monitored) frame.

               Deprecated: BLC_registerUserDataFrameCallback instead

               Issuing a None de-registers the callback function.
               As the function is called from another thread context,
               take care of thread-safety (i.e. using mutexes, * etc.).

               :type channelHandle: integer
               :param channelHandle: handle representing the channel on
                                     which the frame occurred.

               :type cb: class 'function' or NoneType
               :param cb: function call-compatible to cb_t type.

               :type cb_t: _ctypes.PyCFuncPtrType
               :param cb_t: denotes the type of the callback

               :raise BabyLINException: if callback cannot be registered

               :rtype: integer
               :return: Status of operation; '=0' means successful, '!=0' error.
            """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_FRAME)
            rv = cls._registerCallback(handle, cb, cb_t, '_frame_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerJumboFrameCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_JUMBO_FRAME)
            return cls._registerCallback(handle, cb, cb_t,
                                         '_jumbo_frame_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerMacroStateCallback(cls, handle, cb):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_MACRO_STATE)
            rv = cls._registerCallback(handle, cb,
                                       cb_t, '_macro_state_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerSignalCallback(cls, channelHandle, cb):
            """Registers a callback function, which is called on every
               reception of a (monitored) signal.

               Deprecated: BLC_registerUserDataSignalCallback instead.

               Issuing a None de-registers the callback function.
               As the function is called from another thread context,
               take care of thread-safety (i.e. using mutexes, * etc.).

               :type channelHandle: integer
               :param channelHandle: handle representing the channel on
                                     which the signal occurred.

               :type cb: class 'function' or NoneType
               :param cb: function call-compatible to cb_t type.

               :type cb_t: _ctypes.PyCFuncPtrType
               :param cb_t: denotes the type of the signal callback

               :raise BabyLINException: if signal callback cannot be registered

               :rtype: integer
               :return: Status of operation; '=0' means successful, '!=0' error.
            """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_SIGNAL)
            rv = cls._registerCallback(channelHandle, cb,
                                       cb_t, '_signal_callback')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataDTLRequestCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_DTL, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t,
                                           c_void_p(userdata),
                                           '_dtl_request_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataDTLResponseCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_DTL, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t,
                                           c_void_p(userdata),
                                           '_dtl_response_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataDebugCallback(cls, handle, cb, userdata):
            """
            Note that there is a problem with this function: for instance,
            if we register the following callback:

                def debug_callback(channel_handle, text, userdata):
                    import ctypes
                    c_int64_p = ctypes.POINTER(ctypes.c_int64)
                    print('userdata=', userdata)
                    print(ctypes.cast(eval(str(userdata)), c_int64_p).contents)
                    return 0

            then userdata contains the address of the real data, which is OK,
            but then it seems that there is no way to dereference this
            pointer. The method above does somehow not work: '.contents' does
            not show the data, it shows the address again...
            """
            cb_t = CFUNCTYPE(c_int, c_void_p, c_char_p, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t,
                                           c_void_p(userdata),
                                           '_debug_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataErrorCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_ERROR, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t, c_void_p(userdata),
                                           '_error_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv



        @classmethod
        def BLC_registerUserDataEventCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_EVENT, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t, c_void_p(userdata),
                                           '_event_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataFrameCallback(cls, hndl, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_FRAME, c_void_p)
            rv = cls._registerCallbackUser(hndl, cb, cb_t,
                                           c_void_p(userdata),
                                           '_frame_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataJumboFrameCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_EVENT, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t, c_void_p(userdata),
                                           '_jumboframe_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataMacroStateCallback(cls, handle, cb, userdata):
            """ """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_EVENT, c_void_p)
            rv = cls._registerCallbackUser(handle, cb, cb_t, c_void_p(userdata),
                                           '_macrostate_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        @classmethod
        def BLC_registerUserDataSignalCallback(cls, chHandle, cb, userdata):
            """Registers a callback function, which is called on every
               reception of a (monitored) signal.

               Issuing a None de-registers the callback function.
               As the function is called from another thread context,
               take care of thread-safety (i.e. using mutexes, * etc.).

               NOTE: the user has to define some userdata himself, and the act
                     inside the callback accordingly.

                     Example:
                     =======

                        i: Define some data structure:

                            class BLC_CUSTOM(ctypes.Structure):
                                _fields_ = [("var",    c_int),
                                            ("device", c_char * 256)]

                        ii: initialize data:

                            user_data = BLC_CUSTOM()
                            user_data.var = 1234
                            user_data.device = b'user_device'

                        iii: register the callback:

                            BLC_registerUserDataSignalCallback(
                                lin_channel, signalcallback_user, user_data)

                        iv: where 'signalcallback_user' has a form as in

                            def signalcallback_user(handle, signal, userdata):

                                data = \
                                    ctypes.cast(userdata,
                                                POINTER(BLC_CUSTOM)).contents

                                print(data.var)
                                print(data.device.decode('utf-8'))

                                print(str(signal))
                                return 0

                        v: Always make sure that theuser_data are available as
                           long as the callback is active, i.e. not collected
                           by the python interpreter.


               :type channelHandle: integer
               :param channelHandle: handle representing the channel on
                                     which the signal occurred.

               :type cb: class 'function' or NoneType
               :param cb: function call-compatible to cb_t type.

               :type cb_t: _ctypes.PyCFuncPtrType
               :param cb_t: denotes the type of the signal callback

               :type userdata: user defined type
               :param userdata: pointer to custom user data to pass to
                                the callback.

               :raise BabyLINException: if signal callback cannot be registered

               :rtype: integer
               :return: Status of operation; '=0' means successful, '!=0' error.
            """
            cb_t = CFUNCTYPE(c_int, c_void_p, BabyLIN.BLC_SIGNAL, c_void_p)
            rv = cls._registerCallbackUser(chHandle, cb, cb_t,
                                           c_void_p(userdata),
                                           '_signal_cb_user')
            if rv != cls.BL_OK:
                raise cls.BabyLINException(rv, "")
            return rv


        #
        # Frames
        #

        @classmethod
        def BLC_getFrameCount(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                return lib_func(c_void_p(handle))


        @classmethod
        def BLC_getFrameDetails(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int,
                             c_void_p, c_void_p, c_void_p, c_void_p]) \
                    as lib_func:
                        busid, size        = c_int(-1), c_int(-1)
                        nodenum, frametype = c_int(-1), c_int(-1)
                        rv = lib_func(c_void_p(handle),
                                      c_int(idx),
                                      byref(busid),
                                      byref(size),
                                      byref(nodenum),
                                      byref(frametype))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return busid.value, size.value, nodenum, frametype


        @classmethod
        def BLC_getFrameIdForFrameNr(cls, handle, frameNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_ubyte]) as lib_func:
                rv = lib_func(c_void_p(handle), c_ubyte(frameNr))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv



        @classmethod
        def BLC_getFrameName(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    dstLen = c_int(512)
                    dst = create_string_buffer(dstLen.value)
                    rv = lib_func(c_void_p(handle),
                                  c_int(idx),
                                  dst,
                                  dstLen)
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return dst.value


        @classmethod
        def BLC_getFrameNrForFrameId(cls, handle, frameId):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_uint]) as lib_func:
                rv = lib_func(c_void_p(handle), c_uint(frameId))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_getLastFrame(cls, handle, frameNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, POINTER(cls.BLC_FRAME)]) \
                    as lib_func:
                        frame = cls.BLC_FRAME()
                        rv = lib_func(c_void_p(handle), c_int(frameNr),
                                      byref(frame))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return frame


        @classmethod
        def BLC_getNextFrame(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_FRAME)]) \
                    as lib_func:
                        frame = cls.BLC_FRAME()
                        rv = lib_func(c_void_p(channelHandle), byref(frame))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return frame

        @classmethod
        def BLC_getNextJumboFrame(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_JUMBO_FRAME)]) \
                    as lib_func:
                        jumbo_frame = cls.BLC_JUMBO_FRAME()
                        rv = lib_func(c_void_p(channelHandle),
                                      byref(jumbo_frame))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return jumbo_frame


        @classmethod
        def BLC_getNextFrameTimeout(cls, handle, timeOutInMilliSeconds):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_FRAME), c_int]) \
                    as lib_func:
                        frame = cls.BLC_FRAME()
                        rv = lib_func(c_void_p(handle), byref(frame),
                                      c_int(timeOutInMilliSeconds))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return frame


        @classmethod
        def BLC_getNextJumboFrameTimeout(cls, handle, timeOutInMilliSeconds):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_JUMBO_FRAME), c_int]) \
                    as lib_func:
                        jumbo_frame = cls.BLC_JUMBO_FRAME()
                        rv = lib_func(c_void_p(handle),
                                      byref(jumbo_frame),
                                      c_int(timeOutInMilliSeconds))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return jumbo_frame


        @classmethod
        def BLC_getNextFrames(cls, handle, numberOfFrames):
            """ """
            if numberOfFrames <= 0:
                raise cls.BabyLINException(-1, "numberOfFrames <= 0")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_FRAME), c_void_p]) \
                    as lib_func:
                        frames = (cls.BLC_FRAME * numberOfFrames)()
                        size = c_int(numberOfFrames)
                        rv = lib_func(c_void_p(handle), byref(frames[0]),
                                      byref(size))
                        if ((rv == cls.BL_NO_DATA) or
                            (rv == cls.BL_WRONG_PARAMETER) or
                            (rv == cls.BL_HANDLE_INVALID)):
                            raise cls.BabyLINException(rv, "")
                        return frames[:size.value]


        @classmethod
        def BLC_getNextJumboFrames(cls, handle, numberOfFrames):
            """ """
            if numberOfFrames <= 0:
                raise cls.BabyLINException(-1, "numberOfFrames <= 0")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p,
                             POINTER(cls.BLC_JUMBO_FRAME), c_void_p]) \
                    as lib_func:
                        jumbo_frames = (cls.BLC_JUMBO_FRAME * numberOfFrames)()
                        size = c_int(numberOfFrames)
                        rv = lib_func(c_void_p(handle),
                                      byref(jumbo_frames[0]),
                                      byref(size))
                        if ((rv == cls.BL_NO_DATA) or
                            (rv == cls.BL_WRONG_PARAMETER) or
                            (rv == cls.BL_HANDLE_INVALID)):
                            raise cls.BabyLINException(rv, "")
                        return jumbo_frames[:size.value]


        @classmethod
        def BLC_getNextFramesTimeout(cls, handle, numberOfFrames,
                                     timeOutInMilliSeconds):
            """ """
            if numberOfFrames <= 0:
                raise cls.BabyLINException(-1, "numberOfFrames <= 0")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p,
                             POINTER(cls.BLC_FRAME),
                             c_int,
                             c_void_p]) \
                    as lib_func:
                        frames = (cls.BLC_FRAME * numberOfFrames)()
                        size = c_int(numberOfFrames)
                        rv = lib_func(c_void_p(handle),
                                      byref(frames[0]),
                                      c_int(timeOutInMilliSeconds),
                                      byref(size))
                        if ((rv == cls.BL_NO_DATA) or
                            (rv == cls.BL_WRONG_PARAMETER) or
                            (rv == cls.BL_HANDLE_INVALID)):
                            raise cls.BabyLINException(rv, "")
                        return frames[:size.value]


        @classmethod
        def BLC_getNextJumboFramesTimeout(cls, handle, numberOfFrames,
                                          timeOutInMilliSeconds):
            """ """
            if numberOfFrames <= 0:
                raise cls.BabyLINException(-1, "numberOfFrames <= 0")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p,
                             POINTER(cls.BLC_JUMBO_FRAME),
                             c_int,
                             c_void_p]) \
                    as lib_func:
                        jumbo_frames = (cls.BLC_JUMBO_FRAME * numberOfFrames)()
                        size = c_int(numberOfFrames)
                        rv = lib_func(c_void_p(handle),
                                      byref(jumbo_frames[0]),
                                      c_int(timeOutInMilliSeconds),
                                      byref(size))
                        if ((rv == cls.BL_NO_DATA) or
                            (rv == cls.BL_WRONG_PARAMETER) or
                            (rv == cls.BL_HANDLE_INVALID)):
                            raise cls.BabyLINException(rv, "")
                        return jumbo_frames[:size.value]

        #
        # Signals
        #

        @classmethod
        def BLC_encodeSignal(cls, handle, signalNr, value):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p,
                             c_int,
                             c_ulonglong,
                             c_char_p,
                             c_void_p,
                             c_char_p,
                             c_void_p]) as lib_func:
                    bufLen0 = 128
                    bufLen1 = 128
                    encSignal = c_char_p(six.binary_type(bufLen0))
                    encUnit   = c_char_p(six.binary_type(bufLen1))
                    rv = lib_func(c_void_p(handle),
                                  c_int(signalNr),
                                  c_ulonglong(value),
                                  encSignal,
                                  byref(c_int(bufLen0)),
                                  encUnit,
                                  byref(c_int(bufLen1)))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return encSignal[:bufLen0].decode('utf-8'), \
                           encUnit[:bufLen1].decode('utf-8')


        @classmethod
        def BLC_getNextSignal(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_SIGNAL)]) \
                    as lib_func:
                        signal = cls.BLC_SIGNAL()
                        rv = lib_func(c_void_p(channelHandle), byref(signal))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return signal


        @classmethod
        def BLC_getNextSignals(cls, handle, numberOfSignals):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_SIGNAL), c_void_p]) \
                    as lib_func:
                        signals = (cls.BLC_SIGNAL * numberOfSignals)()
                        size = c_int(numberOfSignals)
                        rv = lib_func(c_void_p(handle), byref(signals[0]),
                                      byref(size))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return signals[:size]


        @classmethod
        def BLC_getNextSignalsForNumber(cls, handle, numberOfSignals, signalNr):
            """ """
            if numberOfSignals <= 0:
                raise cls.BabyLINException(rv, "numberOfSignals <= 0")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_SIGNAL), c_int, c_int]) \
                    as lib_func:
                        signals = (cls.BLC_SIGNAL * numberOfSignals)()
                        size = c_int(numberOfSignals)
                        rv = lib_func(c_void_p(handle), byref(signals[0]),
                                      size, c_int(signalNr))
                        if rv < 0:
                            raise cls.BabyLINException(rv, "")
                        return signals[:rv]


        @classmethod
        def BLC_setsig(cls, handle, signalNr, value):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_ulonglong]) as lib_func:
                    rv = lib_func(c_void_p(handle), c_int(signalNr),
                                  c_ulonglong(value))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_getSignalArray(cls, handle, signalNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_void_p]) as lib_func:
                    array = c_char_p(six.binary_type(8))
                    rv = lib_func(c_void_p(handle), c_int(signalNr), array)
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return array


        @classmethod
        def BLC_getSignalArrayByName(cls, handle, signalName):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_char_p]) as lib_func:
                    signalName_ = BabyLIN._create_string_buffer(signalName)
                    array = c_char_p(six.binary_type(8))
                    rv = lib_func(c_void_p(handle), signalName_, array)
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return array


        @classmethod
        def BLC_getSignalArrayWithTimestamp(cls, handle, signalNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_void_p, c_void_p]) as lib_func:
                    array = c_char_p(six.binary_type(8))
                    timeStamp = c_ulonglong(0)
                    rv = lib_func(c_void_p(handle), c_int(signalNr),
                                  array, byref(timeStamp))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return array, timeStamp


        @classmethod
        def BLC_getSignalCount(cls, handle):
            """Get number of signals of the bus according to the
               informations in the loaded SDF.

            Arguments:
            cls -- reference to surrounding class
            handle -- channel handle (see BLC_getChannelHandle)

            Raises exception of type BabyLIN.BabyLINException is case
            of error.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                rv = lib_func(c_void_p(handle))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_getSignalInFrame(cls, handle, frameIndex, signalIndex):
            """Retrieve the signal number of a signal mapped in a frame.

            Arguments:
            cls -- reference to surrounding class
            handle -- channel handle (see BLC_getChannelHandle)
            frameIndex  -- Zero based index of the frame the signal is
                           mapped to (see BLC_getFrameCount)
            signalIndex -- Zero based index of the signal as mapped to
                           the frame (BLC_getSignalsInFrameCount)
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_int]) as lib_func:
                return lib_func(c_void_p(handle), c_int(frameIndex),
                                c_int(signalIndex))


        @classmethod
        def BLC_getSignalName(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    dstLen = c_int(512)
                    dst = create_string_buffer(dstLen.value)
                    rv = lib_func(c_void_p(handle),
                                  c_int(idx),
                                  dst,
                                  dstLen)
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return dst.value


        @classmethod
        def BLC_getSignalSize(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(handle), c_int(idx))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_getSignalValue(cls, channelHandle, signalNr):
            """Return the current signal value (for non-array signals).

               Note: The Baby-LIN reports the signal value only if the
                     command "dissignal" has been sent before.

               Note: the special signalNr '-1' returns always 4711
                     signalNr '-2' returns a counter increased by 1 after
                     every call.

               :type channelHandle:  integer
               :param channelHandle: handle representing the channel to get
                                     the signal value

               :type signalNr: integer
               :param signalNr: number of the signal according to SDF.

               :raise BabyLINException: if port cannot be opened

               :rtype: integer
               :return: the current signal value.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_void_p]) as lib_func:
                    value = c_ulonglong(-1)
                    rv = lib_func(c_void_p(channelHandle),
                                  c_int(signalNr), byref(value))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return value.value


        @classmethod
        def BLC_getSignalValueByName(cls, channelHandle, signalName):
            """Return the current signal value (for non-array signals).

               Note: The Baby-LIN reports the signal value only if the
                     command "dissignal" has been sent before.

               Note: do not pass 'signalName' as byte-string

               Note: the special signalNr '-1' returns always 4711
                     signalNr '-2' returns a counter increased by 1 after
                     every call.

               :type channelHandle:  integer
               :param channelHandle: handle representing the channel to get
                                     the signal value

               :type signalName: string
               :param signalName: name of the signal according to SDF.

               :raise BabyLINException: if port cannot be opened or a
                                        byte-string is passed as signal
                                        name.

               :rtype: integer
               :return: the current signal value.
            """
            if isinstance(signalName, six.binary_type):
                raise cls.BabyLINException(-1, "passed signal as byte string")

            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p]) as lib_func:
                    value = c_ulonglong(-1)
                    name = c_char_p(signalName.encode('utf-8'))
                    rv = lib_func(c_void_p(channelHandle), name, byref(value))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return value.value


        @classmethod
        def BLC_getSignalValueWithTimestamp(cls, channelHandle, signalNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_void_p, c_void_p]) \
                    as lib_func:
                        value, timeStamp = c_ulonglong(-1), c_ulonglong(0)
                        rv = lib_func(c_void_p(channelHandle),
                                      c_int(signalNr),
                                      byref(value),
                                      byref(timeStamp))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return value.value, timeStamp.value


        @classmethod
        def BLC_getSignalsInFrame(cls, handle, frameNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, POINTER(cls.BLC_SIGNAL), c_int]) \
                    as lib_func:
                        length = 64
                        signals = (cls.BLC_SIGNAL * length)()
                        rv = lib_func(c_void_p(handle), c_int(frameNr),
                                      byref(signals[0]), c_int(length))
                        if rv < 0:
                            raise cls.BabyLINException(rv, "")
                        return signals[:rv]


        @classmethod
        def BLC_getSignalsInFrameCount(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                rv = lib_func(c_void_p(handle), c_int(idx))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_isSignalArray(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                rv = lib_func(c_void_p(handle), c_int(idx))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_isSignalEmulated(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                rv = lib_func(c_void_p(handle), c_int(idx))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_decodeSignal(cls, handle, signalNr, encSignal):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p]) as lib_func:
                value = c_longlong()
                encSignal_ = BabyLIN._create_string_buffer(encSignal)
                rv = lib_func(c_void_p(handle),
                              c_int(signalNr),
                              encSignal_,
                              byref(value))
                if rv != BL_OK:
                    raise cls.BabyLINException(rv, "")
                return rv, value.value


        #
        # Nodes
        #

        @classmethod
        def BLC_getNodeCount(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                rv = lib_func(c_void_p(handle))
                if rv < 0:
                    raise cls.BabyLINException(rv, "")
                return rv


        @classmethod
        def BLC_getNodeForSignal(cls, handle, signalNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                    try:
                        rv = lib_func(c_void_p(handle), c_int(signalNr))
                        if rv <= -1:
                            raise cls.BabyLINException(rv, "")
                        return rv
                    except OSError as e:
                        six.print_(six.text_type(e))
                        six.print_("Possible reason: wrong channel handle")
                        raise


        @classmethod
        def BLC_getNodeName(cls, handle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    dstLen = c_int(512)
                    dst = create_string_buffer(dstLen.value)
                    rv = lib_func(c_void_p(handle),
                                  c_int(idx),
                                  dst,
                                  dstLen)
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return dst.value
                    
        @classmethod
        def BLC_varRead(cls, channelHandle, signalNr, numberOfSignalsToRead):
            """ numberOfSignalsToRead: signals are always 8 byte signals."""
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    if numberOfSignalsToRead > 4096:
                        raise cls.BabyLINException(-1, "numberOfSignalsToRead > 4096")                        
                    dstLen = c_int(numberOfSignalsToRead)
                    dst = create_string_buffer(dstLen.value)                    
                    rv = lib_func(c_void_p(channelHandle),
                                  c_int(signalNr),
                                  dst,
                                  dstLen)
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return dst.value
                    
        @classmethod        
        def BLC_varWrite(cls, channelHandle, signalNr, dstBuf, numberOfSignalsToWrite):
            """ numberOfSignalsToWrite: signals are always 8 byte signals.
                dstBuf = b'\x32\x33\x35\x37'
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                if numberOfSignalsToWrite > len(dstBuf):
                    raise cls.BabyLINException(-1, "too many numberOfSignalsToWrite for given input buffer")
                if numberOfSignalsToWrite > 4096:
                    raise cls.BabyLINException(-1, "numberOfSignalsToWrite > 4096")
                rv = lib_func(c_void_p(channelHandle),
                              c_int(signalNr),
                              c_char_p(dstBuf),
                              c_int(numberOfSignalsToWrite))
                if rv != cls.BL_OK:
                  raise cls.BabyLINException(rv, "")
                return rv
            
        @classmethod
        def BLC_AdHoc_DefaultProtocol(cls, type):
            with BabyLIN.ForeignFunctionParameterTypes(cls, cls.BLC_ADHOC_PROTOCOL, [c_uint]) as lib_func:
                return lib_func(c_uint(type))
            
        @classmethod
        def BLC_AdHoc_DefaultService(cls, protocol):
            with BabyLIN.ForeignFunctionParameterTypes(cls, cls.BLC_ADHOC_SERVICE, [cls.BLC_ADHOC_PROTOCOL]) as lib_func:
                return lib_func(protocol)
            
        @classmethod
        def BLC_AdHoc_DefaultExecute(cls):
            with BabyLIN.ForeignFunctionParameterTypes(cls, cls.BLC_ADHOC_EXECUTE, []) as lib_func:
                return lib_func()
            
        #int BL_DLLIMPORT BLC_AdHoc_CreateProtocol(BL_HANDLE channel,
        #                                  BLC_ADHOC_PROTOCOL* protocol,
        #                                  BL_ADHOC_HANDLE* protocol_handle);
        @classmethod
        def BLC_AdHoc_CreateProtocol(cls, channelHandle, protocol):
            with BabyLIN.ForeignFunctionParameterTypes(cls, c_int, [c_void_p, POINTER(cls.BLC_ADHOC_PROTOCOL), POINTER(c_int)]) as lib_func:
                protocol_handle = c_int()
                rv = lib_func(c_void_p(channelHandle), byref(protocol), byref(protocol_handle))
                if rv != cls.BL_OK:
                    raise cls.BabyLINException(rv, "")
                return protocol_handle
            
        @classmethod
        def BLC_AdHoc_CreateService(cls, channelHandle, protocol_handle, service):
            with BabyLIN.ForeignFunctionParameterTypes(cls, c_int, [c_void_p, c_int, POINTER(cls.BLC_ADHOC_SERVICE), POINTER(c_int)]) as lib_func:
                service_handle = c_int()
                rv = lib_func(c_void_p(channelHandle), protocol_handle, byref(service), byref(service_handle))
                if rv != cls.BL_OK:
                    raise cls.BabyLINException(rv, "")
                return service_handle
        
        
        @classmethod
        def BLC_AdHoc_Execute(cls, channelHandle, protocol_handle, service_handle, execute_flags, req_payload, timeout):
            """
            :returns: bytes object of response payload
            :raises BabyLINException: if error occurs
            """
            with BabyLIN.ForeignFunctionParameterTypes(cls, c_int, [c_void_p, # BL_HANDLE channel
                                                                    c_int,    # BL_ADHOC_HANDLE protocol_handle
                                                                    c_int,    # BL_ADHOC_HANDLE service_handle
                                                                    POINTER(cls.BLC_ADHOC_EXECUTE), # BLC_ADHOC_EXECUTE* execute_flags
                                                                    c_char_p,       # const unsigned char* req_payload
                                                                    c_int,          # int req_payload_length
                                                                    c_char_p,       # unsigned char* rsp_payload
                                                                    POINTER(c_int), # int* rsp_payload_length
                                                                    c_int           # int timeout
                                                                    ]) as lib_func:
                req_char_ptr = c_char_p(req_payload)
                buffer = ctypes.create_string_buffer(4096)
                rsp_buffer_len = c_int(4096)
                rv = lib_func(c_void_p(channelHandle),
                              protocol_handle, 
                              service_handle, 
                              byref(execute_flags), 
                              req_char_ptr, 
                              len(req_payload), 
                              buffer, 
                              byref(rsp_buffer_len),
                              timeout)
                buffer_array = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint8 * rsp_buffer_len.value))

                if rv != cls.BL_OK:
                    raise cls.BabyLINException(rv, "")
                return bytes(buffer_array.contents)

        #
        # Macros
        #

        @classmethod
        def BLC_macro_result(cls, handle, macroNr, timeOutMilliSeconds):
            """ Executes "macro_result" in a loop until "macro_result" returns
            anything else than 150 (macro still running), or timeout_ms is
            exceeded. A possible return value of "macro_result" is stored into
            return_value if the returncode was 155 (finished with error),
            156 (finished with exception) or 0 (macro finished).
            BLC_macro_result returns the last return value of "macro_result"
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_void_p, c_uint]) \
                    as lib_func:
                        returnValue = c_longlong(0)
                        macro_result = 0
                        rv = lib_func(c_void_p(handle),
                                      c_int(macroNr),
                                      byref(returnValue),
                                      c_uint(timeOutMilliSeconds))
                        # if BL_MACRO_ERRCODE_IN_RESULT,
                        # BL_MACRO_EXCEPTIONCODE_IN_RESULT or
                        # BL_MACRO_FINISHED, then returnValue.value might be
                        # of interest.
                        if rv == cls.BL_MACRO_ERRCODE_IN_RESULT or \
                           rv == cls.BL_MACRO_EXCEPTIONCODE_IN_RESULT or \
                           rv == cls.BL_MACRO_FINISHED:
                            macro_result = returnValue.value

                        return rv, macro_result

        @classmethod
        def BLC_getMacroResultString(cls, handle, macro_nr):
            """Note: To receive the macro-result-string it may be necessary
            to make sure the macro has been started. A call to 'macro_exec'
            does not mean the macro has been executed, only the command has
            been sent to the device.
            """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    dstLen = c_int(512)
                    dst = create_string_buffer(dstLen.value)
                    rv = lib_func(c_void_p(handle),
                                  c_int(macro_nr),
                                  dst,
                                  dstLen)
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return dst.value.decode("utf-8")

        #
        # SDF
        #

        @classmethod
        def SDF_close(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(handle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def SDF_downloadSectionToChannel(cls, sdfHandle, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(sdfHandle),
                                  c_void_p(channelHandle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def SDF_downloadToDevice(cls, sdfHandle, connectionHandle, mode):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_void_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(sdfHandle),
                                  c_void_p(connectionHandle),
                                  c_int(mode))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def SDF_getSectionCount(cls, sdfHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(sdfHandle))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def SDF_getSectionHandle(cls, sdfHandle, sectionNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_void_p, c_int]) as lib_func:
                    secHandle = lib_func(c_void_p(sdfHandle),
                                         c_int(sectionNr))
                    if not secHandle:
                        raise cls.BabyLINException(-1,
                                                   "Invalid section handle")
                    return secHandle


        @classmethod
        def SDF_getSectionInfo(cls, sectionHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.SDF_SECTIONINFO)]) \
                        as lib_func:
                            secInfo = cls.SDF_SECTIONINFO()
                            rv = lib_func(c_void_p(sectionHandle),
                                          byref(secInfo))
                            if rv != cls.SDF_OK:
                                raise cls.BabyLINException(rv, "")
                            return secInfo


        @classmethod
        def SDF_open(cls, fname):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_char_p]) as lib_func:
                    if not os.path.isfile(fname):
                        raise cls.BabyLINException(-1,
                                "file {} does not exists".format(fname))
                    sdfHandle = lib_func(c_char_p(fname.encode('utf-8')))
                    if not sdfHandle:
                        s = "invalid handle for {}".format(fname)
                        raise cls.BabyLINException(-1, s)
                    return sdfHandle


        @classmethod
        def SDF_openLDF(cls, fname):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_void_p, [c_char_p]) as lib_func:
                    if not os.path.isfile(fname):
                        raise cls.BabyLINException(-1,
                                "file {} does not exists".format(fname))
                    ldfHandle = lib_func(c_void_p(fname.encode('utf-8')))
                    if not ldfHandle:
                        raise cls.BabyLINException(-1, "invalid handle")
                    return ldfHandle


        @classmethod
        def BLC_SDF_getFrameNr(cls, channelHandle, fname):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    fname_ = BabyLIN._create_string_buffer(fname)
                    rv = lib_func(c_void_p(channelHandle),
                                  fname_)
                    if rv <= -1:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_SDF_getMacroNr(cls, channelHandle, macroName):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    macroName_ = BabyLIN._create_string_buffer(macroName)
                    rv = lib_func(c_void_p(channelHandle),
                                  macroName_)
                    if rv <= -1:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_SDF_getNodeNr(cls, channelHandle, nodeName):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    nodeName_ = BabyLIN._create_string_buffer(nodeName)
                    rv = lib_func(c_void_p(channelHandle),
                                  nodeName_)
                    if rv <= -1:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_SDF_getNumSchedules(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    return lib_func(c_void_p(channelHandle))


        @classmethod
        def BLC_SDF_getScheduleName(cls, channelHandle, scheduleNr):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_char_p, [c_void_p, c_int]) as lib_func:
                    return lib_func(c_void_p(channelHandle),
                                    c_int(scheduleNr)).decode('utf-8')


        @classmethod
        def BLC_SDF_getScheduleNr(cls, channelHandle, scheduleName):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    schedName_ = BabyLIN._create_string_buffer(scheduleName)
                    rv = lib_func(c_void_p(channelHandle),
                                  schedName_)
                    if rv <= -1:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_SDF_getSignalNr(cls, channelHandle, signalName):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    sigName_ = BabyLIN._create_string_buffer(signalName)
                    rv = lib_func(c_void_p(channelHandle),
                                  sigName_)
                    if rv <= -1:
                        raise cls.BabyLINException(rv, "")
                    return rv

        #
        # Misc
        #

        @classmethod
        def BLC_getAnswerByIndex(cls, channelHandle, idx):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_uint, c_void_p, c_uint]) as lib_func:
                    bufLen = 64
                    buf = c_char_p(six.binary_type(bufLen))
                    rv = lib_func(c_void_p(channelHandle),
                                  c_uint(idx), buf, c_uint(bufLen))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return buf.value



        @classmethod
        def BLC_getAnswerByName(cls, channelHandle, name):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p, c_uint]) \
                    as lib_func:
                        bufLen = 64
                        buf = c_char_p(six.binary_type(bufLen))
                        rv = lib_func(c_void_p(channelHandle),
                                      c_char_p(name.encode('utf-8')),
                                      buf,
                                      c_uint(bufLen))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return buf.value


        @classmethod
        def BLC_getAnswerNameByIndex(cls, channelHandle, index):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_void_p]) \
                    as lib_func:
                        bufLen = 128
                        buf = c_char_p(six.binary_type(bufLen))
                        rv = lib_func(c_void_p(channelHandle),
                                      c_int(index),
                                      buf, byref(c_int(bufLen)))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return buf.value[:rv].decode('utf-8')


        @classmethod
        def BLC_getAnswerTypeByIndex(cls, channelHandle, index):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_void_p]) \
                    as lib_func:
                        answerType = c_char_p(six.binary_type(8))
                        length = c_uint(-1)
                        rv = lib_func(c_void_p(channelHandle),
                                      c_int(index),
                                      answerType,
                                      byref(length))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return answerType.value, length.value


        @classmethod
        def BLC_getAnswerTypeByName(cls, channelHandle, name):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_char_p, c_void_p]) \
                    as lib_func:
                        answerType = c_char_p(six.binary_type(8))
                        length = c_uint(-1)
                        rv = lib_func(c_void_p(channelHandle),
                                      c_char_p(name.encode('utf-8')),
                                      answerType,
                                      byref(length))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return answerType.value, length.value


        @classmethod
        def BLC_getDTLRequestStatus(cls, linChannelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(linChannelHandle))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_getDTLResponseStatus(cls, linChannelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(linChannelHandle))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_getErrorString(cls, error_code):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_char_p, [c_int]) as lib_func:
                    s = lib_func(c_int(error_code))
                    return s.decode('utf-8')


        @classmethod
        def BLC_getLastError(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_int]) as lib_func:
                    bufLen = c_int(256)
                    buf = create_string_buffer(bufLen.value)
                    rv = lib_func(c_void_p(handle), buf, bufLen)
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return buf.value.decode('utf-8')


        @classmethod
        def BLC_getDetailedErrorString(cls, error_code, report_parameter):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_int, c_int, c_char_p, c_int]) as lib_func:
                    bufLen = c_int(1024)
                    buf = create_string_buffer(bufLen.value)
                    rv = lib_func(c_int(error_code), c_int(report_parameter),
                                  buf, bufLen)
                    if rv == cls.BL_BUFFER_TOO_SMALL:
                        raise cls.BabyLINException(rv, "Buffer too small")
                    return buf.value.decode('utf-8')


        @classmethod
        def BLC_getNextBusError(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_ERROR)]) as lib_func:
                        error = cls.BLC_ERROR()
                        rv = lib_func(c_void_p(channelHandle),
                                      byref(error))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return error


        @classmethod
        def BLC_getNextDTLRequest(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_DTL)]) as lib_func:
                        frame = cls.BLC_DTL()
                        rv = lib_func(c_void_p(channelHandle),
                                      byref(frame))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return frame


        @classmethod
        def BLC_getNextDTLResponse(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, POINTER(cls.BLC_DTL)]) as lib_func:
                        frame = cls.BLC_DTL()
                        rv = lib_func(c_void_p(channelHandle),
                                      byref(frame))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return frame


        @classmethod
        def BLC_getRawSlaveResponse(cls, linChannelHandle, length):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_int]) as lib_func:
                    if length <= 0:
                        raise cls.BabyLINException(-1,
                                        "positive length argument needed")
                    bSize = c_int(length)
                    data = create_string_buffer(bSize.value)
                    rv = lib_func(c_void_p(linChannelHandle), data, bSize)
                    if rv != cls.BL_OK:
                        if rv == cls.BL_NO_DATA:
                            return rv, bytes(length)
                        raise cls.BabyLINException(rv, "")
                    return rv, bytes(data)


        @classmethod
        def BLC_lastAnswerHasData(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_mon_set(cls, channelHandle, frameId, dataBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_int(frameId),
                                  c_char_p(dataBytes),
                                  c_int(len(dataBytes)))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_mon_set_xmit(cls, channelHandle, frameId, dataBytes, slotTime):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_char_p, c_int, c_int]) \
                    as lib_func:
                        rv = lib_func(c_void_p(channelHandle),
                                      c_int(frameId),
                                      c_char_p(dataBytes),
                                      c_int(len(dataBytes)),
                                      c_int(slotTime))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_mon_xmit(cls, channelHandle, frameId, slotTime):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_int]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_int(frameId),
                                  c_int(slotTime))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_sendDTLRequest(cls, linChannelHandle, nad, dataBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_ubyte, c_int, c_char_p]) as lib_func:
                        length = len(dataBytes)

                        if length > 4095:
                            raise cls.BabyLINException(-1,
                                        "data more than 4095 bytes")

                        rv = lib_func(c_void_p(linChannelHandle),
                                      c_ubyte(nad),
                                      c_int(length),
                                      c_char_p(dataBytes))

                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_sendDTLResponse(cls, linChannelHandle, nad, dataBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_ubyte, c_int, c_char_p]) as lib_func:
                        length = len(dataBytes)

                        if length > 4095:
                            raise cls.BabyLINException(-1,
                                        "data more than 4095 bytes")

                        rv = lib_func(c_void_p(linChannelHandle),
                                      c_ubyte(nad),
                                      c_int(length),
                                      c_char_p(dataBytes))

                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_sendRaw(cls, connectionHandle, command):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p]) as lib_func:
                        cmd = command.encode('utf-8')
                        length = c_uint(len(cmd))
                        rv = lib_func(c_void_p(connectionHandle),
                                      c_char_p(cmd),
                                      byref(length))

                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_sendRawMasterRequest(cls, linChannelHandle, dataBytes, count):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_int]) as lib_func:

                        if len(dataBytes) != 8:
                            raise cls.BabyLINException(-1,
                                        "data no 8 bytes array")

                        rv = lib_func(c_void_p(linChannelHandle),
                                      c_char_p(dataBytes),
                                      c_int(count))

                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_sendRawSlaveResponse(cls, linChannelHandle,
                                     reqData, reqMask, dataBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_char_p, c_char_p, c_int]) \
                    as lib_func:

                        if len(reqData) != 8:
                            raise cls.BabyLINException(-1,
                                        "reqData no 8 bytes array")

                        if len(reqMask) != 8:
                            raise cls.BabyLINException(-1,
                                        "reqMask no 8 bytes array")

                        length = len(dataBytes)
                        if (length % 8) != 0:
                            raise cls.BabyLINException(-1,
                                        "data length no multiple of 8")

                        rv = lib_func(c_void_p(linChannelHandle),
                                      c_char_p(reqData),
                                      c_char_p(reqMask),
                                      c_char_p(dataBytes),
                                      c_int(length))

                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_setDTLMode(cls, linChannelHandle, mode):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int]) as lib_func:
                    rv = lib_func(c_void_p(linChannelHandle),
                                  c_int(mode))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_updRawSlaveResponse(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv

        #
        # DirectMode
        #

        @classmethod
        def BLC_dmDelay(cls, channelHandle, paddingTimeMicroSecs):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_uint]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_uint(paddingTimeMicroSecs))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_dmPrepare(cls, channelHandle, mode):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_ubyte]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_ubyte(mode))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_dmPulse(cls, channelHandle, lowTimeMicroSecs,
                        paddingTimeMicroSecs):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_uint, c_uint]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_uint(lowTimeMicroSecs),
                                  c_uint(paddingTimeMicroSecs))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_dmRead(cls, channelHandle, bufferSize):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_void_p, c_uint]) as lib_func:
                    buf = c_char_p(six.binary_type(bufferSize))
                    rv = lib_func(c_void_p(channelHandle),
                                  buf,
                                  c_uint(bufferSize))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return buf[:rv]


        @classmethod
        def BLC_dmReadTimeout(cls, channelHandle, bufferSize, timeoutMilliSecs):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_void_p, c_uint, c_uint]) as lib_func:
                    buf = c_char_p(six.binary_type(bufferSize))
                    rv = lib_func(c_void_p(channelHandle),
                                  buf,
                                  c_uint(bufferSize),
                                  c_uint(timeoutMilliSecs))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return buf[:rv]


        @classmethod
        def BLC_dmReportConfig(cls, channelHandle, timeout, nBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_int]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_int(timeout),
                                  c_int(nBytes))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_dmStart(cls, channelHandle,
                        baudrate, bitwidth, stopbits, parity):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_int, c_int, c_int, c_int]) \
                    as lib_func:
                        rv = lib_func(c_void_p(channelHandle),
                                      c_int(baudrate),
                                      c_int(bitwidth),
                                      c_int(stopbits),
                                      c_int(parity))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_dmStop(cls, channelHandle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_dmWrite(cls, channelHandle, dataBytes):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_uint]) as lib_func:
                    rv = lib_func(c_void_p(channelHandle),
                                  c_char_p(dataBytes),
                                  c_uint(len(dataBytes)))
                    if rv < 0:
                        raise cls.BabyLINException(rv, "")
                    return rv


        ################
        # Unified Access
        ################

        @classmethod
        def BLC_createHandle(cls, handle, path):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p]) as lib_func:
                    if isinstance(path, six.text_type):
                        path = path.encode('utf-8')
                    result = c_void_p()
                    p = create_string_buffer(path)
                    rv = lib_func(c_void_p(handle),
                                  p,
                                  byref(result))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return result.value


        @classmethod
        def BLC_destroy(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(handle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_releaseHandle(cls, handle):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p]) as lib_func:
                    rv = lib_func(c_void_p(handle))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_discover(cls, handle, path):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_char_p, c_void_p]) \
                    as lib_func:
                        p = BabyLIN._create_string_buffer(path)
                        bSize = c_uint(512)
                        buf = create_string_buffer(bSize.value)

                        rv = lib_func(c_void_p(handle),
                                      p,
                                      buf,
                                      byref(bSize))

                        if rv == cls.BLC_UA_INVALID_PARAMETER:
                            # try again with proper buffer size
                            if bSize.value > 0:
                                buf = create_string_buffer(bSize.value)
                                rv = lib_func(c_void_p(handle),
                                              p,
                                              buf,
                                              byref(bSize))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        else:
                            if bSize.value > 0:
                                if six.PY3: return \
                                    buf[:bSize.value].decode('utf-8').split()
                                if six.PY2: return buf[:bSize.value].split()
                        return ['']


        @classmethod
        def BLC_getSignedNumber(cls, handle, path):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p]) as lib_func:
                    p = BabyLIN._create_string_buffer(path)
                    result = c_longlong()
                    rv = lib_func(c_void_p(handle),
                                  p,
                                  byref(result))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return result.value


        @classmethod
        def BLC_getUnsignedNumber(cls, handle, path):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p]) as lib_func:
                    p = BabyLIN._create_string_buffer(path)
                    result = c_ulonglong()
                    rv = lib_func(c_void_p(handle),
                                  p,
                                  byref(result))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return result.value


        @classmethod
        def BLC_getBinary(cls, handle, path, *, remove_trailing_nul=False):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p, c_void_p]) \
                    as lib_func:
                        p = BabyLIN._create_string_buffer(path)
                        bSize = c_uint(512)
                        buf = create_string_buffer(bSize.value)

                        rv = lib_func(c_void_p(handle),
                                      p,
                                      buf,
                                      byref(bSize))

                        if rv == cls.BLC_UA_INVALID_PARAMETER:
                            # try again with proper buffer size
                            if bSize.value > 0:
                                buf = create_string_buffer(bSize.value)
                                rv = lib_func(c_void_p(handle),
                                              p,
                                              buf,
                                              byref(bSize))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        else:
                            if remove_trailing_nul:
                                if bSize.value > 1:
                                    cnt = bSize.value-1
                                    while cnt > 0 and buf[cnt] == 0x00:
                                        cnt = cnt - 1
                                    return buf[:cnt]
                            if bSize.value > 0:
                                return buf[:bSize.value]
                        return bytes()


        @classmethod
        def BLC_setSignedNumber(cls, handle, path, value):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_longlong]) as lib_func:
                    p = BabyLIN._create_string_buffer(path)
                    rv = lib_func(c_void_p(handle),
                                  p,
                                  c_longlong(value))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_setUnsignedNumber(cls, handle, path, value):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_ulonglong]) as lib_func:
                    p = BabyLIN._create_string_buffer(path)
                    rv = lib_func(c_void_p(handle),
                                  p,
                                  c_ulonglong(value))
                    if rv != cls.BL_OK:
                        raise cls.BabyLINException(rv, "")
                    return rv


        @classmethod
        def BLC_setBinary(cls, handle, path, value):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_char_p, c_uint]) \
                    as lib_func:
                        p = BabyLIN._create_string_buffer(path)
                        value_length = len(value)
                        rv = lib_func(c_void_p(handle),
                                      p,
                                      c_char_p(value),
                                      c_uint(value_length))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_setCallback(cls, handle, path, callback, parameter):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p, c_void_p]) \
                    as lib_func:
                        p = BabyLIN._create_string_buffer(path)
                        rv = lib_func(c_void_p(handle),
                                      p,
                                      c_void_p(callback),
                                      c_void_p(parameter))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


        @classmethod
        def BLC_execute(cls, handle, path):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p]) as lib_func:
                    p = BabyLIN._create_string_buffer(path)
                    rv = lib_func(c_void_p(handle), p)
                    if rv != cls.BL_OK:
                        s = 'with command %s' % path
                        raise cls.BabyLINException(rv, s)
                    return rv


        @classmethod
        def BLC_execute_async(cls, handle, callback, parameter):
            """ """
            with BabyLIN.ForeignFunctionParameterTypes(
                cls, c_int, [c_void_p, c_char_p, c_void_p, c_void_p]) \
                    as lib_func:
                        p = BabyLIN._create_string_buffer(path)
                        rv = lib_func(c_void_p(handle),
                                      p,
                                      c_void_p(callback),
                                      c_void_p(parameter))
                        if rv != cls.BL_OK:
                            raise cls.BabyLINException(rv, "")
                        return rv


    # return generated class
    return BabyLIN.config()





