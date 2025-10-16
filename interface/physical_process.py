import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from threading import Thread
import time
import os

# Inicializando a aplicação Dash
app = dash.Dash(__name__)
app.title = "Simulação com Tanque em SVG"

# Caminho para o arquivo HTML do SVG
svg_path = os.path.join(os.getcwd(), f"assets", "background1.html")

# Layout da aplicação
app.layout = html.Div([
    html.H1("Simulação de Controle de Tanque", style={'text-align': 'center'}),

    # Contêiner com o tanque e controles sobrepostos
    html.Div([
        # Tanque SVG incorporado via Iframe
        html.Div([
            html.Iframe(
                src=f"assets/background1.html",
                id="svg-container",
                style={"width": "100%", "height": "100%", "border": "none", "position": "relative", "align": "center"}
            ),
            # Indicador de nível dinâmico
            html.Div(
                id="level-indicator",
                style={
                    "width": "20px",
                    "height": "10px",  # Inicia vazio
                    "background-color": "blue",
                    "position": "absolute",
                    "left": "500px",  # Ajuste conforme o tanque no SVG
                    "bottom": "160px"  # Alinha com a base do tanque

                }
            ),
            # Display da temperatura
            html.Div(
                id="temperature-display",
                children="Temp: 25 °C",
                style={
                    "position": "absolute",
                    "top": "20px",
                    "left": "100px",
                    "color": "black",
                    "font-weight": "bold"
                }
            )
        ], style={"position": "relative", "width": "100%", "height": "500px", "margin": "auto"}),

        # Botões de controle
        html.Div([
            html.Button("Iniciar", id="start-button", n_clicks=0),
            html.Button("Parar", id="stop-button", n_clicks=0, style={"margin-left": "10px"}),
        ], style={"text-align": "center", "margin-top": "20px"}),
    ], style={"text-align": "center"}),

    # Logs da simulação
    html.Div([
        html.H3("Logs da Simulação"),
        html.Pre(id="logs",
                 style={"height": "200px", "overflow": "auto", "border": "1px solid black", "margin": "20px auto",
                        "width": "300px"})
    ]),

    # Intervalo para atualizações automáticas
    dcc.Interval(
        id="interval-component",
        interval=1000,  # Intervalo em milissegundos (1 segundo)
        n_intervals=0  # Contador de intervalos, atualizado automaticamente
    )


])

# Variáveis de simulação
tank_level = 0
tank_temperature = 25
simulating = False
logs = []


# Thread de simulação
def simulation_thread():
    global tank_level, tank_temperature, simulating, logs
    while simulating:
        # Atualização das variáveis
        tank_level += 5  # Simulando um pequeno aumento
        tank_temperature += 0.05
        tank_level = min(100, tank_level)
        tank_temperature = min(100, tank_temperature)

        # Adicionando log
        logs.append(f"Nível: {tank_level:.2f} L, Temperatura: {tank_temperature:.2f} °C")
        if len(logs) > 10:
            logs.pop(0)

        time.sleep(1)


# Callback para iniciar/parar a simulação
@app.callback(
    Output("interval-component", "disabled"),
    [Input("start-button", "n_clicks"),
     Input("stop-button", "n_clicks")]
)
def toggle_simulation(start_clicks, stop_clicks):
    global simulating
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # Identificar qual botão foi clicado
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "start-button":
        simulating = True
        return False  # Habilita o `dcc.Interval`
    elif button_id == "stop-button":
        simulating = False
        return True  # Desabilita o `dcc.Interval`


# Callback para atualizar o tanque e logs
@app.callback(
    [Output("level-indicator", "style"),
     Output("temperature-display", "children"),
     Output("logs", "children")],
    [Input("interval-component", "n_intervals")]
)
def update_simulation(n_intervals):
    global tank_level, tank_temperature, logs

    if not simulating:
        raise dash.exceptions.PreventUpdate

    # Atualização das variáveis
    tank_level += 0.1  # Simulando um pequeno aumento
    tank_temperature += 0.05
    tank_level = min(100, tank_level)
    tank_temperature = min(100, tank_temperature)

    # Atualizar o nível do tanque
    level_height = 300 * (tank_level / 100)  # Altura proporcional ao nível
    level_style = {
        "width": "20px",
        "height": f"{level_height}px",
        "background-color": "blue",
        "position": "absolute",
        "left": "500px",  # Ajuste conforme o tanque no SVG
        "bottom": "160px"
    }

    # Atualizar temperatura no texto
    temperature_text = f"Temp: {tank_temperature:.2f} °C"

    # Adicionando log
    logs.append(f"Nível: {tank_level:.2f} L, Temperatura: {tank_temperature:.2f} °C")
    if len(logs) > 10:
        logs.pop(0)

    return level_style, temperature_text, "\n".join(logs)


# Executando a aplicação
if __name__ == "__main__":
    app.run_server(debug=True)