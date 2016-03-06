#!/bin/bash
################################################################
# Script Name: pico_dgt_bt
# Date: 12/29/2012
# Author: Eric Singer
# Description: Check for an rfcomm device for stockfish to use
#              If the device doesn't exist then try to create it
#---------------------------------------------------------------
# Modified on 1/26/2014 to automatically connect to the 
# Revelation II board
#===============================================================
#  Exit Codes: 0 - Bluetooth device found and configured
#              1 - No Bluetooth device found

DGT_BT_FOUND=""

####################################################################
# use the rfcomm command to see if a bluetooth device is defined ###
####################################################################
while read RFDEV RFADDR SKIP RFCHANNEL RFSTATE
do
   ####################################################
   ### See if the device is the DGT bluetooth board ###
   ####################################################
   export DGT_BT_FOUND=`/usr/bin/hcitool info ${RFADDR} | grep -E "Device Name: DGT_BT|Device Name: PCS-REVII"`
   if [[ -n ${DGT_BT_FOUND} ]]
   then
      break
   fi
done < <(/usr/bin/rfcomm)

#######################################################
### If the DGT board device is already defined exit ###
#######################################################
if [[ -n ${DGT_BT_FOUND} ]]
then
   exit 0
fi

###################################################################
### At this point there isn't any bluetooth DGT boards defined. ###
### Check to see if there's a bluetooth dongle attached ###########
###########################################################
BT_DONGLE=`/usr/sbin/hciconfig|grep "^hci"|cut -d":" -f1`

########################################
### If BT_DONGLE doesn't exist, exit ###
########################################'
if [[ -z ${BT_DONGLE} ]]
then
   exit 1
fi

########################################
### Scan for the DGT bluetooth board ###
########################################
DGT_BOARD_ADDR=`/usr/bin/hcitool scan|grep -E "DGT_BT|PCS-REVII"|awk -F' ' '{ print $1 }'`

###############################################
### If there's no DGT board found then exit ###
###############################################
if [[ -z ${DGT_BOARD_ADDR} ]]
then
   exit 1
fi

#################################
### Setup the blutooth device ###
#################################
echo "0000"|/usr/bin/bluez-simple-agent ${BT_DONGLE} ${DGT_BOARD_ADDR}

################################################
### Check to see if the device authenticated ###
################################################
TEST_DGT_AUTH=`/usr/bin/bluez-test-device list|grep DGT_BT`

###########################################################################
### If the DGT board did not authenticate, then try the revelation code ###
###########################################################################
if [[ -z ${TEST_DGT_AUTH} ]]
then
   echo "1234"|/usr/bin/bluez-simple-agent ${BT_DONGLE} ${DGT_BOARD_ADDR}
fi

############################################
### Write the bluetooth bind information ###
############################################
# Empty out file first
> /etc/bluetooth/rfcomm.conf
echo "rfcomm0 {" >> /etc/bluetooth/rfcomm.conf
echo "          bind yes;" >> /etc/bluetooth/rfcomm.conf
echo "          device ${DGT_BOARD_ADDR};" >> /etc/bluetooth/rfcomm.conf
echo "          channel 1;" >> /etc/bluetooth/rfcomm.conf
echo '          comment "DGT Bluetooth Board";' >> /etc/bluetooth/rfcomm.conf
echo "        }" >> /etc/bluetooth/rfcomm.conf

##############################################################
### Finally restart bluetooth to get the new rfcomm device ###
##############################################################
/usr/bin/rfcomm bind all
exit 0
