import asyncio
import random
from time import sleep

from opcua import Server
import time
from datetime import datetime


server = Server()
server_url = "opc.tcp://127.0.0.1:1234"
server.set_endpoint(server_url)

name = "opcuapython"
namespace = server.register_namespace(name)
node = server.get_objects_node()
param = node.add_object(namespace, "sensors")
var = param.add_variable(namespace, "Temperature", 0.0)
var.set_writable()

server.start()
print("OPC UA server started")

try:
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("OPC UA server running", current_time)
        value = var.get_value()
        time.sleep(1)

finally:
    print("Error")
