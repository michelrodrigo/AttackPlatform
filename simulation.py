import time
import random

def simulation_process(conn):
    # Constantes do sistema
    C = 4186  # Calor específico da água (J/(kg·°C))
    RHO = 1000  # Densidade da água (kg/m³)
    H = 10  # Coeficiente de troca térmica (W/(m²·°C))
    A_T = 0.2  # Área da base do tanque (m²)
    AREA_TROCA_TERMICA = 2.0  # Área de troca térmica (m²)
    T_AMB = 25.0  # Temperatura ambiente (°C)

    # Variáveis do sistema
    nivel_tanque = 0  # Nível inicial do tanque (m)
    initial_temperature = 25.0  # Temperatura inicial do tanque (°C)
    potencia_aquecedor = 0.0  # Potência do aquecedor (W)
    vazao_entrada = 0.0  # Vazão de entrada de água (m³/s)
    temperatura_entrada = 20.0  # Temperatura da água de entrada (°C)

    delta_t = 1  # Intervalo de tempo (s)


    level = 00  # Initial level
    running = False
    input_valve_open = False
    output_valve_open = False
    heater_on = False

    print("RUNNING...")

    while True:
        # Verifica se há mensagens recebidas da interface
        if conn.poll():
            message = conn.recv()

            if message["type"] == "event":
                if message["value"] == "START":
                    running = True
                    print("Simulação iniciada.")
                elif message["value"] == "STOP":
                    running = False
                    print("Simulação parada.")
                elif message["value"] == "OPEN_INPUT_VALVE":
                    input_valve_open = True
                    print("Válvula de entrada aberta.")
                elif message["value"] == "CLOSE_INPUT_VALVE":
                    input_valve_open = False
                    print("Válvula de entrada fechada.")
                elif message["value"] == "OPEN_OUTPUT_VALVE":
                    output_valve_open = True
                    print("Válvula de saída aberta.")
                elif message["value"] == "CLOSE_OUTPUT_VALVE":
                    output_valve_open = False
                    print("Válvula de saída fechada.")
                elif message["value"] == "TURN_ON_HEATER":
                    heater_on = True
                    print("Aquecedor ligado.")
                elif message["value"] == "TURN_OFF_HEATER":
                    heater_on = False
                    print("Aquecedor desligado.")
                elif message["value"] == "EXIT":
                    print("Encerrando processo de simulação.")
                    break
            if message["type"] == "control":
                if message["variable"] == "speed":
                    delta_t = message["value"]


        # Atualiza os valores se a simulação estiver em execução
        if running:
            if input_valve_open:
                vazao_entrada = 0.001

            else:
                vazao_entrada = 0

            if output_valve_open:
                vazao_saida = 0.002
            else:
                vazao_saida = 0

            if heater_on:
                potencia_aquecedor = 200000
            else:
                potencia_aquecedor = 0

            # Calcula o nível do tanque
            nivel_tanque += delta_t * (vazao_entrada - vazao_saida) / A_T
            if nivel_tanque < 0:
                nivel_tanque = 0  # Impede nível negativo

            # Calcula massa e dinâmica da temperatura
            volume_tanque = nivel_tanque * A_T
            massa = volume_tanque * RHO  # Massa da água no tanque (kg)

            # Modelo de temperatura
            ganho_aquecedor = potencia_aquecedor / (massa * C) if massa > 0 else 0
            perda_ambiente = (H * AREA_TROCA_TERMICA * (temperatura_tanque - T_AMB)) / (
                        massa * C) if massa > 0 else 0
            efeito_entrada = (vazao_entrada * RHO * C * (temperatura_entrada - temperatura_tanque)) / (
                        massa * C) if massa > 0 else 0

            # Atualiza a temperatura
            temperatura_tanque += delta_t * (ganho_aquecedor - perda_ambiente + efeito_entrada )

            print(temperatura_tanque, ganho_aquecedor, perda_ambiente, efeito_entrada, nivel_tanque, delta_t * (ganho_aquecedor - perda_ambiente + efeito_entrada), massa)

            # Limita os valores para evitar inconsistências
            #level = max(0, min(level, 100))
            temperatura_tanque = max(0, min(temperatura_tanque, 500))


        # Envia os valores para a interface
        conn.send({"level": nivel_tanque, "temperature": temperatura_tanque, "input_valve": input_valve_open, "output_valve": output_valve_open})

        # Espera 1 segundo antes de atualizar novamente
        time.sleep(1)
