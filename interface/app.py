import dash
from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from opcua import Client
import os
import dash_bootstrap_components as dbc
import logging
from .nodes_adresses import *
from utils.colors import *
from colorama import Fore, Back, Style
from .opc_client import OPCUAClient
import utils.simulation_params as sim_params


Interface_ON = True
simulating = False
tank_level = 50
tank_temperature = 25.0
logs = []

MAX_LEVEL_INDICATOR_HEIGHT = 190

# Set the logging level of the 'werkzeug' logger to 'ERROR'
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])



# Layout do Dash
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Simulação de Controle de Tanque", className="text-center text-primary mb-4"),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row("Interface control", style={"padding": "10px"}),
                        dbc.Button("On", id="interface_on_button", n_clicks=0, color="success", className="me-2", style={"width": "70px", "height": "40px"}),
                        dbc.Button("Off", id="interface_off_button", n_clicks=0, color="danger", style={"width": "70px", "height": "40px"}),
                        dbc.Row("Simulation", style={"padding": "10px"}),
                        dbc.Button("Start", id="start-button", n_clicks=0, color="success", className="me-2", style={"width": "70px", "height": "40px"}),
                        dbc.Button("Stop", id="stop-button", n_clicks=0, color="danger", style={"width": "70px", "height": "40px"}),
                        dbc.Button("Reset", id="reset-button", n_clicks=0, color="danger", style={"width": "70px", "height": "40px"}),
                        # Nova linha para o controle de velocidade
                        dbc.Row("Simulation Speed", style={"padding": "10px"}),
                        dcc.Slider(
                            id="speed-slider",
                            min=1,
                            max=15,
                            step=1,
                            marks=None,
                            value = sim_params.DELTA_T,  # Velocidade inicial
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                        dbc.Row("Input Valve", style={"padding": "10px"}),
                        dbc.Button("Open", id="input_valve_open_button", n_clicks=0, color="success", className="me-2", style={"width": "70px", "height": "40px"}),
                        dbc.Button("Close", id="input_valve_close_button", n_clicks=0, color="danger", style={"width": "70px", "height": "40px"}),
                        dbc.Row("Output Valve", style={"padding": "10px"}),
                        dbc.Button("Open", id="output_valve_open_button", n_clicks=0, color="success", className="me-2", style={"width": "70px", "height": "40px"}),
                        dbc.Button("Close", id="output_valve_close_button", n_clicks=0, color="danger", style={"width": "70px", "height": "40px"}),
                        html.Div(id="action-feedback", className="mt-3 text-info"),

                    ],
                    width=2,
                ),
                dbc.Col([


                    dbc.Row([
                        dbc.Alert("⚠️ Nível atingiu 100%!", id='tank_overflow_alert', color='danger', is_open=False)
                    ]),
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.Iframe(src="assets/background1.html", width="100%", height="500px", style={"border": "none"}),
                                html.Div(
                                    id="level-indicator",
                                    style={
                                        "width": "20px",
                                        "height": "0px",
                                        "background-color": "blue",
                                        "position": "absolute",
                                        "left": "150px",
                                        "bottom": "200px",
                                    },
                                ),
                                html.Div(
                                    id="level-border",
                                    style={
                                        "width": "20px",
                                        "height": f"{MAX_LEVEL_INDICATOR_HEIGHT}px",
                                        "color": "black",
                                        "position": "absolute",
                                        "left": "150px",
                                        "bottom": "200px",
                                        "border": "1px solid black"
                                    },
                                ),
                                # Circle that represents the Low Level Discrete sensor
                                html.Div(
                                    id="low-level-circle",
                                    style={
                                        "width": "15px",
                                        "height": "15px",
                                        "border-radius": "50%",
                                        "background-color": "red",  # Initial color: red (closed)
                                        "position": "absolute",
                                        "left": "170px",  # Adjust
                                        "bottom": "320px",   # Adjust
                                    }
                                ),
                                # Circle that represents the High Level Discrete sensor
                                html.Div(
                                    id="high-level-circle",
                                    style={
                                        "width": "15px",
                                        "height": "15px",
                                        "border-radius": "50%",
                                        "background-color": "red",  # Initial color: red (closed)
                                        "position": "absolute",
                                        "left": "170px",  # Adjust
                                        "top": "155px",  # Adjust
                                    }
                                ),
                                # Circle that represents the Extra High Level Discrete sensor
                                html.Div(
                                    id="xhigh-level-circle",
                                    style={
                                        "width": "15px",
                                        "height": "15px",
                                        "border-radius": "50%",
                                        "background-color": "red",  # Initial color: red (closed)
                                        "position": "absolute",
                                        "left": "170px",  # Adjust
                                        "top": "140px",  # Adjust
                                    }
                                ),
                                html.Div(
                                    id="temperature-display",
                                    children="Temp: 25 °C",
                                    style={
                                        "position": "absolute",
                                        "top": "20px",
                                        "left": "100px",
                                        "color": "black",
                                        "font-weight": "bold",
                                    },
                                ),
                                # Circle that represents the input valve
                                html.Div(
                                    id="input-valve-circle",
                                    style={
                                        "width": "25px",
                                        "height": "25px",
                                        "border-radius": "50%",
                                        "background-color": "red",  # Initial color: red (closed)
                                        "position": "absolute",
                                        "left": "40px",  # Adjust
                                        "top": "60px",   # Adjust
                                    }
                                ),
                                # Circle that represents the output valve
                                html.Div(
                                    id="output-valve-circle",
                                    style={
                                        "width": "25px",
                                        "height": "25px",
                                        "border-radius": "50%",
                                        "background-color": "red",  # Initial color: red (closed)
                                        "position": "absolute",
                                        "left": "250px",  # Adjust
                                        "top": "315px",   # Adjust
                                    }
                                )
                            ]
                        ),
                        className="mb-4",
                    )],
                    width=8,
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.Div(id="debug-output", style={"margin-top": "10px", "font-weight": "bold"}),
                    html.H3("Logs da Simulação", className="mt-4"),
                    html.Pre(
                        id="logs",
                        style={
                            "height": "200px",
                            "overflow": "auto",
                            "border": "1px solid black",
                            "padding": "10px",
                        },
                    ),
                ],
                width=12,
            )
        ),
        # Interval for controlling interface update
        dcc.Interval(id="interval-component", interval=800, disabled=True),
        dcc.Store(id="interface-state", data=True),  # True means that interface starts running.
        html.Div(id="dummy-output", style={"display": "none"}),
        html.Div(id="dummy-output2", style={"display": "none"})
    ],
    fluid=True,

)


@app.callback(
    Output("dummy-output", "children"),
    Input("speed-slider", "value")
)
def update_speed(new_speed):
    sim_params.DELTA_T = new_speed
    print(f"{CRED}Simulation speed (DELTA_T) updated to: {new_speed}{CEND}")
    return f"Speed updated to {new_speed}"



# Callback to monitor input and output valve related buttons and to send corresponding message to OPC server
@app.callback(
    Output("dummy-output2", "children"),
    [Input('reset-button', "n_clicks")]
)
def reset_simulation(n_clicks_reset):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Identifies which button was clicked
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    print(CRED+"Clicked button: "+CEND, button_id)

    if button_id == "reset-button":
        try:
            # Updates the OPC UA node to open input valve (True value)
            client.set_value(simulation_reset_node_address, True)
            return "Simulation Reset."
        except Exception as e:
            return f"Error while resetting simulation: {e}"

# Callback to monitor input and output valve related buttons and to send corresponding message to OPC server
@app.callback(
    Output("action-feedback", "children"),
    [Input('input_valve_open_button', "n_clicks"),
     Input('input_valve_close_button', "n_clicks"),
     Input('output_valve_open_button', "n_clicks"),
     Input('output_valve_close_button', "n_clicks")]
)
def control_input_valve(n_clicks_open_input, n_clicks_close_input, n_clicks_open_output, n_clicks_close_output):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Identifies which button was clicked
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    print(CRED+"Clicked button: "+CEND, button_id)

    if button_id == "input_valve_open_button":
        try:
            # Updates the OPC UA node to open input valve (True value)
            client.set_value(input_valve_open_node_address, True)
            return "Input Valve opened."
        except Exception as e:
            return f"Error while opening Input Valve: {e}"
    elif button_id == "input_valve_close_button":
        try:
            # Updates the OPC UA node to close input valve (False value)
            client.set_value(input_valve_close_node_address, True)
            return "Input Valve closed."
        except Exception as e:
            return f"Error while closing Input Valve : {e}"
    elif button_id == "output_valve_open_button":
        try:
            # Updates the OPC UA node to open output valve (False value)
            client.set_value(output_valve_open_node_address, True)
            return "Output Valve opened."
        except Exception as e:
            return f"Error while opening Output Valve : {e}"
    elif button_id == "output_valve_close_button":
        try:
            # Updates the OPC UA node to close output valve (False value)
            client.set_value(output_valve_close_node_address, True)
            return "Output Valve closed."
        except Exception as e:
            return f"Error while closing Output Valve : {e}"
    return "No action."

@app.callback(
    Output('tank_overflow_alert', 'is_open'),
    Input('interval-component', 'n_intervals')
)
def tank_overflow_alert(n):
    overflow = client.read_value(tank_overflow)
    #print("Tank overflow: ", overflow)
    return bool(overflow)

# Callback to updated extra high level sensor status through OPC UA
@app.callback(
    Output("xhigh-level-circle", "style"),
    Input("interval-component", "n_intervals"),
)
def update_extra_high_level_sensor(n_intervals):
    try:
        # Reads valve status
        sensor_state = client.read_value(extra_high_level)
    except Exception as e:
        print(f"Error while reading valve status: {e}")
        sensor_state = False

    # If valve is open, its color is set to green, otherwise is set to red
    color = "green" if sensor_state else "red"

    # Defines the style for position, changing only the color
    return {
        "width": "15px",
        "height": "15px",
        "border-radius": "50%",
        "background-color": color,
        "position": "absolute",
        "left": "170px",
        "top": "140px",
    }

# Callback to updated high level sensor status through OPC UA
@app.callback(
    Output("high-level-circle", "style"),
    Input("interval-component", "n_intervals"),
)
def update_high_level_sensor(n_intervals):
    try:
        # Reads valve status
        sensor_state = client.read_value(high_level)
    except Exception as e:
        print(f"Error while reading valve status: {e}")
        sensor_state = False

    # If valve is open, its color is set to green, otherwise is set to red
    color = "green" if sensor_state else "red"

    # Defines the style for position, changing only the color
    return {
        "width": "15px",
        "height": "15px",
        "border-radius": "50%",
        "background-color": color,
        "position": "absolute",
        "left": "170px",
        "top": "155px",
    }


# Callback to updated low level sensor status through OPC UA
@app.callback(
    Output("low-level-circle", "style"),
    Input("interval-component", "n_intervals"),
)
def update_low_level_sensor(n_intervals):
    try:
        # Reads valve status
        sensor_state = client.read_value(low_level)
    except Exception as e:
        print(f"Error while reading valve status: {e}")
        sensor_state = False

    # If valve is open, its color is set to green, otherwise is set to red
    color = "green" if sensor_state else "red"

    # Defines the style for position, changing only the color
    return {
        "width": "15px",
        "height": "15px",
        "border-radius": "50%",
        "background-color": color,
        "position": "absolute",
        "left": "170px",
        "top": "320px",
    }



# Callback to updated input valve status through OPC UA
@app.callback(
    Output("input-valve-circle", "style"),
    Input("interval-component", "n_intervals"),
)
def update_input_valve(n_intervals):
    try:
        # Reads valve status
        valve_state = client.read_value(input_valve_node_address)
    except Exception as e:
        print(f"Error while reading valve status: {e}")
        valve_state = False

    # If valve is open, its color is set to green, otherwise is set to red
    color = "green" if valve_state else "red"

    # Defines the style for position, changing only the color
    return {
        "width": "25px",
        "height": "25px",
        "border-radius": "50%",
        "background-color": color,
        "position": "absolute",
        "left": "40px",  # Ajuste conforme necessário
        "top": "60px",   # Ajuste conforme necessário
    }

# Callback to updated output valve status through OPC UA
@app.callback(
    Output("output-valve-circle", "style"),
    Input("interval-component", "n_intervals"),
)
def update_output_valve(n_intervals):
    try:
        # Reads valve status
        valve_state = client.read_value(output_valve_node_address)
    except Exception as e:
        print(f"Error while reading valve status: {e}")
        valve_state = False

    # If valve is open, its color is set to green, otherwise is set to red
    color = "green" if valve_state else "red"

    # Defines the style for position, changing only the color
    return {
        "width": "25px",
        "height": "25px",
        "border-radius": "50%",
        "background-color": color,
        "position": "absolute",
        "left": "250px",  # Adjust
        "top": "315px",   # Adjust
    }

@app.callback(
    Output("debug-output", "children"),
    [Input("interface_on_button", "n_clicks"),
     Input("interface_off_button", "n_clicks")]
)
def test_callback(n_clicks_on, n_clicks_off):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "Nenhum botão pressionado ainda."

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return f"Botão pressionado: {button_id}"

@app.callback(
    [Output("start-button", "disabled"),
     Output("stop-button", "disabled"),
     Output("interface_on_button", "disabled"),
     Output("interface_off_button", "disabled"),
     Output("interface-state", "data")],  # Armazena o estado da interface
    [Input("interface_on_button", "n_clicks"),
     Input("interface_off_button", "n_clicks")],
    [State("interface-state", "data")]
)
def toggle_interface(start_clicks, stop_clicks, interface_on):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    #print(f"Botão pressionado: {button_id}")

    if button_id == "interface_on_button":
        interface_on = True
        #print(colored("Interface LIGADA.", interface_text_color))
    elif button_id == "interface_off_button":
        interface_on = False
        #print(colored("Interface DESLIGADA.", interface_text_color))

    # Atualiza apenas os botões e o estado da interface.
    return (
        not interface_on,  # Iniciar: desabilitado se interface off
        not interface_on,  # Parar: desabilitado se interface off
        interface_on,      # Botão On: desabilitado se interface já ligada
        not interface_on,  # Botão Off: desabilitado se interface já desligada
        interface_on       # Atualiza o estado da interface
    )


@app.callback(
    Output("interval-component", "disabled"),
    [Input("start-button", "n_clicks"),
     Input("stop-button", "n_clicks")],
    [State("interface_off_button", "disabled")]
)
def toggle_simulation(start_clicks, stop_clicks, interface_disabled):
    global simulating

    # Se a interface estiver desligada, não processa os cliques dos botões de simulação
    if interface_disabled:
        raise dash.exceptions.PreventUpdate

    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"{CRED}Simulação: botão pressionado: {button_id}{CEND}")

    if button_id == "start-button":
        simulating = True
        client.set_value(simulation_running_address, True)
        return False  # Habilita o dcc.Interval (simulação ativa)
    elif button_id == "stop-button":
        simulating = False
        client.set_value(simulation_stop_address, True)
        return True   # Desabilita o dcc.Interval (simulação pausada)


# Callback para atualizar o tanque e logs
@app.callback(
    [Output("level-indicator", "style"),
     Output("temperature-display", "children"),
     Output("logs", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_simulation(n_intervals):
    global simulating, tank_level, tank_temperature, logs

    if not simulating:
        raise dash.exceptions.PreventUpdate

    # Atualização das variáveis
    #tank_level += 0.5  # Simulando aumento no nível
    new_tank_level = client.read_value(level_node_address)
    if new_tank_level is not None:
        tank_level = new_tank_level
    tank_level = min(100, tank_level)

    new_temperature = client.read_value(temperature_node_address)  # Ler do OPC UA
    if new_temperature is not None:
        tank_temperature = new_temperature
    tank_temperature = min(100, tank_temperature)

    # Atualizar nível do tanque
    level_height = MAX_LEVEL_INDICATOR_HEIGHT * (tank_level / 100)
    level_style = {
        "width": "20px",
        "height": f"{level_height}px",
        "background-color": "blue",
        "position": "absolute",
        "left": "150px",  # Ajuste conforme necessário
        "bottom": "200px",   # Ajuste conforme necessário
    }

    # Atualizar temperatura no texto
    temperature_text = f"Temp: {tank_temperature:.2f} °C"

    # Adicionando log
    logs.append(f"Nível: {tank_level:.2f} L, Temperatura: {tank_temperature:.2f} °C")
    if len(logs) > 10:
        logs.pop(0)

    return level_style, temperature_text, "\n".join(logs)

# Inicialização
def run():
    print(CRED+"Inicializando cliente OPC UA"+CEND)
    global client
    client = OPCUAClient()
    client.connect()
    app.run_server(debug=False)

if __name__ == "__main__":
    run()
