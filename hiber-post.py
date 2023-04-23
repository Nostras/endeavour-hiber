#!/usr/bin/env python3
import subprocess, os, math, time

tmpFn = "/tmp/thom-hiber-py"

def run(runCmd):
    output = []
    with subprocess.Popen([runCmd], stdout=subprocess.PIPE, shell=True) as proc:
        print('EXEC: ' + runCmd)
        read = proc.stdout.read().decode('utf-8')
        if(read == ''):
            pass
        else:
            print(read)
            output.extend(read.split('\n'))
    return output

def step():
    run('sudo swapoff /hibfile')
    run('sudo rm /hibfile')
    run('sudo fallocate -l 33G /hibfile')
    run('sudo chmod 600 /hibfile')
    run('sudo mkswap /hibfile')
    run('sudo swapon /hibfile')
    resumeOffset = run('sudo swap-offset /hibfile')[0].split(' ')[3]
    uuid = run('findmnt -no UUID -T /hibfile')[0]
    run('sudo update-grub')
    fstab = run('sudo cat /etc/fstab')
    if 'hibfile' not in '\t'.join(fstab):
        run('echo "/hibfile swap swap defaults 0 0" | sudo tee -a /etc/fstab')
    print('Done')

def hibernate():
    run('sudo systemctl hibernate')

def getStatus():
    status = None
    if(os.path.exists(tmpFn)):
        with open(tmpFn) as file:
            status = file.read()
    return status

def updateStatus(toWrite):
    with open(tmpFn, 'w') as file:
        file.write(str(toWrite))

def removeStatusIfPresent():
    if(os.path.exists(tmpFn)):
        run(tmpFn)

status = getStatus()

if status == None:
    print('No tmp file found, assuming this is the first attempt')
    # Check if we truly failed the last time
    hiberResult = run('sudo systemctl status hibernate.target')[-2]
    if 'failed' in hiberResult:
        # We truly failed and got invoked by the post recover
        updateStatus(1)
        step()
        hibernate()
    else:
        # Nothing then, this is a good post result
        removeStatusIfPresent()

if status != None:
    if("1" in status):
        updateStatus(2)