from opcua import Server


def create_server():
    server = Server()

    # Definir endpoint (pode mudar a porta se necessário)
    server.set_endpoint("opc.tcp://localhost:4840/freeopcua/server/")

    # Criar um namespace
    uri = "http://example.org/opcua/"
    idx = server.register_namespace(uri)

    # Criar um objeto no espaço de endereçamento
    tank = server.nodes.objects.add_object(idx, "Tank")

    # Criar variáveis dentro do objeto
    level = tank.add_variable(idx, "Level", 50.0)  # Inicializa em 50
    temperature = tank.add_variable(idx, "Temperature", 25.0)  # Inicializa em 25

    # Permitir escrita nas variáveis
    level.set_writable()
    temperature.set_writable()

    return server
