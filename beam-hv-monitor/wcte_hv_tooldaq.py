import time 
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

import cppyy, cppyy.ll
import ctypes
import sys
sys.path.insert(0,'/home/wcte/libDAQInterfaces/lib')
std = cppyy.gbl.std
try:
  cppyy.load_reflection_info('libDAQInterfaceClassDict')
except:
  raise BaseException("class dictionary not found: did you run 'make python'?") from None

from cppyy.gbl import ToolFramework
from cppyy.gbl.ToolFramework import DAQInterface

from wcte_hv_logger import wcte_beam_hv_read, hv

debug = True

class daq_interface_info:
  '''
  daq_interface_info is a class to wrap all the needed tooldaq operations
  '''
  def __init__(self, configfile='./InterfaceConfig'):
    self.configfile = configfile
    self.setup_tooldaq()

  def setup_tooldaq(self):
    '''
      Setup tooldaq connection and object to write data to
    ''' 
    print("Initialising daqinterface")
    self.daq_inter = DAQInterface( self.configfile )
    self.device_name = self.daq_inter.GetDeviceName()
    print("for "+self.device_name+"\n")

    # set initial status so we can track when the service is ready
    self.daq_inter.sc_vars["Status"].SetValue("Initialising")

    self.monitoring_data = cppyy.gbl.ToolFramework.Store()
    self.monitoring_data.Delete()

  # This function copied from water group's example -- I added a docstring (maybe wrong)
  def send_data( self, variable_name_list, values ):
    '''
    send_data Sends list of variables and values to toolDAQ database
    Inputs:
    variable_name_list ['name1','name2',...]   list of names of the variables being sent
    values             ['value1','value2',...] list of values corresponding to the names
    '''
    # populate the monitoring Store
    self.monitoring_data.Delete()
    print("setting monitoring vals")
    print('names=',variable_name_list)
    print('values=',values )
    for name,value in zip(variable_name_list,values):
      self.monitoring_data.Set(name, str(value))

    # generate a JSON from the contents
    monitoring_json = std.string("")
    self.monitoring_data.__rshift__['std::string'](monitoring_json)

    # send to the Database for plotting on the webpage
    sentData = self.daq_inter.SendMonitoringData(monitoring_json)
    if(sentData==False):
      print('send_data:',self.device_name,'failed to send data to database')


def wcte_hv_tooldaq(systemtype, linktype, address, username, password, timeinterval):
  '''
  wcte_hv_tooldaq connects to tooldaq, periodically queries hv mainframe, and sends data to database.

  Inputs:
  systemtype 'str' see wcte_hv_logger.wcte_beam_hv_read
  linktype   'str' ...
  address    'str' ...
  username   'str' ...
  password   'str' ...
  timeinterval int time in seconds between records (-1 if just one read)

  No return value, loops until killed.
  '''
  dq = daq_interface_info()
  
  print("start loop")
  while True:
    names, values = wcte_beam_hv_read( systemtype, linktype, address, username, password )
    dq.send_data( names, values )
    if timeinterval == -1:
      break
    time.sleep( timeinterval )
  return


def main():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    # Shared parser for subcommands
    parser.add_argument('-s', '--systemtype', type=str, help='system type', default='SY4527', choices=tuple(i.name for i in hv.SystemType))
    parser.add_argument('-l', '--linktype', type=str, help='system type', default='TCPIP', choices=tuple(i.name for i in hv.LinkType))
    parser.add_argument('-a', '--arg', type=str, help='connection argument (depending on systemtype and linktype)', default='192.168.11.12')
    parser.add_argument('-u', '--username', type=str, help='username', default='admin')
    parser.add_argument('-p', '--password', type=str, help='password', default='04310055')
    parser.add_argument('-t', '--timeinterval',type=int, help='time interval for recording (s), -1 for just one value', default=-1 )
    args = parser.parse_args()

    wcte_hv_tooldaq( args.systemtype, args.linktype, args.arg, args.username, args.password, args.timeinterval )
    print('Done.')
    return 0

if __name__ == "__main__":
  main()