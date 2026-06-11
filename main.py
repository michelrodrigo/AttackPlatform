import threading
import time


from utils.bus import Bus
from controller import Controller
from subsystems import register_subsystems
from interface.app import run



# criar a dinâmica de temperatura.



def main():
    stop_event = threading.Event()

    # Initializes the bus
    bus = Bus()

    # Initializes the controller
    controller = Controller(bus)

    # Initializes the OPC UA server in a different thread
    opc_thread = threading.Thread(target=controller.start, name="OpcServerThread", daemon=True)
    opc_thread.start()

    # Initializes the subsystems
    subsystems = register_subsystems(controller, stop_event, bus)
    # Initializes the threads from subsystems
    for subsystem in subsystems:
        subsystem.start()

    # Waits some time to allow OPC Server to be ready
    time.sleep(3)

    # Initializes the web interface in a new thread
    ui_thread = threading.Thread(target=run, name="UIThread")
    ui_thread.start()

    try:
        # waits for the stop event
        stop_event.wait()
    except KeyboardInterrupt:
        print("Terminating...")

    # Stops all threads
    stop_event.set()
    controller.stop()
    for subsystem in subsystems:
        subsystem.join()

    print("System stopped.")

if __name__ == "__main__":
    main()



