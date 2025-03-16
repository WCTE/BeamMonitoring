#!/bin/bash
source ./beamline-eq-monitor/venv/bin/activate
export JAVA_HOME=/usr/lib/jvm/java-1.21.0-openjdk-amd64
export SPARK_LOCAL_IP=192.168.11.11
export LIBDAQDIR=/home/wcte/libDAQInterface
export LD_LIBRARY_PATH=/home/wcte/libDAQInterface/lib:${LD_LIBARY_PATH}
export LD_LIBRARY_PATH=${LIBDAQDIR}/Dependencies/zeromq-4.0.7/lib:${LIBDAQDIR}/Dependencies/boost_1_66_0/install/lib:${LIBDAQDIR}/Dependencies/ToolDAQFramework/lib:${LIBDAQDIR}/Dependencies/ToolFrameworkCore/lib:$LD_LIBRARY_PATH
ln -s ${LIBDAQDIR}/include .
./beamline-eq-monitor/get_beamline_values.py
