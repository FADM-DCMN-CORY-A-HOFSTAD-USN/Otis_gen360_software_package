"""
Univac Aegis Central Ingestion Bridge
Architecture: Otis Gen360 Elevator Telemetry Uplink
"""

import asyncio
import aiohttp
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [OTIS-AEGIS BRIDGE] | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

class OtisAegisBridge:
    def __init__(self, aegis_url: str, node_id: str = "Otis-Gen360-Car1"):
        self.aegis_url = aegis_url
        self.node_id = node_id
        self.session = None

    async def initialize(self):
        """Initializes the persistent asynchronous HTTP session."""
        timeout = aiohttp.ClientTimeout(total=3.0)
        self.session = aiohttp.ClientSession(timeout=timeout)
        logger.info(f"Bridge initialized for {self.node_id}.")
        logger.info(f"Aegis Target: {self.aegis_url}")

    async def shutdown(self):
        """Gracefully closes the network sockets."""
        if self.session:
            await self.session.close()
            logger.info("Bridge sockets closed.")

    def _map_severity(self, status: str) -> int:
        """Maps standard Otis Gen360 states to the Univac Aegis Threat Matrix."""
        status = status.upper()
        if status in ["FIRE_RECALL", "SEISMIC_STOP", "FREE_FALL_ARREST"]:
            return 10
        elif status in ["WEIGHT_OVERLOAD", "DOOR_SENSOR_FAULT"]:
            return 8
        elif status in ["MAINTENANCE_MODE", "INSPECTION"]:
            return 4
        return 0  # NORMAL, IDLE, MOVING

    async def dispatch_telemetry(self, otis_data: Dict[str, Any]):
        """
        Translates Otis Gen360 kinematics and safety states into the 
        Univac Aegis Payload Schema and dispatches it asynchronously.
        """
        if not self.session:
            return

        current_status = otis_data.get("status", "UNKNOWN")
        severity = self._map_severity(current_status)

        # Pack elevator forensics into the Raw Protocol Data string
        floor = otis_data.get("current_floor", 0)
        speed = otis_data.get("velocity_mps", 0.0)
        doors = otis_data.get("door_state", "CLOSED")
        raw_data = f"FL:{floor}|V:{speed}m/s|DR:{doors}|MODE:{current_status}"

        aegis_payload = {
            "EventId": f"OTIS-{uuid.uuid4().hex[:8].upper()}",
            "Timestamp": datetime.utcnow().isoformat() + "Z",
            "SourceNode": self.node_id,
            "EventType": f"ELEVATOR_{current_status}",
            "SeverityLevel": severity,
            "RawProtocolData": raw_data
        }

        headers = {"X-Aegis-Client": self.node_id, "Content-Type": "application/json"}

        try:
            async with self.session.post(self.aegis_url, json=aegis_payload, headers=headers) as response:
                if response.status == 200:
                    # Only log high-severity events to keep the local console clean during normal transit
                    if severity >= 4:
                        logger.info(f"Aegis Uplink Successful: {aegis_payload['EventType']}")
                else:
                    logger.warning(f"Aegis Uplink Rejected: Status {response.status}")
        except Exception as e:
            logger.error(f"Aegis Uplink Fault: {str(e)}")
