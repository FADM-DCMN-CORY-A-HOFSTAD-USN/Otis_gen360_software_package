"""
Seattle Center Space Needle Infrastructure Control Framework
File: cli_main.py
Version: 2026.1.0

Unified Engineering Blueprint for Otis Gen360 Digital Modernization.
Combines:
  1. Advanced Precipitation (Rain, Snow, Hail) Kinetic Mass Profiles
  2. Elliott Bay Wind Shear & Boundary Layer Hysteresis Scaling
  3. Unequal Load Balancing Performance Attenuation
  4. Non-Public Stop Access Filtering & Maintenance Speed Caps
  5. 24V Hardware I/O Modbus TCP Industrial Mapping Interlocks
  6. Two-Stage Secure Emergency Remote Lockdown Handling
  7. Automated Nightly Zero-Point Tare Load-Cell Recalibration
  8. Continuous Emergency Evacuation Command Routing Loops
  9. Guide Rail Thermal Modeling, Induction Heating & Lubrication Alerts
"""
import math
import time
import json
import threading
import requests
from pyModbusTCP.server import ModbusServer, DataBank

# =====================================================================
# SYSTEM STRUCTURAL CHARACTERISTICS & CONSTANTS
# =====================================================================
class SystemState:
    IDLE = 0
    RUNNING_NORMAL = 1
    HOLD_BUNCHING = 2
    HOLD_WIND = 3
    DOOR_INTERLOCKING = 4
    ALIGNMENT_MATCHING = 5
    INSPECTION_MODE = 6
    EVACUATION_MODE = 7
    CRITICAL_HALT = 8

class TowerAccessLevel:
    PUBLIC = "PUBLIC"
    MAINTENANCE = "MAINTENANCE"
    RESTRICTED_SERVICES = "RESTRICTED_SERVICES"

# =====================================================================
# CORE COMPONENT 1: METEOROLOGICAL & PRECIPITATION ENVIRONMENT ENGINE
# =====================================================================
class AdvancedWeatherProcessor:
    def __init__(self, sensor_height_m=158.5, roof_area_m2=15.0, frontal_area_m2=22.3):
        # Microclimate Ingestion Settings
        self.SENSOR_HEIGHT_M = sensor_height_m
        self.HELLMANN_EXPONENT = 0.16       # Open water urban coast drag profiles
        self.AIR_DENSITY = 1.225            # kg/m^3 sea-level standard
        self.DRAG_COEFF_CD = 1.3            # Dual-deck aerodynamic profile rectangle
        self.A_ROOF = roof_area_m2
        self.A_FRONTAL = frontal_area_m2
        
        # Precipitation Ingestion Profiles
        self.DENSITY_RAIN = 1.0
        self.DENSITY_SNOW = 0.1             # Fresh uncompressed powder
        self.DENSITY_HAIL = 0.9             # Dense ice pellets
        self.TERMINAL_VEL_RAIN = 9.0        # m/s
        self.TERMINAL_VEL_SNOW = 1.0        # m/s
        self.TERMINAL_VEL_HAIL = 20.0       # m/s
        
        # Guide Rail Friction Drop Weights
        self.MU_DRY_BASE = 1.0
        self.DROP_RAIN = 0.15
        self.DROP_SNOW = 0.45
        self.DROP_HAIL = 0.30
        
        # Wind Safety Metrics
        self.WIND_CRITICAL_MPH = 35.0
        self.HYSTERESIS_BUFFER_MPH = 4.0
        self.EMA_ALPHA = 0.15               # 10-second smoothing interval filter
        self.BETA_DAMPING = 0.04
        
        # Memory Banks
        self.smoothed_wind_mph = 0.0
        self.speed_cap_active = False

    def process_wind_telemetry(self, raw_wind_mph, car_height_m):
        """Applies an EMA filter, models Hellmann vertical shear, and checks hysteresis."""
        if self.smoothed_wind_mph == 0.0:
            self.smoothed_wind_mph = raw_wind_mph
        else:
            self.smoothed_wind_mph = (self.EMA_ALPHA * raw_wind_mph) + ((1.0 - self.EMA_ALPHA) * self.smoothed_wind_mph)
            
        z = max(1.0, min(car_height_m, self.SENSOR_HEIGHT_M))
        localized_wind_mph = self.smoothed_wind_mph * ((z / self.SENSOR_HEIGHT_M) ** self.HELLMANN_EXPONENT)
        
        if self.smoothed_wind_mph >= self.WIND_CRITICAL_MPH:
            self.speed_cap_active = True
        elif self.speed_cap_active and (self.smoothed_wind_mph < (self.WIND_CRITICAL_MPH - self.HYSTERESIS_BUFFER_MPH)):
            self.speed_cap_active = False
            
        return round(localized_wind_mph, 2), self.speed_cap_active

    def calculate_environmental_impacts(self, car_speed_mps, rain_mm_hr, snow_cm_hr, hail_mm_hr):
        """Calculates dynamic precipitation weight load (kg) and friction reduction factor."""
        rain_m_s = (rain_mm_hr / 1000.0) / 3600.0
        snow_m_s = (snow_cm_hr / 100.0) / 3600.0
        hail_m_s = (hail_mm_hr / 1000.0) / 3600.0

        mass_rain = (rain_m_s * self.A_ROOF * self.DENSITY_RAIN * 1000.0) + \
                    ((car_speed_mps / self.TERMINAL_VEL_RAIN) * rain_m_s * self.A_FRONTAL * self.DENSITY_RAIN * 1000.0)
                    
        mass_snow = (snow_m_s * self.A_ROOF * self.DENSITY_SNOW * 1000.0) + \
                    ((car_speed_mps / self.TERMINAL_VEL_SNOW) * snow_m_s * self.A_FRONTAL * self.DENSITY_SNOW * 1000.0)
                    
        mass_hail = (hail_m_s * self.A_ROOF * self.DENSITY_HAIL * 1000.0) + \
                    ((car_speed_mps / self.TERMINAL_VEL_HAIL) * hail_m_s * self.A_FRONTAL * self.DENSITY_HAIL * 1000.0)
                    
        total_weather_mass_kg = max(0.0, mass_rain + mass_snow + mass_hail)

        derated_mu = self.MU_DRY_BASE
        if rain_mm_hr > 0:  derated_mu *= (1.0 - self.DROP_RAIN)
        if snow_cm_hr > 0:  derated_mu *= (1.0 - self.DROP_SNOW)
        if hail_mm_hr > 0:  derated_mu *= (1.0 - self.DROP_HAIL)

        return round(total_weather_mass_kg, 2), round(derated_mu, 3)

# =====================================================================
# CORE COMPONENT 2: THERMAL INTERLOCK & AUTOMATED LUBRICATION MONITOR
# =====================================================================
class RailThermalManager:
    def __init__(self):
        self.RAIL_MASS_SEGMENT_KG = 120.0  
        self.SPECIFIC_HEAT_STEEL = 490.0   
        self.CRITICAL_TEMP_LUBRICATION = 55.0 
        self.FREEZING_THRESHOLD = 2.0      
        
        self.rail_temperature_c = 15.0      
        self.accumulated_friction_wear = 0.0
        self.WEAR_LIMIT_TRIGGER = 500000.0

    def compute_thermal_profile(self, dt, ambient_temp_c, car_speed_mps, imbalance_force_n, current_mu, heater_coil_on):
        """Runs the thermodynamic transient profile equation to calculate rail temperature."""
        p_induction = 1500.0 if heater_coil_on else 0.0 
        frictional_heat_w = 0.85 * imbalance_force_n * current_mu * car_speed_mps
        cooling_w = 15.0 * (self.rail_temperature_c - ambient_temp_c)
        
        net_power_w = frictional_heat_w + p_induction - cooling_w
        delta_t = (net_power_w / (self.RAIL_MASS_SEGMENT_KG * self.SPECIFIC_HEAT_STEEL)) * dt
        
        self.rail_temperature_c += delta_t
        if car_speed_mps > 0:
            self.accumulated_friction_wear += imbalance_force_n * car_speed_mps * dt

        lubrication_warning = self.rail_temperature_c >= self.CRITICAL_TEMP_LUBRICATION or self.accumulated_friction_wear >= self.WEAR_LIMIT_TRIGGER
        freeze_warning = self.rail_temperature_c <= self.FREEZING_THRESHOLD

        return round(self.rail_temperature_c, 2), lubrication_warning, freeze_warning

# =====================================================================
# CORE COMPONENT 3: SAFETY INTEGRATION SUBROUTINE MONITOR
# =====================================================================
class SafetySubroutineMonitor:
    def __init__(self):
        self.MAX_DECK_PAYLOAD_KG = 3000.0   
        self.IMBALANCE_THRESHOLD_KG = 1500.0 
        self.CRITICAL_LOCKOUT_KG = 2500.0    
        self.ATTENUATION_GAMMA = 0.5         
        self.MAX_PERMISSIBLE_DRIFT_KG = 75.0

    def evaluate_load_balance(self, lower_kg, upper_kg, normal_speed, normal_accel):
        """Verifies center of gravity offsets and scales down traction acceleration rates."""
        imbalance_delta = abs(upper_kg - lower_kg)
        
        if lower_kg > self.MAX_DECK_PAYLOAD_KG or upper_kg > self.MAX_DECK_PAYLOAD_KG:
            return False, 0.0, 0.0, "CRITICAL_OVERLOAD"
        if imbalance_delta >= self.CRITICAL_LOCKOUT_KG:
            return False, 0.0, 0.0, "CRITICAL_ASYMMETRICAL_TENSION"

        if imbalance_delta > self.IMBALANCE_THRESHOLD_KG:
            excess = imbalance_delta - self.IMBALANCE_THRESHOLD_KG
            penalty = max(0.4, 1.0 - (self.ATTENUATION_GAMMA * (excess / self.MAX_DECK_PAYLOAD_KG)))
            return True, round(normal_speed * penalty, 2), round(normal_accel * penalty, 2), "DAMPED_PROFILES"
            
        return True, normal_speed, normal_accel, "OPTIMAL_LOAD_BALANCED"

# =====================================================================
# CORE COMPONENT 4: CLOUD DATA PIPELINE OVER HTTP API
# =====================================================================
class OtisOneTelemetryStreamer:
    def __init__(self, client_id, client_secret, asset_id="SPACE-NEEDLE-LIFT-01"):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.ASSET_ID = asset_id
        self.access_token = "MOCK_CACHED_TOKEN_991144"

    def stream_telemetry(self, state_code, inspection_active, speed_mps, lower_kg, upper_kg, wind_mph):
        """Dispatches enterprise structural analytics packets up to the cloud framework."""
        payload = {
            "timestamp": int(time.time() * 1000),
            "assetId": self.ASSET_ID,
            "telemetry": {
                "operatingStateCode": int(state_code),
                "inspectionModeActive": bool(inspection_active),
                "driveSpeedMetersPerSecond": round(float(speed_mps), 2),
                "lowerDeckLoadKg": round(float(lower_kg), 1),
                "upperDeckLoadKg": round(float(upper_kg), 1),
                "windSpeedMph": round(float(wind_mph), 2)
            }
        }
        # In field deployment, connect directly via requests.post to global entry points
        return True

# =====================================================================
# MASTER INFRASTRUCTURE ORCHESTRATION COMPONENT
# =====================================================================
class SpaceNeedleMasterController:
    def __init__(self, host="0.0.0.0", port=502):
        self.server = ModbusServer(host=host, port=port, no_block=True)
        
        # 24V Hardware Modbus Map - COILS
        self.COIL_SOLENOID_LOWER = 0    # 00001: Lower Gate Lock
        self.COIL_SOLENOID_UPPER = 1    # 00002: Upper Gate Lock
        self.COIL_RAIL_HEATER = 2       # 00003: Induction Thermal relay
        self.COIL_ALARM_BUZZER = 3      # 00004: Evacuation Horn Speaker
        self.COIL_LUBRICATION_WARN = 4  # 00005: Viscosity Indicator Warning Lamp
        
        # 24V Hardware Modbus Map - DISCRETE INPUTS
        self.IN_INSPECTION_SWITCH = 3   # 10004: Car-Top Maintenance Toggle
        self.IN_DOOR_CLOSE_BUTTON = 5   # 10006: Crew Passenger Exit Button
        self.IN_EVAC_START_SWITCH = 6   # 10007: Master Evacuation Mode Switch
        
        # 24V Hardware Modbus Map - HOLDING REGISTERS
        self.REG_TARGET_VELOCITY = 0    # 40001: Velocity Target to VFD (x100)
        self.REG_RAIL_TEMP = 1          # 40002: Live Rail Temperature (x10)
        self.REG_WATCHDOG_HEARTBEAT = 2 # 40003: Watchdog Heartbeat Counter
        self.REG_EMERGENCY_LOCKDOWN = 3 # 40004: Emergency Override Key Switch
        self.REG_RAW_LOWER_LOAD = 4     # 40005: Lower Cabin Strain Gauges
        self.REG_RAW_UPPER_LOAD = 5     # 40006: Upper Cabin Strain Gauges
        
        # Topographical Mechanical Target Mapping Matrix
        self.TOWER_TOPOGRAPHY = {
            "G":  (0.0, TowerAccessLevel.PUBLIC, True),
            "M1": (30.4, TowerAccessLevel.MAINTENANCE, False),
            "M2": (61.0, TowerAccessLevel.MAINTENANCE, False),
            "L1": (152.4, TowerAccessLevel.PUBLIC, True),
            "L2": (155.45, TowerAccessLevel.RESTRICTED_SERVICES, False),
            "OD": (158.5, TowerAccessLevel.PUBLIC, True)
        }
        
        # Kinematic Boundaries
        self.HOISTWAY_HEIGHT_M = 158.5
        self.V_NORMAL_MAX = 4.47        # ~10 mph cruise speed
        self.V_INSPECTION_MAX = 1.0     # Safe crawl speed for car-top maintenance work
        self.A_NORMAL_MAX = 1.22        # Comfort acceleration threshold
        self.M_CAR_DEADWEIGHT = 8000.0
        self.NUM_ROPES = 8
        self.ROPE_DENSITY = 1.5
        
        # Sub-Module Instances
        self.weather_processor = AdvancedWeatherProcessor()
        self.rail_manager = RailThermalManager()
        self.safety_monitor = SafetySubroutineMonitor()
        self.cloud_streamer = OtisOneTelemetryStreamer("ID_9921", "SEC_4410")
        
        # Dynamic State Variables
        self.current_lower_height_m = 0.0
        self.heartbeat_counter = 0
        self.lower_deck_offset_kg = 0.0
        self.upper_deck_offset_kg = 0.0
        self.active_state = SystemState.IDLE
        self.kiosk_dispatch_matrix = {floor: [0, 0] for floor in self.TOWER_TOPOGRAPHY}

    def start_infrastructure(self):
        self.server.start()
        # Spawn the high-frequency cyclic scan thread (mimics a 20ms industrial PLC scan cycle)
        threading.Thread(target=self._run_plc_scan_cycle, daemon=True).start()
        print("[PLC ENGINE] Space Needle Control Core Server Online.")

    def shutdown_infrastructure(self):
        self.server.stop()

    def register_passenger_call(self, deck, floor):
        """Hides non-public levels from public screens and logs passenger calls to the matrix."""
        if floor in self.TOWER_TOPOGRAPHY and self.TOWER_TOPOGRAPHY[floor][2]:
            idx = 0 if deck == "lower" else 1
            self.kiosk_dispatch_matrix[floor][idx] += 1
            return True
        return False

    def execute_nightly_tare_recalibration(self):
        """Zero-Point Tare Recalibration: Checks for empty-deck sensor drift every evening."""
        raw_l_data = DataBank.get_words(self.REG_RAW_LOWER_LOAD, 1)
        raw_u_data = DataBank.get_words(self.REG_RAW_UPPER_LOAD, 1)
        
        raw_l = raw_l_data[0] if raw_l_data else 0
        raw_u = raw_u_data[0] if raw_u_data else 0
        
        if abs(raw_l) < self.safety_monitor.MAX_PERMISSIBLE_DRIFT_KG and abs(raw_u) < self.safety_monitor.MAX_PERMISSIBLE_DRIFT_KG:
            self.lower_deck_offset_kg = raw_l
            self.upper_deck_offset_kg = raw_u
            print(f"[NIGHTLY TARE] Load cells zeroed. Lower Offset: {raw_l}kg | Upper Offset: {raw_u}kg")
            return True
            
        print("[NIGHTLY TARE FAULT] Calibration aborted: Unexplained cabin weight profile detected.")
        return False

    def _run_plc_scan_cycle(self):
        """High-frequency industrial automation loop."""
        while True:
            try:
                # 1. Rolling 16-bit Heartbeat Watchdog Counter update
                self.heartbeat_counter = (self.heartbeat_counter + 1) % 65536
                DataBank.set_words(self.REG_WATCHDOG_HEARTBEAT, [self.heartbeat_counter])
                
                # 2. Check for emergency force-lockdown overrides from engineers
                lockdown_cmd = DataBank.get_words(self.REG_EMERGENCY_LOCKDOWN, 1)
                if lockdown_cmd and lockdown_cmd[0] == 9911:  # Core override PIN verification
                    self.active_state = SystemState.CRITICAL_HALT
                    self._set_gate_lockout(lock_lower=True, lock_upper=True)
                    self._write_vfd_speed(0.0)
                    time.sleep(0.02)
                    continue
                    
                # 3. Read physical car-top maintenance toggle inputs
                if DataBank.get_bits(self.IN_INSPECTION_SWITCH, 1) == [1]:
                    self.active_state = SystemState.INSPECTION_MODE
                    self.kiosk_dispatch_matrix = {f: [0, 0] for f in self.TOWER_TOPOGRAPHY} # Wipe public queues
                    self._set_gate_lockout(lock_lower=True, lock_upper=True)
                    self._write_vfd_speed(self.V_INSPECTION_MAX)
                    time.sleep(0.02)
                    continue
                    
                # 4. Check for high-priority continuous evacuation loop requests
                if DataBank.get_bits(self.IN_EVAC_START_SWITCH, 1) == [1]:
                    self.active_state = SystemState.EVACUATION_MODE
                    self._process_continuous_evacuation_loop()
                    continue
                    
                time.sleep(0.02) # Standard 20ms industrial PLC cycle sleep
            except Exception as e:
                print(f"[PLC HARDWARE ERROR] Exception in logic cycle: {e}")
                time.sleep(1.0)

    def process_standard_dispatch(self, dt, ambient_c, raw_wind_mph, rain_mm, snow_cm, hail_mm):
        """Standard runtime engine loop: Evaluates wind, weather mass, and load cells."""
        if self.active_state in [SystemState.INSPECTION_MODE, SystemState.EVACUATION_MODE, SystemState.CRITICAL_HALT]:
            return
            
        self.active_state = SystemState.RUNNING_NORMAL
        
        # A. Read load cells and subtract tared zero-drift offsets
        raw_l_data = DataBank.get_words(self.REG_RAW_LOWER_LOAD, 1)
        raw_u_data = DataBank.get_words(self.REG_RAW_UPPER_LOAD, 1)
        raw_l = raw_l_data[0] if raw_l_data else 0
        raw_u = raw_u_data[0] if raw_u_data else 0
        
        w_lower = max(0.0, raw_l - self.lower_deck_offset_kg)
        w_upper = max(0.0, raw_u - self.upper_deck_offset_kg)
        imbalance_force_n = abs(w_lower - w_upper) * 9.81
        
        # B. Check for unequal load balancing and calculate velocity caps
        is_safe, target_v, target_a = self.safety_monitor.evaluate_load_balance(
            w_lower, w_upper, self.V_NORMAL_MAX, self.A_NORMAL_MAX
        )
        if not is_safe:
            self.active_state = SystemState.CRITICAL_HALT
            self._write_vfd_speed(0.0)
            return
            
        # C. Run Elliott Bay weather processors to calculate vertical wind profiles
        local_wind, wind_cap_active = self.weather_processor.process_wind_telemetry(raw_wind_mph, self.current_lower_height_m)
        if wind_cap_active:
            self.active_state = SystemState.HOLD_WIND
            excess = max(0.0, local_wind - self.weather_processor.WIND_CRITICAL_MPH)
            target_v = min(target_v, self.V_NORMAL_MAX * math.exp(-self.weather_processor.BETA_DAMPING * excess))
            
        # D. Run rain, snow, and hail mass impact criteria matrices
        added_mass, friction_factor = self.weather_processor.calculate_environmental_impacts(
            target_v, rain_mm, snow_cm, hail_mm
        )
        if friction_factor < 0.6:
            target_v *= friction_factor
            
        # E. Calculate rope drift mass at the mid-point transit position
        hanging_rope_mass = self.NUM_ROPES * self.ROPE_DENSITY * (self.HOISTWAY_HEIGHT_M - self.current_lower_height_m)
        total_shaft_mass = self.M_CAR_DEADWEIGHT + w_lower + w_upper + added_mass + hanging_rope_mass
        
        # F. Thermodynamic rail modeling & safety processing step
        heater_active = DataBank.get_bits(self.COIL_RAIL_HEATER, 1) == [1]
        temp_reading, trig_lubrication, trig_freeze = self.rail_manager.compute_thermal_profile(
            dt, ambient_c, target_v, imbalance_force_n, friction_factor, heater_active
        )
        
        # G. Update 24V Modbus databanks and outputs
        DataBank.set_bits(self.COIL_RAIL_HEATER, [1 if trig_freeze else 0])
        DataBank.set_bits(self.COIL_LUBRICATION_WARN, [1 if trig_lubrication else 0])
        DataBank.set_words(self.REG_RAIL_TEMP, [int(temp_reading * 10)])
        self._write_vfd_speed(target_v)
        
        # H. Scan the destination matrix and execute floor-to-floor segments
        target_floor = None
        for floor, counts in self.kiosk_dispatch_matrix.items():
            if counts[0] > 0 or counts[1] > 0:
                target_floor = floor
                break
                
        if target_floor:
            self.current_lower_height_m = self.TOWER_TOPOGRAPHY[target_floor][0]
            # Clear passenger calls from the processed matrix queue segment
            self.kiosk_dispatch_matrix[target_floor] = [0, 0]
            
        # I. Stream real-time metrics up to the Otis ONE IoT Cloud platform
        self.cloud_streamer.stream_telemetry(self.active_state, False, target_v, w_lower, w_upper, local_wind)

    def _process_continuous_evacuation_loop(self):
        """Continuous Emergency Loop: Moves people out of the observation deck until stopped."""
        print("\n" + "!" * 80)
        print(" [CRITICAL PROTOCOL] CONTINUOUS OVERRIDE EVACUATION ROUTE ENGAGED ")
        print("!" * 80)
        
        DataBank.set_bits(self.COIL_ALARM_BUZZER, [1])
        
        while DataBank.get_bits(self.IN_EVAC_START_SWITCH, 1) == [1]:
            # Sortie Run Upward
            print("[EVAC CORE] Driving car up to Top House platforms...")
            self._write_vfd_speed(self.V_NORMAL_MAX)
            self._set_gate_lockout(lock_lower=True, lock_upper=True)
            time.sleep(1.0)
            
            # Arrive at Top Observation Deck, open doors, and activate buzzer alert
            print("[EVAC CORE] Top arrived. Releasing gate solenoids. Waiting for Door Close...")
            self._write_vfd_speed(0.0)
            self._set_gate_lockout(lock_lower=False, lock_upper=False)
            
            while DataBank.get_bits(self.IN_DOOR_CLOSE_BUTTON, 1) == [0]:
                time.sleep(0.05)
                if DataBank.get_bits(self.IN_EVAC_START_SWITCH, 1) == [0]: return
                
            DataBank.set_bits(self.IN_DOOR_CLOSE_BUTTON, [0]) # Reset flag button
            
            # Sortie Run Downward
            print("[EVAC CORE] Clearance received. Commencing rapid descent drop...")
            self._write_vfd_speed(self.V_NORMAL_MAX)
            self._set_gate_lockout(lock_lower=True, lock_upper=True)
            time.sleep(1.0)
            
            # Arrive at Ground Terminal and unload occupants
            print("[EVAC CORE] Ground arrived. Releasing gate solenoids. Waiting for Door Close...")
            self._write_vfd_speed(0.0)
            self._set_gate_lockout(lock_lower=False, lock_upper=False)
            
            while DataBank.get_bits(self.IN_DOOR_CLOSE_BUTTON, 1) == [0]:
                time.sleep(0.05)
                if DataBank.get_bits(self.IN_EVAC_START_SWITCH, 1) == [0]: return
                
            DataBank.set_bits(self.IN_DOOR_CLOSE_BUTTON, [0]) # Reset flag button
            
        # Stop command received from engineers; kill alarm and lock down gates safely
        DataBank.set_bits(self.COIL_ALARM_BUZZER, [0])
        self._set_gate_lockout(lock_lower=True, lock_upper=True)
        self.active_state = SystemState.IDLE

    def _write_vfd_speed(self, mps):
        DataBank.set_words(self.REG_TARGET_VELOCITY, [int(mps * 100)])

    def _set_gate_lockout(self, lock_lower, lock_upper):
        DataBank.set_bits(self.COIL_SOLENOID_LOWER, [0 if lock_lower else 1])
        DataBank.set_bits(self.COIL_SOLENOID_UPPER, [0 if lock_upper else 1])


# =====================================================================
# SYSTEM VERIFICATION AND TEST RUNNER
# =====================================================================
if __name__ == "__main__":
    # Initialize the complete master platform framework instance
    scada_system = SpaceNeedleMasterController()
    scada_system.start_infrastructure()
    
    try:
        # Mocking an asymmetrical passenger group boarding at the ground station kiosks
        DataBank.set_words(scada_system.REG_RAW_LOWER_LOAD, [2800]) # Lower deck packed
        DataBank.set_words(scada_system.REG_RAW_UPPER_LOAD, [0])    # Upper deck empty
        
        # Register destinations to the public observation deck
        scada_system.register_passenger_call("lower", "OD")
        scada_system.register_passenger_call("upper", "OD")
        
        # Test Case Validation Cycle: Severe winter storm conditions off Puget Sound
        print("\n--- Processing Runtime Framework Cycle: Wet Snow Ingestion Run ---")
        scada_system.process_standard_dispatch(
            dt=1.0, ambient_c=-1.5, raw_wind_mph=42.0, rain_mm=0.0, snow_cm=6.5, hail_mm=0.0
        )
        
    finally:
        # Gracefully stop network listeners to prevent communication port binding locks
        scada_system.shutdown_infrastructure()
        print("\n[FINALIZE] Core system environment test complete. Hardware layers halted.")
