#!/usr/bin/env python3
"""
WCTE HV read to logfile
"""

from caen_libs import caenhvwrapper as hv
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from time import sleep
import datetime

slots_of_interest=[2,4,6,8]
channels = { 2:[0,1,2,3,4,5,6,7,8,9,10,11], 
             4:[0,1,2,3,4,5,6,7,8,9,10],
             6:[0,1,2,5,6,7,8,9,10,11], 
             8:[0,1,2,3,4,5,6,7,8,9,10,11] }

channel_names = {
    2:['ACT0-L','ACT0-R','ACT1-L','ACT1-R','ACT2-L','ACT2-R','ACT3-L','ACT3-R','ACT4-L','ACT4-R','ACT5-L','ACT5-R'],
    4:['T1-0L','T1-0R','T1-1L','T1-1R','T0-1L','T0-1R','HC2','T3','T0-0L','T0-0R','T2','empty'],
    6:['HD-12','HD-13','HD-14','empty','empty','HC-0','HC-1','MuonTag-R','MuonTag-L','PbGlass','WMS-source','WMS-reci'],
    8:['HD-0','HD-1','HD-2','HD-3','HD-4','HD-5','HD-6','HD-7','HD-8','HD-9','HD-10','HD-11']
}
    
params_of_interest = ['V0Set','VMon','IMon','Pw']    

debug = True

def wcte_beam_hv_read( systemtype, linktype, address, username, password ):
    '''
    wcte_beam_hv_read reads the caen hv mainframe for the slots, channels and parameters hard coded in this module.

    Input arguments:
    systemtype 'str' is one of SY1527,SY2527,SY4527,SY5527,N568,V65XX,N1470,V8100,N568E,DT55XX,FTK,DT55XXE,N1068,SMARTHV,NGPS,N1168,R6060
    linktype   'str' is one of TCPIP,RS232,CAENET,USB,OPTLINK,USB_VCP,USB3,A4818
    address    'str' eg. '192.168.11.12' for a TCPIP address
    username   'str' eg. 'admin'
    password   'str' eg. 'admin'

    Returns: (as a tuple)
    list_of_names ['str','str',...] list of the names of the values read
    list_of_values ['value','value',....] list of strings containing values read
    '''
    list_of_names = []
    list_of_values = []

    if debug:
        print('systemtype=',systemtype)
        print('linktype=',linktype)
        print('address=',address)
        print('username=',username)
        print('password=',password)

    with hv.Device.open(hv.SystemType[systemtype], hv.LinkType[linktype], address, username, password) as device:
        for slot in slots_of_interest:
            for ch in channels[slot]:
                ch_params = device.get_ch_param_info(slot, ch)
                for param_name in ch_params:
                    if param_name in params_of_interest:
                        param_prop = device.get_ch_param_prop(slot, ch, param_name)
                        if param_prop.mode is not hv.ParamMode.WRONLY:
                            param_value = device.get_ch_param(slot, [ch], param_name)
                            list_of_names.append( channel_names[slot][ch]+'-'+param_name )
                            list_of_values.append( param_value[0] )
    
    return (list_of_names, list_of_values)


def main():

    # Parse arguments
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
    parser.add_argument('-f', '--filename',type=str,help='output logfile name',default='wcte-hv.log')

    args = parser.parse_args()
    print(args)

    print('------------------------------------------------------------------------------------')
    print(f'CAEN HV Logger (lib version {hv.lib.sw_release()})')
    print('------------------------------------------------------------------------------------')

    list_of_names = []
    list_of_values = []
    
    fileout = open(args.filename,'w')

    header='Date Time '
    for slot in slots_of_interest:
        for ch in channels[slot]:
            for parname in params_of_interest:
                header+=channel_names[slot][ch]+'-'+parname+' '

    fileout.write(header+'\n')

    while (True):
        names, values = wcte_beam_hv_read( args.systemtype, args.linktype, args.arg, args.username, args.password )
        output = str(datetime.datetime.now())+' '
        for name, value in zip( names, values ):
            output+=str(value)+' '
        fileout.write(output.strip(' ')+'\n')
        sleep(60)
    fileout.close()
    print('Done.')


if __name__ == "__main__":
    main()