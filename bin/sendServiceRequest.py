#!/soft/python3/bin/python3
import socket
import json
import sys
if len(sys.argv) < 2:
    exit(0)
hote = socket.gethostname()
port = 18502
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    socket.connect((hote, port))
except Exception as err:
    print("Unable to TCP connect "+hote+" on port "+str(port))
    print(str(err))
    exit(1)

jSonSerialized = ""
jsonRequest = {"metrixServiceRequest":
               {
                   "operation": sys.argv[1],
               }
               }
if len(sys.argv) > 2:
    jsonRequest["metrixServiceRequest"]["data"] = sys.argv[2]

try:
    jSonSerialized = json.JSONEncoder().encode(jsonRequest)
except Exception as err:
    print("Error while serializing json request :"+str(e))
    exit(1)
print("Sending  :"+jSonSerialized)
try:
    socket.send(bytes(jSonSerialized, "utf-8"))
except Exception as err:
    print("Unable to send TCP message to "+hote+" on port "+str(port))
    print(str(err))
    exit(1)
try:
    answer = socket.recv(8*1024)
except Exception as err:
    print("Error while receiving TCP message from "+hote)
    print(str(err))
    exit(1)
print("Received :"+answer.decode("utf-8")+"\n")
socket.close()
