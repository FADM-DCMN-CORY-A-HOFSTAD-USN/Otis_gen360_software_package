# Space Needle Otis Gen360 SCADA Framework

## Overview
This repository contains the production-grade Supervisory Control and Data Acquisition (SCADA) framework for the Seattle Center Space Needle's Otis Gen360 double-deck elevator modernization. The software replaces traditional mechanical relays with an active digital logic engine, managing kinematic physics, unequal load balancing, precipitation mass ingestion, and Modbus TCP hardware interlocks.

## Deployment Environment
For optimal stability in a production environment, deploying the core runtime on an AlmaLinux virtual machine provisioned through VMware ESXi is recommended. The application relies on continuous socket listening for hardware communication, so ensure your ConfigServer Security Firewall rules are explicitly configured to allow inbound TCP traffic on port 502.

## Installation

1. Clone this repository to your host machine.
2. Ensure Python 3.10 or higher is installed.
3. Install the required software dependencies using pip:

   pip install -r requirements.txt

   (Note: Required packages include pyModbusTCP, typer, and requests).

## Usage

### Starting the Master Controller
To launch the main SCADA engine, execute the master script from the root directory. This will spin up the Modbus TCP server, initialize the watchdog heartbeat, and begin the high-frequency 20ms industrial PLC scan cycle.

   python cli_main.py

### Generating System Documentation
This repository includes a custom command-line interface tool to automatically generate and maintain the system's technical documentation.

To initialize the documentation directory:
   python docs_cli.py init

To build the complete documentation suite (Architecture, Modbus Map, and Kinematics):
   python docs_cli.py build-all

To overwrite existing files during a rebuild, append the force flag:
   python docs_cli.py build-all --force
