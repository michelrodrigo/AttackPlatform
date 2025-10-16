import asyncio
import random
import time

from opcua import Server

class OPCServer:
    def __init__(self):
        self.server = Server()
        self.variables = {}
        self.name = "http://industrialplant.com"
        self.url = "opc.tcp://127.0.0.1:4840"


    def start(self):
        """Initialize and start the OPC UA Server"""
        self.server.set_endpoint(self.url)
        self.namespace = self.server.register_namespace(self.name)
        node = self.server.get_objects_node()
        param = node.add_object(self.namespace, "Sensors")

        self.variables["Temperature"] = param.add_variable(self.namespace, "Temperature", 25.0)
        self.variables["Level"] = param.add_variable(self.namespace, "Level", 50.0)

        self.variables["Temperature"].set_writable()
        self.variables["Level"].set_writable()


        self.server.start()
        print("✅ OPC UA Server Started!")

        while True:
            self.update_variables()
            time.sleep(1)

    def update_variables(self):
        """Periodically update the variables"""

        new_temp = round(random.uniform(15.0, 30.0), 2)
        new_level = round(random.uniform(40.0, 60.0), 2)

        self.variables["Temperature"].set_value(new_temp)
        self.variables["Level"].set_value(new_level)

        print(f"🌡 Updated Temperature: {new_temp}°C, 📊 Level: {new_level}%")


if __name__ == "__main__":
    opc_server = OPCServer()
    opc_server.start()
