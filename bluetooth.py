import subprocess
import time
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read

p = subprocess.Popen("bluetoothctl", stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

# set the O_NONBLOCK flag of p.stdout file descriptor:
flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)

line = ""
lastmac = ""
lastname = ""
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
            if not lastmac == line.split()[3] :
                lastmac=line.split()[3]
                lastname=line.split()[4]

        line=""

    if "Enter PIN code:" in line:
        if "DGT_BT_" in lastname:
            p.stdin.write("0000\n")
            p.stdin.flush()
        if "PCS-REVII" in lastname:
            p.stdin.write("1234\n")
            p.stdin.flush()
        line=""

    if "Confirm passkey" in line:
        p.stdin.write("yes\n")
        p.stdin.flush()
        line=""

    if state == 4:
        if lastmac:
            state = 5
            print("pairing to: ",lastmac,lastname)
            p.stdin.write("pair "+lastmac+"\n")
            p.stdin.flush()

    if state == 6:
        # now try rfcomm
        print("JEEJ")
        time.sleep(5)
        # if this fails try next
        state = 4
