import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    help="Otis Gen360 SCADA Documentation Generator",
    add_completion=False
)

DOCS_DIR = Path("docs")

# ==========================================
# DOCUMENTATION TEMPLATES
# ==========================================
DOC_TEMPLATES = {
    "architecture": """# System Architecture
## Overview
The Space Needle Otis Gen360 digital modernization framework transitions the vertical transit system from mechanical relays to an active digital logic engine.

## Core Modules
1. **Meteorological Engine:** Ingests Elliott Bay wind shear and precipitation mass.
2. **Thermal Rail Manager:** Models induction heating and guide rail friction.
3. **Safety Subroutine Monitor:** Tracks asymmetrical load balancing.
4. **Master Orchestrator:** Modbus TCP server managing 24V I/O hardware interlocks.
""",
    "modbus_map": """# Modbus TCP Registry Map
## Coils (00001+)
* `00001`: Lower Gate Lock Solenoid
* `00002`: Upper Gate Lock Solenoid
* `00003`: Induction Thermal Relay
* `00004`: Evacuation Horn Speaker
* `00005`: Viscosity Indicator Warning Lamp

## Discrete Inputs (10001+)
* `10004`: Car-Top Maintenance Toggle
* `10006`: Crew Passenger Exit Button
* `10007`: Master Evacuation Mode Switch

## Holding Registers (40001+)
* `40001`: Target Velocity to VFD (x100)
* `40002`: Live Rail Temperature (x10)
* `40003`: Watchdog Heartbeat Counter
* `40004`: Emergency Override Key Switch
* `40005`: Lower Cabin Strain Gauges
* `40006`: Upper Cabin Strain Gauges
""",
    "kinematics": """# Kinematic & Safety Equations
## 1. Position and Velocity (Equations of Motion)
To track the dual-deck car relative to the 520-foot tower height limit:
* s(t) = s_0 + v_0t + (1/2)at^2
* v(t) = v_0 + at

## 2. Kinetic Energy Dispersal (Emergency Braking)
The force (Fb) required over a sliding distance (d) to safely dissipate the kinetic energy (Ek) of the 8000.0 kg car upon a PESSRAL actuator trip:
* Ek = (1/2)mv^2
* Fb = (mv^2) / (2d)
"""
}

# ==========================================
# CLI COMMANDS
# ==========================================

@app.command()
def init():
    """Initializes the docs directory if it does not exist."""
    # Guard clause: Check if directory already exists
    if DOCS_DIR.exists():
        typer.secho(f"Directory '{DOCS_DIR}' already exists.", fg=typer.colors.YELLOW)
        return
        
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    typer.secho(f"Successfully created '{DOCS_DIR}' directory.", fg=typer.colors.GREEN)

@app.command()
def build(doc_name: str, force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file")):
    """Generates a specific documentation file (e.g., architecture, modbus_map, kinematics)."""
    # Guard clause: Ensure docs directory exists
    if not DOCS_DIR.exists():
        typer.secho("Error: 'docs' directory missing. Run 'python docs_cli.py init' first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Guard clause: Validate requested document type
    if doc_name not in DOC_TEMPLATES:
        typer.secho(f"Error: Unknown document '{doc_name}'. Available templates: {list(DOC_TEMPLATES.keys())}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    file_path = DOCS_DIR / f"{doc_name}.md"

    # Guard clause: Prevent accidental overwrites
    if file_path.exists() and not force:
        typer.secho(f"Error: '{file_path}' already exists. Use --force to overwrite.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Write payload
    file_path.write_text(DOC_TEMPLATES[doc_name], encoding="utf-8")
    typer.secho(f"Generated documentation: {file_path}", fg=typer.colors.GREEN)

@app.command()
def build_all(force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files")):
    """Auto-generates the entire documentation suite."""
    # Guard clause: Ensure docs directory exists
    if not DOCS_DIR.exists():
        typer.secho("Error: 'docs' directory missing. Run 'python docs_cli.py init' first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo("Building all standard documentation...")
    
    for doc_name, content in DOC_TEMPLATES.items():
        file_path = DOCS_DIR / f"{doc_name}.md"
        
        # Guard clause: Skip existing files unless force is applied
        if file_path.exists() and not force:
            typer.secho(f"Skipped {file_path} (Already exists)", fg=typer.colors.YELLOW)
            continue
            
        file_path.write_text(content, encoding="utf-8")
        typer.secho(f"Created: {file_path}", fg=typer.colors.GREEN)
        
    typer.secho("Documentation build complete.", fg=typer.colors.GREEN, bold=True)

if __name__ == "__main__":
    app()
