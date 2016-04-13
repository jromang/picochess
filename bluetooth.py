#import Queue
#import threading
import subprocess
import time
from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read



#def enqueue_output(out, queue):
#    for line in iter(out.readline, b''):
#        queue.put(line)
#    out.close()

#def getOutput(outQueue):
#    outStr = ''
#    try:
#        while True: #Adds output from the Queue until it is empty
#            outStr+=outQueue.get_nowait()

#    except Queue.Empty:
#        return outStr

p = subprocess.Popen("bluetoothctl", stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

# set the O_NONBLOCK flag of p.stdout file descriptor:
flags = fcntl(p.stdout, F_GETFL) # get current p.stdout flags
fcntl(p.stdout, F_SETFL, flags | O_NONBLOCK)

#outQueue = Queue()
#outThread = Thread(target=enqueue_output, args=(p.stdout, outQueue))
#outThread.daemon = True
#outThread.start()

#line = p.stdout.readline()
#print(line)
#line = p.stdout.readline()
#print(line)
#line = p.stdout.readline()
#print(line)
#time.sleep(1)
#p.communicate(input="power on\n" )

line=""
lastmac=0
p.stdin.write("power on\n")
p.stdin.write("agent on\n")
p.stdin.flush()

while True:
    try:
        line += read(p.stdout.fileno(), 1).decode(encoding='UTF-8')
    except OSError as e:
        time.sleep(0.1)
    if '\n' in line:
        print(line,)
        if "Agent registered" in line:
            p.stdin.write("default-agent\n")
            p.stdin.flush()
            print(line,)
        if "Changing power on succeeded" in line:
            p.stdin.write("scan on\n")
            p.stdin.flush()
            break
        if "DGT_BT_" in line:
            lastmac=line.split()[3]
        line=""
while True:
    try:
        line += read(p.stdout.fileno(), 1).decode(encoding='UTF-8')
    except OSError as e:
        time.sleep(0.1)
    if '\n' in line:
        print(line,)
        if "Discovering: yes" in line:
            if lastmac:
                print("pairing to: ",lastmac)
                time.sleep(1)
                p.stdin.write("pair "+lastmac+"\n")
                p.stdin.flush()
        if "DGT_BT_" in line:
            if not lastmac == line.split()[3] :
                lastmac=line.split()[3]
                print("pairing to: ",lastmac)
                p.stdin.write("pair "+lastmac+"\n")
                p.stdin.flush()
        if "Failed to pair: org.bluez.Error.InProgress" in line:
            print("again pairing to: ",lastmac)
            time.sleep(1)
            p.stdin.write("pair "+lastmac+"\n")
            p.stdin.flush()
        line=""
    if "Enter PIN code:" in line:
        p.stdin.write("0000\n")
        p.stdin.flush()
        line=""
 

#    print("loop")
#    someInput = raw_input("Input: ")


#output = getOutput(outQueue)
