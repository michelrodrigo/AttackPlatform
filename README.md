# AttackPlatform Architecture

## Overview

The AttackPlatform simulates an industrial control system (ICS) composed of:

- Human Machine Interface (HMI)
- OPC UA communication
- Supervisory Controller
- Discrete Event System (DES) automata
- Industrial communication bus
- Sensors and actuators
- Physical process dynamics

---

## System Architecture

```mermaid
flowchart TD

    UI[Dash HMI Interface]

    OPC_CLIENT[OPC UA Client]

    CONTROLLER[Controller<br/>Supervisory Control]

    OPC_SERVER[OPC UA Server]

    SUPERVISOR[Supervisor Automata]

    QUEUE[Command Queue]

    BUS[Industrial Message Bus]

    IV[Input Valve]
    OV[Output Valve]
    LD[Level Dynamics]
    LS[Level Sensor]

    UI --> OPC_CLIENT

    OPC_CLIENT --> OPC_SERVER

    OPC_SERVER --> CONTROLLER

    CONTROLLER --> SUPERVISOR

    SUPERVISOR --> QUEUE

    QUEUE --> BUS

    BUS --> IV
    BUS --> OV
    BUS --> LD
    BUS --> LS

    IV --> LD
    OV --> LD

    LD --> LS

    LS --> BUS

    BUS --> CONTROLLER
```

---

## Command Flow

```mermaid
sequenceDiagram

    participant User
    participant HMI
    participant OPC
    participant Controller
    participant Supervisor
    participant Bus
    participant InputValve

    User->>HMI: Click "Open Input Valve"

    HMI->>OPC: Write command

    OPC->>Controller: OPC UA update

    Controller->>Supervisor: Check event feasibility

    Supervisor-->>Controller: Event accepted

    Controller->>Bus: Publish event

    Bus->>InputValve: e_open_input_valve

    InputValve->>InputValve: Update automaton state

    InputValve->>InputValve: Set flow rate
```

---

## Physical Process Flow

```mermaid
flowchart LR

    IV[Input Valve Flow]
    OV[Output Valve Flow]

    LD[Level Dynamics]

    LS[Level Sensor]

    IV --> LD
    OV --> LD

    LD --> LS
```

---

## Measurement Flow

```mermaid
sequenceDiagram

    participant Dynamics
    participant Sensor
    participant Bus
    participant Controller
    participant OPC
    participant HMI

    Dynamics->>Sensor: Level update

    Sensor->>Bus: Measurement

    Bus->>Controller: Level information

    Controller->>OPC: Update OPC nodes

    OPC->>HMI: Read values

    HMI->>HMI: Refresh visualization
```

---

## Reset Flow

```mermaid
sequenceDiagram

    participant HMI
    participant Controller
    participant Bus
    participant Devices
    participant Sensor

    HMI->>Controller: e_reset

    Controller->>Bus: Broadcast reset

    Bus->>Devices: Reset event

    Devices->>Devices: Reset internal states

    Sensor->>Bus: Publish current level

    Bus->>Controller: Updated measurement

    Controller->>HMI: Update interface
```