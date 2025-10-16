from opcua import Server
from opcua.crypto import uacrypto, security_policies
import random
import os

class TankSimulator:
    def __init__(self):
        self.temperature = 25.0
        self.level = 50.0

    def update_values(self):
        self.temperature += random.uniform(-0.5, 0.5)
        self.level += random.uniform(-1, 1)
        self.temperature = max(20.0, min(self.temperature, 30.0))
        self.level = max(0.0, min(self.level, 100.0))

class Controller:
    def __init__(self):
        self.server = Server()
        self.tank_simulator = TankSimulator()

        # Configuração do servidor OPC UA
        self.server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        idx = self.server.register_namespace(uri)

        # get Objects node, this is where we should put our nodes
        objects = self.server.get_objects_node()

        # populating our address space
        self.myobj = objects.add_object(idx, "MyObject")
        self.myvar = self.myobj.add_variable(idx, "MyVariable", 6.7)
        self.myvar.set_writable()  # Set MyVariable to be writable by clients

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop()

    def update(self):
        self.tank_simulator.update_values()
        temp = self.tank_simulator.temperature
        self.myvar.set_value(temp)
