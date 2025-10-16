from opcua import Client
import logging
from utils.colors import *
from colorama import Fore, Back, Style

class OPCUAClient:
    def __init__(self, url="opc.tcp://127.0.0.1:4840"):
        self.client = Client(url)

    def connect(self):
        try:
            self.client.connect()
            print(CORA+"Conectado ao servidor OPC UA"+CEND)
        except Exception as e:
            print(CORA+f"ERRO ao conectar: {e}"+CEND)

    def disconnect(self):
        self.client.disconnect()
        print(CORA+"Desconectado do servidor OPC UA"+CEND)

    def read_value(self, node_id):
        try:
            node = self.client.get_node(node_id)
            return node.get_value()
        except Exception as e:
            print(CORA+f"Erro ao ler valor no servidor: {e}"+CEND)
            return None

    def set_value(self, node_id, value):
        try:
            node = self.client.get_node(node_id)
            if node is not None:
                node.set_value(value)
                print(f"{CORA}Valor {value} escrito no nó {node_id}{CEND}")
            else:
                print(f"{CORA}Nó {node_id} não encontrado.{CEND}")
        except Exception as e:
            print(f"{CORA}Erro ao escrever valor: {e}{CEND}")