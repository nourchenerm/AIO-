from __future__ import unicode_literals
from ctypes import *
import  sys, six, time
from network.protocol import Protocol
import logging
try:
    # import the BabyLIN Python wrapper
    import network.libs.BabyLIN_library as BabyLIN_library
except ImportError as e:
    six.print_(e)


"""
This code only handles one baby LIN device ( the device bey default).
TODO: make it compatible with multiple devices using a dict of 
baby_lins : {serial_number, conHandle, conHandle, sdf}
"""

MAX_PORTS = 10

def _on_receive_callback(handle, frame):
    """ frame callback to be used later."""
    if frame.frameId == 16:
        six.print_(frame)
    return 0


class BabyLIN_Handler(Protocol):
    
    def __init__(self, conf):
        super().__init__(conf)
        self.logger = logging.getLogger(__name__)
        self.sdf = conf.get('sdf_file') #sdf
        self.verbose = conf.get('verbose') #verbose
        self.is_readable_signals_set = False
        self._on_receive_callback = self.default__on_receive_callback
         


    def connect(self):
        try: 
            self.create_baby_lin()
            self.connect_port()
            self.open_device()
            self.start_bus()
            print("Successfully connected to device...")
        except Exception as e:
            six.print_(e)
            sys.exit(-1)   
            
    def set_on_receive_callback(self, callback):
        """Set a custom callback function to be called when a message is received."""
        self._on_receive_callback = callback
        self.BabyLIN.BLC_registerFrameCallback(self.chHandle, self._on_receive_callback)


    def default__on_receive_callback(self, handle, frame): 
        """ frame callback to be used later."""
        if frame.frameId == 16:
            six.print_(frame)
        return 0
    
    def print_wrapper_version(self):
        six.print_(self.BabyLIN.BLC_getWrapperVersion())
        
    
    def print_shared_object_version(self):
        # print shared object (BabyLIN.dll/libBabyLIN.so) version as numbers
        major, minor = self.BabyLIN.BLC_getVersion()
        six.print_("major={} minor={}".format(major, minor))

        # print shared object extended version as numbers
        major, minor, build, patch = self.BabyLIN.BLC_getExtendedVersion()
        six.print_("major={} minor={} build={} patch={}"
                .format(major, minor, build, patch))
        
        # print shared object version as string
        six.print_(self.BabyLIN.BLC_getVersionString())

    def create_baby_lin(self):
        """"""    
        self.BabyLIN = BabyLIN_library.create_BabyLIN()
        if self.verbose: 
            six.print_("Using dynamic library " + self.BabyLIN.BABYLIN_DLL_PATH_NAME)
            six.print_(f"Using sdf file : {self.sdf}")
            self.print_shared_object_version()
            self.print_wrapper_version()
            
    def connect_port(self):
        self.ports = self.BabyLIN.BLC_getBabyLinPorts(MAX_PORTS)
        if not self.ports:
            six.print_("No BabyLIN found")
            sys.exit(-1)

    def open_device(self):
        """ the example will open the first device with an included
        LIN channel, download the sdf to it, start the LIN bus,
        register a frame-callback and watch the incoming LIN-frames
        in the callback """
                       # open the device(s)
        conHandle    = (self.BabyLIN.BLC_openPort(port) for port in self.ports)

                       # get the device's number of channels
        channelCount = ((self.BabyLIN.BLC_getChannelCount(h), h) for h in conHandle)

                       # among these, look for the first LIN channel:
        channelRange = ((range(chNr), h) for chNr, h in channelCount)

                       # first, get the corresponding channel handles
        chHandle     = ((self.BabyLIN.BLC_getChannelHandle(h, channelIndex), h)
                            for r, h in channelRange for channelIndex in r)

                       # for each channel (handle), get the channel info
        chInfo       = ((self.BabyLIN.BLC_getChannelInfo(ch), h, ch) for ch, h in chHandle)

                       # using the channel info, filter the LIN channels
                       # using 'info.type == 0'
        self.conH_chH     = ((h, ch) for info, h, ch in chInfo if info.type == 0)
        
        
        for conHandle, chHandle in self.conH_chH:
            self.conHandle = conHandle
            self.chHandle = chHandle
            
        # for debugging, print the target-id
        six.print_(self.BabyLIN.BLC_getTargetID(self.conHandle))
        # load the sdf into the device. as soon as the LIN bus starts,
        # it will activate a LIN schedule table, and the LIN frames
        # will show up in the frame-callback '_on_receive_callback'.
        self.BabyLIN.BLC_loadSDF(self.conHandle, self.sdf, 1)
        # register the frame-callback
        self.BabyLIN.BLC_registerFrameCallback(self.chHandle, self._on_receive_callback)


    
    def start_bus(self):
        self.BabyLIN.BLC_sendCommand(self.chHandle, "start;")
        self.BabyLIN.BLC_sendCommand(self.chHandle, "disframe 255 1;")

            
    def set_signal(self, signal_index, value):
        self.BabyLIN.BLC_setsig(self.chHandle, signal_index, value)
                       
    def read_signal(self, signal_index):
        if self.is_readable_signals_set == True:
            return self.BabyLIN.BLC_getSignalValue(self.chHandle, signal_index)
        else: 
            print("Error can not read signal. Please call set_readable_signals first...")
            
    def send(self): 
        print('Function not implemented yet...')
    
    
    def start_sechdule_by_number(self, scehdule_number):
        self.BabyLIN.BLC_sendCommand(self.chHandle, f"start schedule {scehdule_number};")
        
    def start_sechdule_by_name(self, scehdule_name):
        schedule_nr = self.BabyLIN.BLC_SDF_getScheduleNr(self.chHandle, scehdule_name)
        self.BabyLIN.BLC_sendCommand(self.chHandle, f"start schedule {schedule_nr};")
        
    
    def execute_macro(self, macro_number):
        time.sleep(0.05)
        #self.BabyLIN.BLC_sendCommand(self.chHandle, f"execute macro {macro_number};")
        self.BabyLIN.BLC_sendCommand(self.chHandle, f" macro_exec {macro_number};")
        

    def set_readable_signals(self, signals_indexes : list):
        """ set the frame name and the signals in the frame 
        example: {
           0 :  
        }"""
        
        for signal_index in signals_indexes:
            self.BabyLIN.BLC_sendCommand(self.chHandle, f"dissignal {signal_index} 1;")
            time.sleep(0.2)
        self.is_readable_signals_set = True
            
        

            
            
    def disconnect(self):
        # wait before disconnect to make sure all previous commands are executed
        time.sleep(0.5) 
        # de-register the frame-callback
        self.BabyLIN.BLC_registerFrameCallback(self.chHandle, None)
        # stop the LIN-bus
        self.BabyLIN.BLC_sendCommand(self.chHandle, "stop;")
        # close all devices. end of example.
        self.BabyLIN.BLC_closeAll()
        print("Disconnected from device...")


