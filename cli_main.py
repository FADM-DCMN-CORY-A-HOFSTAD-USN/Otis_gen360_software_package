import time
import math

class SpaceNeedleElevator:
    def __init__(self):
        # Physical constants based on Space Needle specifications
        self.MAX_HEIGHT_FT = 520.0        # Total vertical hoistway distance
        self.MAX_SPEED_FT_S = 14.67       # ~10 mph operating speed
        self.MAX_ACCEL_FT_S2 = 4.0        # Comfort acceleration threshold
        self.EMERGENCY_TRIP_SPEED = 18.0  # Overspeed threshold trigger (ft/s)
        self.CAR_MASS_KG = 8000.0         # Estimated mass of double-deck glass car
        
        # Real-time telemetry sensors
        self.current_position = 0.0       # Feet from base station
        self.current_velocity = 0.0       # Feet per second
        self.current_acceleration = 0.0   # Feet per second squared
        self.load_lbs = 0.0
        
        # PESSRAL Safety Chain status registers
        self.safety_chain_closed = True
        self.electronic_actuator_tripped = False
        self.aro_mode_active = False       # Automatic Rescue Operation

    def update_telemetry(self, dt, requested_accel):
        """
        Main kinematic loop updating positions based on physical motion equations.
        """
        if not self.safety_chain_closed or self.electronic_actuator_tripped:
            self.apply_emergency_brakes()
            return

        # Constrain acceleration to comfort limits
        self.current_acceleration = max(min(requested_accel, self.MAX_ACCEL_FT_S2), -self.MAX_ACCEL_FT_S2)
        
        # Equation: v(t) = v0 + a*t
        self.current_velocity += self.current_acceleration * dt
        
        # Equation: s(t) = s0 + v0*t + 0.5*a*t^2
        self.current_position += (self.current_velocity * dt) + (0.5 * self.current_acceleration * (dt ** 2))
        
        # Clamp bounds to physical shaft limits
        if self.current_position >= self.MAX_HEIGHT_FT:
            self.current_position = self.MAX_HEIGHT_FT
            self.current_velocity = 0.0
        elif self.current_position <= 0:
            self.current_position = 0.0
            self.current_velocity = 0.0

        # Execute absolute positioning safety monitor checks
        self.monitor_absolute_positioning()

    def monitor_absolute_positioning(self):
        """
        Simulates the Gen360 PESSRAL digital safety chain tracking overspeed anomalies.
        """
        # Active electronic overspeed monitor check
        if abs(self.current_velocity) > self.EMERGENCY_TRIP_SPEED:
            print(f"\n[CRITICAL] ABSOLUTE POSITIONING ALARM: Overspeed detected at {abs(self.current_velocity):.2f} ft/s!")
            self.electronic_actuator_tripped = True
            self.safety_chain_closed = False

    def calculate_braking_force(self, slide_distance_m=2.0):
        """
        Calculates required emergency friction force (Newtons) based on kinetic energy dissipation.
        Equation: F = (m * v^2) / (2 * d)
        """
        # Convert velocity from ft/s to meters per second
        v_mps = self.current_velocity * 0.3048
        if v_mps == 0:
            return 0.0
        kinetic_energy = 0.5 * self.CAR_MASS_KG * (v_mps ** 2)
        required_force_n = kinetic_energy / slide_distance_m
        return required_force_n

    def apply_emergency_brakes(self):
        """
        Triggers emergency electronic actuators and logs physical braking data.
        """
        req_force = self.calculate_braking_force()
        self.current_velocity = 0.0
        self.current_acceleration = 0.0
        print(f"[SAFETY WORKFLOW] Electronic Safety Actuator Locked. Required Braking Force: {req_force:.2f} Newtons.")
        print("[SAFETY WORKFLOW] Car securely anchored to hoistway guide rails.")

    def trigger_power_loss_event(self):
        """
        Maneuver: Swaps system execution flow to Automatic Rescue Operation (ARO).
        """
        print("\n[EVENT] Main grid power loss detected at Seattle Center.")
        self.aro_mode_active = True
        print("[ARO ACTIVE] Engaging backup battery reserve. Re-routing car to nearest top-house floor deck.")
        
        # Safe, crawl-speed descent maneuver
        self.current_acceleration = -1.0
        self.current_velocity = -2.0 

# Run a test simulation iteration
if __name__ == "__main__":
    print("Initializing Seattle Center Otis Gen360 Software Package Core Emulator...")
    needle_lift = SpaceNeedleElevator()
    
    # Simulate an asset climbing the tower safely
    print("\n--- Phase 1: Normal Ascending Maneuver ---")
    for second in range(1, 6):
        needle_lift.update_telemetry(dt=1.0, requested_accel=3.5)
        print(f"Time: {second}s | Height: {needle_lift.current_position:.2f} ft | Speed: {needle_lift.current_velocity:.2f} ft/s")

    # Simulate an intentional code anomaly causing sudden overspeed
    print("\n--- Phase 2: Anomaly / Overspeed Simulation ---")
    needle_lift.update_telemetry(dt=1.0, requested_accel=15.0) # Forces a dangerous speed burst
