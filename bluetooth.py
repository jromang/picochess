import subprocess
import time
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read
import os.path

import sys
if not os.path.exists("/usr/bin/bluetoothctl"):
    sys.exit()

if os.path.exists("/dev/rfcomm123"):
    print("release 123")
    subprocess.call(["rfcomm","release","123"])

p = subprocess.Popen("/usr/bin/bluetoothctl", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)

# set the O_NONBLOCK flag of p.stdout file descriptor:
flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)

line = ""
current = -1
mac_list = []
name_list = []

state = 0
p.stdin.write("power on\n")
p.stdin.flush()

while True:
    try:
        line += read(p.stdout.fileno(), 1).decode(encoding='UTF-8')
        time.sleep(0.001)
    except OSError as e:
        time.sleep(0.1)
    if '\n' in line:
        print(line,end="")
        if "Changing power on succeeded" in line:
            state = 1
            p.stdin.write("agent on\n")
            p.stdin.flush()
        if "Agent registered" in line:
            state = 2
            p.stdin.write("default-agent\n")
            p.stdin.flush()
        if "Default agent request successful" in line:
            state = 3
            p.stdin.write("scan on\n")
            p.stdin.flush()
        if "Discovering: yes" in line:
            state = 4
        if "Pairing successful" in line:
            state = 6
        if "Failed to pair: org.bluez.Error.AlreadyExists" in line:
            state = 6
        elif "Failed to pair" in line:
            # try the next
            state = 4
        if  "not available" in line:
            # remove and try the next
            state = 4
            mac_list.remove(mac_list[current])
            name_list.remove(name_list[current])
            print(name_list)
            current -= 1

        if ("DGT_BT_" in line or "PCS-REVII" in line) and "NEW" in line:
            if not line.split()[3] in mac_list :
                mac_list.append(line.split()[3])
                name_list.append(line.split()[4])
                print(name_list)


        line=""

    if "Enter PIN code:" in line:
        if "DGT_BT_" in name_list[current]:
            p.stdin.write("0000\n")
            p.stdin.flush()
        if "PCS-REVII" in name_list[current]:
            p.stdin.write("1234\n")
            p.stdin.flush()
        line=""

    if "Confirm passkey" in line:
        p.stdin.write("yes\n")
        p.stdin.flush()
        line=""

    if state == 4:
        if len(mac_list) > 0:
            state = 5
            current += 1
            if current >= len(mac_list):
                current = 0
            print("pairing to: ",mac_list[current],name_list[current])
            p.stdin.write("pair "+mac_list[current]+"\n")
            p.stdin.flush()

    if state == 6:
        # now try rfcomm
        state = 7
        print("rfcomm connect")
        rfcomm = subprocess.Popen("rfcomm connect 123 "+mac_list[current], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    if state == 7:
        if os.path.exists("/dev/rfcomm123"):
            print("JEEJ connected to: ",mac_list[current],name_list[current])
            break
        if (rfcomm.poll() != None):
            p.stdin.write("remove "+mac_list[current]+"\n")
            mac_list.remove(mac_list[current])
            name_list.remove(name_list[current])
            print(name_list)
            current -= 1
            p.stdin.flush()
            print("removed, try the next")
            state = 4
        else:
            print(end=".",flush=True)
            time.sleep(0.1)
            
p.stdin.write("quit\n")
p.stdin.flush()
