import subprocess
import time
import array
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read, popen

p = subprocess.Popen("bluetoothctl", stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

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
    except OSError as e:
        time.sleep(0.1)
    if '\n' in line:
        print(line,)
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

        if "DGT_BT_" in line or "PCS-REVII" in line:
            if not line.split()[3] in mac_list :
                mac_list.append(line.split()[3])
                name_list.append(line.split()[4])

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
        popen("rfcomm release 123")
        print (popen("rfcomm bind 123 "+mac_list[current]))
#        if (popen("rfcomm bind 123 "+mac_list[current])) == "":
#            print("JEEJ")
        break
#        else:
#            print("NOOOO")
        time.sleep(5)
        # if this fails try next
        state = 4
