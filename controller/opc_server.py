from opcua import Server

class OpcServer:
    def __init__(self):
        self.opc_server = Server()
        self.opc_server.set_endpoint("opc.tcp://127.0.0.1:4840")
        self.opc_server.set_server_name("OPC UA Server")

        self.variables = {}

        # Configurar namespace
        self.uri = "http://industrialplant.com"
        self.idx = self.opc_server.register_namespace(self.uri)

        # Criar o nó principal
        self.node = self.opc_server.get_objects_node()
        self.sensors_node = self.node.add_object(self.idx, "Sensors")
        self.commands_node = self.node.add_object(self.idx, "Commands")
        self.status_node = self.node.add_object(self.idx, "Status")
        #self.simulation_control = self.node.add_object(self.idx, "SimulationControl")

        self.variables["Simulation Running"] = self.commands_node.add_variable(self.idx, "Simulation Running", False)
        self.variables["Simulation Stop"] = self.commands_node.add_variable(self.idx, "Simulation Stop", False)

        self.variables["Temperature"] = self.sensors_node.add_variable(self.idx, "Temperature", 25.0)
        self.variables["Level"] = self.sensors_node.add_variable(self.idx, "Level", 50.0)

        self.variables["Input Valve Open"] = self.commands_node.add_variable(self.idx, "Input Valve Open", False)
        self.variables["Input Valve Close"] = self.commands_node.add_variable(self.idx, "Input Valve Close", False)

        self.variables["Output Valve Open"] = self.commands_node.add_variable(self.idx, "Output Valve Open", False)
        self.variables["Output Valve Close"] = self.commands_node.add_variable(self.idx, "Output Valve Close", False)

        self.variables["Input Valve"] = self.status_node.add_variable(self.idx, "Input Valve", False)
        self.variables["Output Valve"] = self.status_node.add_variable(self.idx, "Output Valve", False)

        self.variables["LowLevel"] = self.sensors_node.add_variable(self.idx, "LowLevel", False)
        self.variables["HighLevel"] = self.sensors_node.add_variable(self.idx, "HighLevel", False)
        self.variables["ExtraHighLevel"] = self.sensors_node.add_variable(self.idx, "ExtraHighLevel", False)

        self.variables["Tank Overflow"] = self.status_node.add_variable(self.idx, "Tank Overflow", False)

        self.variables["Simulation Reset"] = self.commands_node.add_variable(self.idx, "Simulation Reset", False)

        self.variables["Mixer"] = self.status_node.add_variable(self.idx, "Mixer", False)
        self.variables["Mixer On"] = self.commands_node.add_variable(self.idx, "Mixer On", False)
        self.variables["Mixer Off"] = self.commands_node.add_variable(self.idx, "Mixer Off", False)

        self.variables["Heater"] = self.status_node.add_variable(self.idx, "Heater", False)
        self.variables["Heater On"] = self.commands_node.add_variable(self.idx, "Heater On", False)
        self.variables["Heater Off"] = self.commands_node.add_variable(self.idx, "Heater Off", False)
        self.variables["Heater Power"] = self.sensors_node.add_variable(self.idx, "Heater Power", 0)

        # Permitir escrita para variáveis que podem ser controladas
        for var_name, var in self.variables.items():
            var.set_writable()

        #print("✅ OPC UA Server Started!")
        #self.opc_server.start()

    def update_variable(self, name, value):
        """
        Atualiza o valor de uma variável no servidor OPC UA.
        """
        self.variables[name] = value
        print(f"Variável {name} atualizada para {value}")

    def get_commands(self):
        """
        Lê os comandos enviados pela interface via OPC UA.
        Retorna um dicionário onde a chave é o nome do comando e o valor é o comando.
        Após ler o comando, ele é opcionalmente resetado para False.
        """
        commands = {}
        try:
            # Para cada nó de comando sob o objeto "Commands"
            for cmd_node in self.commands_node.get_children():
                cmd_name = cmd_node.get_browse_name().Name  # Ex: "OpenInputValve"
                #print(cmd_name)
                value = cmd_node.get_value()
                #print(value)
                # Se o comando estiver ativado (por exemplo, True ou diferente do valor padrão)
                if value not in [None, False]:
                    commands[cmd_name] = value
                    # Opcional: resetar o comando para o valor padrão
                    cmd_node.set_value(False)
        except Exception as e:
            print(f"Erro ao ler comandos OPC UA: {e}")
        return commands

    def start(self):
        self.opc_server.start()

    def stop(self):
        self.opc_server.stop()

