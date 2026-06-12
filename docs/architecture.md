# System Architecture

## Overview
The Space Needle Otis Gen360 digital modernization framework is a Python-based SCADA (Supervisory Control and Data Acquisition) system. It transitions the tower's vertical transit infrastructure from traditional mechanical relays to an active, predictive digital logic engine. 

The master controller runs a high-frequency cyclic scan loop (mimicking a 20ms industrial PLC cycle) to continuously evaluate kinematic physics, environmental factors, and load cell telemetry before dispatching commands to the physical 24V hardware.

## Core Modules

### 1. AdvancedWeatherProcessor (Meteorological Engine)
Calculates real-time environmental impacts on the glass cabs and hoistway.
* **Wind Shear Modeling:** Utilizes the Hellmann exponential law to calculate localized wind speeds at the car's exact altitude, applying an Exponential Moving Average (EMA) filter to raw telemetry.
* **Hysteresis Scaling:** Enforces a 35-mph speed-cap threshold with a 4-mph hysteresis buffer to prevent erratic speed toggling during Elliott Bay storm gusts.
* **Precipitation Kinetic Mass:** Ingests rain, snow, and hail data to calculate the added kinetic mass of water or ice accumulating on the cab roofs and frontal areas.
* **Friction Derating:** Dynamically reduces the traction friction coefficient ($\mu$) based on precipitation type to accurately scale safe braking distances.

### 2. RailThermalManager (Thermodynamic Interlock)
Monitors the physical condition of the hoistway guide rails.
* **Thermal Modeling:** Computes the transient thermodynamic heat building up on the steel rails due to high-speed friction and ambient cooling.
* **Induction Heating:** Actively triggers the 24V induction heater coils if the rail temperature drops below the 2.0°C freezing threshold.
* **Automated Lubrication Warning:** Tracks accumulated friction wear and temperature to trigger viscosity warning lamps if the rails exceed the 55.0°C critical lubrication limit.

### 3. SafetySubroutineMonitor (Load Balancing)
Audits the mechanical strain placed on the hoistway cables by the double-deck cabs.
* **Asymmetrical Tension Attenuation:** Evaluates load-cell data across both the upper and lower passenger decks. If the imbalance exceeds the 1500.0 kg threshold, the engine automatically attenuates the motor's maximum acceleration and velocity profiles.
* **Critical Lockout:** Instantly halts the system if the load imbalance exceeds 2500.0 kg or if either deck exceeds the 3000.0 kg structural payload limit.

### 4. SpaceNeedleMasterController (Modbus TCP Orchestrator)
The industrial networking bridge that links the Python logic to the physical tower hardware.
* **I/O Mapping:** Maps the calculated digital logic to standard holding registers (40001+) and coils (00001+) to command Variable Frequency Drive (VFD) motor speeds and fire physical gate solenoids.
* **Watchdog Heartbeat:** Runs an independent background thread that constantly ticks a dedicated register (40003). If the network drops, the physical PLCs will sense the frozen heartbeat and immediately drop the 24V relays to fail-secure the turnstiles.
* **Destination Matrix:** Replaces standard up/down buttons with a topographical destination matrix, filtering out restricted maintenance levels (M1, M2, L2) from public boarding screens.

### 5. OtisOneTelemetryStreamer (Cloud Data Pipeline)
Dispatches structural analytics and system states via HTTP over the Otis ONE IoT framework, streaming drive speeds, deck loads, and active wind constraints to off-site cloud dashboards.

## System State Machine
The core engine routes through explicit, numbered operational states to guarantee execution safety:
* `STATE 0`: **IDLE** (Standing by at berth)
* `STATE 1`: **RUNNING_NORMAL** (Executing matrix dispatches)
* `STATE 2`: **HOLD_BUNCHING** (Dynamic headway delay active)
* `STATE 3`: **HOLD_WIND** (Elliott Bay wind shear constraints active)
* `STATE 4`: **DOOR_INTERLOCKING** (Securing 24V gate solenoids)
* `STATE 5`: **ALIGNMENT_MATCHING** (Matching structural targets)
* `STATE 6`: **INSPECTION_MODE** (Car-top maintenance; speed capped to 1.0 m/s)
* `STATE 7`: **EVACUATION_MODE** (Continuous top-to-bottom rapid extraction loop)
* `STATE 8`: **CRITICAL_HALT** (Emergency override or absolute load failure)
