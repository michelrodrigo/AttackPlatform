import threading
import time
#from client import OPCUAClient
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from controller import Controller

def start_opcua_server(controller):
    controller.start()
    try:
        while True:
            controller.update()
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()

def start_dash_app():
    app = dash.Dash(__name__)

    #client = OPCUAClient("opc.tcp://localhost:4840/freeopcua/server/")

    app.layout = html.Div([
        html.H1("Industrial Tank Monitoring"),
        html.Div(id="live-update-text"),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,
            n_intervals=0
        )
    ])

    @app.callback(Output('live-update-text', 'children'),
                  Input('interval-component', 'n_intervals'))
    def update_metrics(n):
        temp, level = controller.tank_simulator.temperature, controller.tank_simulator.level#client.read_values()
        return [
            html.P(f"Temperature: {temp} °C"),
            html.P(f"Level: {level} %")
        ]

    app.run_server(debug=True)

if __name__ == "__main__":
    controller = Controller()

    server_thread = threading.Thread(target=start_opcua_server, args=(controller,))
    server_thread.daemon = True
    server_thread.start()

    time.sleep(2)
    start_dash_app()
