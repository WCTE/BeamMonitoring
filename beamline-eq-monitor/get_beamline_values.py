#!/usr/bin/env python3
# import the required modules
import time
#import pyspark
#sc=pyspark.SparkContext()

#sc.setSystemProperty('kerberos.principal', 'mahartz@CERN.CH')
#sc.setSystemProperty('kerberos.keytab', '/tmp/mahartz.keytab');


from nxcals.spark_session_builder import get_or_create
from nxcals.api.extraction.data.builders import DataQuery

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import cppyy, cppyy.ll
import ctypes
import sys
sys.path.insert(0,'/home/wcte/libDAQInterface/lib')
std = cppyy.gbl.std
try:
	cppyy.load_reflection_info('libDAQInterfaceClassDict')
except:
	raise BaseException("class dictionary not found: did you run 'make python'?") from None
from cppyy.gbl import ToolFramework
from cppyy.gbl.ToolFramework import DAQInterface

class daq_interface_info:
	'''
	daq_interface_info is a class to wrap all the needed tooldaq operations
	'''
	def __init__(self, configfile='./InterfaceConfigBLEQ'):
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
			self.monitoring_data.Set(name, float(value))

		# generate a JSON from the contents
		monitoring_json = std.string("")
		self.monitoring_data.__rshift__['std::string'](monitoring_json)

		# send to the Database for plotting on the webpage
		sentData = self.daq_inter.SendMonitoringData(monitoring_json)
		if(sentData==False):
			print('send_data:',self.device_name,'failed to send data to database')


dq = daq_interface_info()

variables = ['T09.XCHV011:POS_JAW1_MEAS','T09.XCHV011:POS_JAW2_MEAS','T09.XCHV012:POS_JAW1_MEAS','T09.XCHV012:POS_JAW2_MEAS','T09.XCHV014:POS_JAW1_MEAS',
						'T09.XCHV014:POS_JAW2_MEAS','T09.XCHV015:POS_JAW1_MEAS','T09.XCHV015:POS_JAW2_MEAS','T09.XCHV026:POS_JAW1_MEAS','T09.XCHV026:POS_JAW2_MEAS',
						'T09.XCHV027:POS_JAW1_MEAS','T09.XCHV027:POS_JAW2_MEAS','T09.BHZ019:I_MEAS','T09.BHZ031:I_MEAS','T09.BVT037:I_MEAS','T09.DHZ001:I_MEAS',
						'T09.DHZ002:I_MEAS','T09.DHZ045:I_MEAS','T09.QDN012:I_MEAS','T09.QDN034:I_MEAS','T09.QDN042:I_MEAS','T09.QFN009:I_MEAS','T09.QFN016:I_MEAS',
						'T09.QFN024:I_MEAS','T09.QFN027:I_MEAS','T09.QFN039:I_MEAS','T09.TBS017:Acquisition:position',
						'T09.XCHV011:POS_JAW1_REF','T09.XCHV011:POS_JAW2_REF','T09.XCHV012:POS_JAW1_REF','T09.XCHV012:POS_JAW2_REF','T09.XCHV014:POS_JAW1_REF',
						'T09.XCHV014:POS_JAW2_REF','T09.XCHV015:POS_JAW1_REF','T09.XCHV015:POS_JAW2_REF','T09.XCHV026:POS_JAW1_REF','T09.XCHV026:POS_JAW2_REF',
						'T09.XCHV027:POS_JAW1_REF','T09.XCHV027:POS_JAW2_REF','T09.BHZ019:I_REF','T09.BHZ031:I_REF','T09.BVT037:I_REF','T09.DHZ01:I_REF',
						'T09.DHZ02:I_REF','T09.DHZ045:I_REF','T09.QDN012:I_REF','T09.QDN034:I_REF','T09.QDN042:I_REF','T09.QFN009:I_REF','T09.QFN016:I_REF',
						'T09.QFN024:I_REF','T09.QFN027:I_REF','T09.QFN039:I_REF']


spark = get_or_create("My_APP")
#spark.setSystemProperty('kerberos.principal', 'mahartz@CERN.CH')
#spark.setSystemProperty('kerberos.keytab', '/tmp/mahartz.keytab');

#startTime = datetime.datetime.now()
#runningTime = datetime.datetime.now()-startTime

while True:

  current_time = time.time_ns()
  start_time = current_time - 100000000000
  values = []
  names = []

  for var in variables:
    df1 = DataQuery.builder(spark).variables() \
      .system('CMW') \
      .nameEq(var) \
      .timeWindow(start_time, current_time) \
      .build()
    firstRow = df1.first()
    if firstRow is not None:
      values.append(firstRow[0])
      names.append(var)
      print(var,' ',firstRow[0],' ',firstRow[2])

  print(len(values),' ',len(names))

  dq.send_data( names, values )

 # runningTime = datetime.datetime.now()-startTime
 # print('Running Time',runningTime.total_hours())

  time.sleep(50)    

#exit()

