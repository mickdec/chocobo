import sys
import subprocess
import time
import os
sys.path.insert(0, sys.path[0].replace("\\SRC\\Core\\Modules", "").replace("/SRC/Core/Modules",""))

from SRC.Core import Globals
from SRC.Core import Traversal
from SRC.Libs import LibThreading
from SRC.Libs import LibDebug
from SRC.Libs import LibTraversal

LibDebug.CheckAlexanderReq()

def menu():
    print("Welcome to Alexander")
    print("Enter you command >", end='')
    cmd = input()

    if cmd == "help" or cmd == "h":
        print("start >> start Alexander")
        print("stop >> stop Alexander")
    elif cmd == "start":
        LibDebug.Log("WORK", "Starting Alexander module..")
        try:
            process = subprocess.Popen(['node','RES/ALEXANDER/alexander.js'])
            LibTraversal.AddInstructions('Globals.Jobs.JobList.append(LibThreading.JOB("Alexander", ' + str(process.pid) + '))')
            time.sleep(1)
            LibDebug.Log("SUCCESS", "Starting Alexander module..")
        except:
            LibDebug.Log("ERROR", "Error while starting Alexander module..")
    elif cmd == "stop":
        LibDebug.Log("WORK", "Stoping Alexander module..")
        try:
            for job in Globals.Jobs.JobList:
                if "Alexander" == job.name:
                    os.kill(job.pid, 9)
                    LibTraversal.RemInstructions('Globals.Jobs.JobList.append(LibThreading.JOB("Alexander", ' + str(job.pid) + '))')
            LibDebug.Log("SUCCESS", "Stoping Alexander module..")
        except:
            LibDebug.Log("ERROR", "Error while trying to stop Alexander module..")
    exit()


menu()
