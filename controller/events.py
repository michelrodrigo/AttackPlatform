from automata_tool.automata import Event

# Events related to the Input Valve
e_open_input_valve = Event("open_input_valve", controllable=True)
e_close_input_valve = Event("close_input_valve", controllable=True)

# Events related to the Output Valve
e_open_output_valve = Event("open_output_valve", controllable=True)
e_close_output_valve = Event("close_output_valve", controllable=True)

# Events related to the Level Sensor
e_low_level_trigger = Event("low_level_t", controllable=False)
e_high_level_trigger = Event("high_level_t", controllable=False)
e_extra_high_level_trigger = Event("extra_high_level_t", controllable=False)

e_low_level_reset = Event("low_level_r", controllable=False)
e_high_level_reset = Event("high_level_r", controllable=False)
e_extra_high_level_reset = Event("extra_high_level_r", controllable=False)

# Events related to the Simulation Control
e_sim_running = Event("simulation_running", controllable=False)
e_sim_stop = Event("simulation_stop", controllable=False)
e_sim_reset = Event("simulation_reset", controllable=False)

# Reset Event
e_rst = Event("rst", controllable=False)


commands2events = {
    "Input Valve Open": e_open_input_valve,
    "Input Valve Close": e_close_input_valve,
    "Output Valve Open": e_open_output_valve,
    "Output Valve Close": e_close_output_valve,
    "Simulation Running": e_sim_running,
    "Simulation Stop": e_sim_stop,
    "Simulation Reset": e_sim_reset
}


signals2events = {
    "Low Level"
}

