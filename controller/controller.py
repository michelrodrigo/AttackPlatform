import threading
import queue
import logging
import time



import random
from .automata_plants import *
from .opc_server import OpcServer
from automata_tool.supervisory_control import SupervisoryControl
from utils.colors import *
from utils.simulation_params import *




def print_transitions(automaton):
    for (s, e), value in automaton.transitions.items():
        print(f"{CGREEN}{s.name}->{e.name}->{value.name}{CEND}")

class Controller:
    def __init__(self, bus):
        """
        Initializes the controller with reference to the bus

        Args:
            bus (Bus): Communication bus shared between subsystems
        """
        self.name = "Controller"

        self.bus = bus # communication between controller and subsystems
        self.opc_server = OpcServer() # communication between controller and interface

        # Threads and communication queues.
        self.running = True
        self.threads = []
        self.message2bus_queue = queue.Queue()

        self.bus2controller = self.bus.register(self.name) # subscribes the controller in the bus

        # Flag that indicates that if the simulation is running
        self.simulation_running = False


        # Variables with status for the graphic display of elements
        self.input_valve_open = False
        self.input_valve_command = False

        self.output_valve_open = False
        self.output_valve_command = False

        self.low_level_sensor = False
        self.high_level_sensor = False
        self.extra_high_level_sensor = False

        self.tank_overflow = False

        # Process variables
        self.level = 0

        # Defines the automata for the supervisory control
        self.supervisory_control = SupervisoryControl(mode="manual")
        self.supervisory_control.add_automaton("Input Valve", InputValve(self))
        self.supervisory_control.add_automaton("Output Valve", OutputValve(self))
        self.supervisory_control.add_automaton("Low Level Sensor", LowLevelSensor(self))
        self.supervisory_control.add_automaton("High Level Sensor", HighLevelSensor(self))
        self.supervisory_control.add_automaton("Extra High Level Sensor", ExtraHighLevelSensor(self))
        self.supervisory_control.add_automaton("Simulation Control", SimulationControl(self))

    def start(self):
        """Starts the controller threads"""
        # Starts the OPC server
        self.opc_server.start()
        print(f"{CGREEN}OPC UA Server Initialized{CEND}")

        # Initializes controller threads
        self.threads.append(threading.Thread(target=self.listen_to_bus, name="BusListener"))
        self.threads.append(threading.Thread(target=self.listen_to_opc, name="OpcListener"))
        self.threads.append(threading.Thread(target=self.update_opc, name="OpcUpdater"))
        self.threads.append(threading.Thread(target=self.update_commands, name="CommandUpdater"))

        for thread in self.threads:
            thread.start()


    #def simulate(self):
    #    # Atualizar os valores de temperatura e nível com base na lógica de simulação
    #    new_temp = round(random.uniform(15.0, 30.0), 2)
    #    new_level = round(random.uniform(40.0, 60.0), 2)
    #    self.opc_server.variables["Temperature"].set_value(new_temp)
    #    self.opc_server.variables["Level"].set_value(new_level)
    #    print(f"{CGREEN}🌡 Updated Temperature: {new_temp}°C, 📊 Level: {new_level}%{CEND}")


    def stop(self):
        """Finishes the controller and its threads"""
        self.running = False
        for thread in self.threads:
            thread.join()
        self.opc_server.stop()
        print(f"{CGREEN}Controller finished.{CEND}")

    def update_commands(self):
        """Takes the commands in the queue of commands to be sent and send them through the bus"""
        while self.running:
            try:
                cmd = self.message2bus_queue.get(timeout=1)
                if cmd:
                    message = {
                        "source": "Controller",
                        "type": "command",
                        "data": commands2events.get(cmd)
                    }
                    self.bus.send_message(message)

                    event = message["data"]
                    print(f"{CGREEN2}Message sent through the bus: {CEND}"
                          f"source={message['source']} "
                          f"type={message['type']} "
                          f"event={event.name}")

            except queue.Empty:
                pass



    def listen_to_bus(self):
        """
        Listens to the bus to receive messages sent by the subsystems
        """
        while self.running:
            try:
                # Waits for notification of new message
                if self.bus.wait_for_new_message(self.name, timeout=1):  # Timeout avoids blocking
                    messages = self.bus.get_messages(self.name)
                    for message in messages:
                        self.process_bus_message(message)
                time.sleep(1)
            except Exception as e:
                print(f"{CGREEN}Error while listening to the bus: {e}{CEND}")


    def process_bus_message(self, message):
        """
        Process messages received through the bus
        
        Args:
            message (dict): Message in the format {"source": str, "type": str, "data": any}.
        """
        source = message.get("source")
        msg_type = message.get("type")
        data = message.get("data")

        if msg_type == "alarm":
            print(f"{CGREEN}Alarm received from {source}: {data}{CEND}")
        elif msg_type == "status_update":
            print(f"{CGREEN}Status update from {source}: {data}{CEND}")
        elif msg_type == "variable_update":
            print(f"{CGREEN}State {source}: {data}{CEND}")
            if source == "LevelSensor":
                self.level = data
        elif msg_type == "discrete_event":
            print(f"{CGREEN}Event from {source}: {data.name}{CEND}")
        #else:
            #print(f"Mensagem desconhecida: {message}")

        if source == "LevelSensor" and msg_type == "discrete_event":
            ev = data

            automata = self.supervisory_control.find_automata_with_event(ev)

            for a in automata:
                print(f"{CSUP}Automaton {a.name}{CEND}")
                print(f"{CGREEN}Is feasible: {a.is_feasible(ev)}{CEND}")
                if a.is_feasible(ev):
                    a.trigger_event(ev)
                    #self.message2bus_queue.put(cmd)


    def listen_to_opc(self):
        """
        Monitors changes in the variables from OPC UA and process commands.
        """

        while self.running:
            commands = self.opc_server.get_commands()

            if commands:
                print(f"{CSERV}Commands: {commands}{CEND}")

            for cmd, value in commands.items():

                if value:

                    ev = commands2events.get(cmd)
                    automata = self.supervisory_control.find_automata_with_event(ev)

                    for a in automata:
                        print(f"{CSUP}Automaton {a.name}{CEND}")
                        print(f"{CGREEN}Is feasible: {a.is_feasible(ev)}{CEND}")
                        if a.is_feasible(ev):
                            a.trigger_event(ev)
                            self.message2bus_queue.put(cmd)



            #for var_name, var in self.variables.items():
             #   try:
             #       current_value = var.get_value()
             #   except Exception as e:
             #       print(f"Erro ao ler {var_name}: {e}")
             #       continue

              #  if var_name not in last_values or last_values[var_name] != current_value:
              #      last_values[var_name] = current_value
              #      self.handle_opc_change(var_name, current_value)


            # Verificar alterações nas válvulas
            #self.input_valve_open = self.variables["Input Valve"].get_value()
            #print(self.input_valve_open)
            #output_valve = self.output_valve_node.get_value()

            # Enviar comandos ao barramento
            #if input_valve:
             #   message = {"source": "Controller", "type": "command", "data": "open_input_valve"}
             #   self.bus.send_message(message)

            #if output_valve:
            #    message = {"source": "Controller", "type": "command", "data": "open_output_valve"}
            #    self.bus.send_message(message)

            #print("executing....")
            time.sleep(0.5)

    def handle_opc_change(self, var_name, new_value):
        """
        Processa a mudança de valor de uma variável OPC UA e dispara o evento correspondente.
        """
        #print(f"Variável {var_name} mudou para {new_value}")
        # Exemplo: Se a variável for "Input Valve", dispara o comando correspondente
        if var_name == "Input Valve":
            if new_value:
                event = e_open_input_valve
            else:
                event = e_close_input_valve
            #message = {"source": "Controller", "type": "command", "data": event}
            #self.bus.send_message(message)
            print(f"{CGREEN}evento {event} recebido.{CEND}")
        # Você pode adicionar outras condições para outras variáveis, se necessário.

    def update_opc(self):
        """
        Atualiza o servidor OPC UA com informações do barramento.
        """
        while self.running:
            #level = self.request_subsystem_state("LevelTransmitter")
            #temperature = self.request_subsystem_state("TemperatureTransmitter")
            new_temp = round(random.uniform(15.0, 30.0), 2)
            new_level = self.level #round(random.uniform(40.0, 60.0), 2)

            if new_level is not None:
                self.opc_server.variables["Level"].set_value(new_level)

            if new_temp is not None:
                self.opc_server.variables["Temperature"].set_value(new_temp)

            if new_level >= 100:
                self.opc_server.variables["Tank Overflow"].set_value(True)
                automata = self.supervisory_control.find_automata_with_event(e_sim_stop)
                cmd = "Simulation Stop"
                for a in automata:
                    if a.is_feasible(e_sim_stop):
                        a.trigger_event(e_sim_stop)
                        self.message2bus_queue.put(cmd)
            else:
                self.opc_server.variables["Tank Overflow"].set_value(False)


            time.sleep(0.5)

    def request_subsystem_state(self, subsystem):
        """
        Consulta o estado de um subsistema enviando uma solicitação no barramento.

        Args:
            subsystem (str): Nome do subsistema a ser consultado.

        Returns:
            any: Valor do estado retornado pelo subsistema.
        """
        # Envia solicitação para o subsistema
        request_message = {"source": "Controller", "type": "state_request", "data": subsystem}
        self.bus.send_message(request_message)

        # Aguarda a resposta
        start_time = time.time()
        while time.time() - start_time < 1.0:  # Timeout de 1 segundo
            if self.bus.wait_for_new_message(timeout=0.1):
                messages = self.bus.get_messages()
                for response_message in messages:
                    if (
                        response_message.get("source") == subsystem
                        and response_message.get("type") == "state_response"
                    ):
                        return response_message.get("data")
        print(f"{CGREEN}Timeout ao consultar estado do subsistema {subsystem}.{CEND}")
        return None

    def open_input_valve(self):
        self.input_valve_open = True
        self.opc_server.variables["Input Valve"].set_value(self.input_valve_open)

    def close_input_valve(self):
        self.input_valve_open = False
        self.opc_server.variables["Input Valve"].set_value(self.input_valve_open)

    def open_output_valve(self):
        self.output_valve_open = True
        self.opc_server.variables["Output Valve"].set_value(self.output_valve_open)

    def close_output_valve(self):
        self.output_valve_open = False
        self.opc_server.variables["Output Valve"].set_value(self.output_valve_open)

    def trigger_low_level_sensor(self):
        self.low_level_sensor = True
        self.opc_server.variables["LowLevel"].set_value(self.low_level_sensor)

    def reset_low_level_sensor(self):
        self.low_level_sensor = False
        self.opc_server.variables["LowLevel"].set_value(self.low_level_sensor)

    def trigger_high_level_sensor(self):
        self.high_level_sensor = True
        self.opc_server.variables["HighLevel"].set_value(self.high_level_sensor)

    def reset_high_level_sensor(self):
        self.high_level_sensor = False
        self.opc_server.variables["HighLevel"].set_value(self.high_level_sensor)

    def trigger_extra_high_level_sensor(self):
        self.extra_high_level_sensor = True
        self.opc_server.variables["ExtraHighLevel"].set_value(self.extra_high_level_sensor)

    def reset_extra_high_level_sensor(self):
        self.extra_high_level_sensor = False
        self.opc_server.variables["ExtraHighLevel"].set_value(self.extra_high_level_sensor)

    def start_simulation(self):
        self.simulation_running = True
        self.opc_server.variables["Simulation Reset"].set_value(False)
        #self.opc_server.variables["ExtraHighLevel"].set_value(self.extra_high_level_sensor)

    def stop_simulation(self):
        self.simulation_running = False
        #self.opc_server.variables["ExtraHighLevel"].set_value(self.extra_high_level_sensor)

    def reset_simulation(self):
        self.simulation_running = False
        self.opc_server.variables["Simulation Reset"].set_value(True)