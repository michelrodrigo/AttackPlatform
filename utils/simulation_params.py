# System constants
C = 4186  # Water Specific Heat (J/(kg·°C))
RHO = 1000  # Water Density (kg/m³)
H = 10  # Thermal exchange coeficient (W/(m²·°C))
A_T = 0.2  # Area of tank base (m²)
AREA_THERMAL_EXCHANGE = 2.0  # Area fo thermal exchange (m²)
T_ENV = 25.0  # Environment temperature (°C)

# System variables
initial_tank_level = 0  # Initial tank level (m)
tank_temperature = 25.0  # Initial tank temperature (°C)
heater_power = 0.0  # Heater power (W)
input_flow = 0.1#0.01  # Water input flow (m³/s)
output_flow = 0.02  # Water input flow (m³/s)
input_temperature = 20.0  # Temperature of water  (°C)

LL = 1 # Discrete Level Sensor - Low Level setting (%)
LH = 95 # Discrete Level Sensor - High Level setting (%)
LHH = 100 # Discrete Level Sensor - Extra High Level setting (%)

DELTA_T = 1  # time interval (s)

print_input_valve = True
print_output_valve = True
print_mixer = True
print_heater = False
