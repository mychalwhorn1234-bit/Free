#!/usr/bin/env python3
"""
Command-line interface for FORScan Python tools.
"""

import click
import logging
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()
logger = logging.getLogger(__name__)

try:
    from forscan import FORScanConnector, DiagnosticSession, Config
except ImportError as e:
    logger.error(f"Failed to import forscan modules: {e}")
    raise

# Constants for repeated messages
FAILED_CONNECT_MSG = "[red]✗ Failed to connect to vehicle[/red]"
FAILED_SESSION_MSG = "[red]✗ Failed to start diagnostic session[/red]"

@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """FORScan Python automation tools."""
    
    # Initialize configuration
    ctx.ensure_object(dict)
    try:
        ctx.obj['config'] = Config(config) if config else Config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        ctx.obj['config'] = Config()
    
    # Setup logging
    try:
        if verbose:
            ctx.obj['config'].update_logging_config(level='DEBUG')
        
        ctx.obj['config'].setup_logging()
    except AttributeError:
        # Fallback if methods don't exist
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)


@cli.command()
@click.option(
    '--adapter', '-a', default='ELM327', 
    help='Adapter type (ELM327, J2534, STN)'
)
@click.option('--port', '-p', default='COM1', help='Communication port')
@click.pass_context
def connect(ctx, adapter, port):
    """Connect to vehicle via specified adapter."""
    
    try:
        config = ctx.obj['config']
        
        # Update adapter configuration
        config.update_adapter_config(type=adapter, port=port)
        
        # Create connector
        connector = FORScanConnector(config.get_forscan_config())
        
        # Attempt connection
        rprint(
            f"[blue]Connecting to vehicle via {adapter} on {port}...[/blue]"
        )
        
        if connector.connect(adapter, port):
            rprint("[green]✓ Successfully connected to vehicle[/green]")
            
            # Get vehicle info
            vehicle_info = connector.get_vehicle_info()
            if vehicle_info:
                vehicle_text = (
                    f"Vehicle: {vehicle_info.year} {vehicle_info.make} "
                    f"{vehicle_info.model}"
                )
                rprint(f"[cyan]{vehicle_text}[/cyan]")
                if vehicle_info.vin:
                    rprint(f"[cyan]VIN: {vehicle_info.vin}[/cyan]")
        else:
            rprint("[red]✗ Failed to connect to vehicle[/red]")
            
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--adapter', '-a', default='ELM327', help='Adapter type')
@click.option('--port', '-p', default='COM1', help='Communication port')
@click.pass_context
def scan(ctx, adapter, port):
    """Scan for diagnostic trouble codes."""
    
    try:
        config = ctx.obj['config']
        
        # Create connector and session
        connector = FORScanConnector(config.get_forscan_config())
        session = DiagnosticSession(connector)
        
        # Connect and start session
        rprint(f"[blue]Connecting via {adapter} on {port}...[/blue]")
        
        if not connector.connect(adapter, port):
            rprint(FAILED_CONNECT_MSG)
            return
        
        if not session.start_session():
            rprint(FAILED_SESSION_MSG)
            return
        
        # Scan for DTCs
        rprint("[blue]Scanning for diagnostic trouble codes...[/blue]")
        dtcs = session.scan_dtcs()
        
        if dtcs:
            # Create table for results
            table = Table(title="Diagnostic Trouble Codes")
            table.add_column("Code", style="red")
            table.add_column("Description", style="white")
            table.add_column("Status", style="yellow")
            
            for dtc in dtcs:
                table.add_row(dtc.code, dtc.description, dtc.status)
            
            console.print(table)
            dtc_count_msg = f"Found {len(dtcs)} diagnostic trouble codes"
            rprint(f"\n[yellow]{dtc_count_msg}[/yellow]")
        else:
            rprint("[green]✓ No diagnostic trouble codes found[/green]")
        
        # End session
        session.end_session()
        connector.disconnect()
        
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--adapter', '-a', default='ELM327', help='Adapter type')
@click.option('--port', '-p', default='COM1', help='Communication port')
@click.confirmation_option(prompt='Are you sure you want to clear all DTCs?')
@click.pass_context
def clear(ctx, adapter, port):
    """Clear diagnostic trouble codes."""
    
    try:
        config = ctx.obj['config']
        
        # Create connector and session
        connector = FORScanConnector(config.get_forscan_config())
        session = DiagnosticSession(connector)
        
        # Connect and start session
        if not connector.connect(adapter, port):
            rprint(FAILED_CONNECT_MSG)
            return
        
        if not session.start_session():
            rprint(FAILED_SESSION_MSG)
            return
        
        # Clear DTCs
        rprint("[blue]Clearing diagnostic trouble codes...[/blue]")
        
        if session.clear_dtcs():
            success_msg = "Diagnostic trouble codes cleared successfully"
            rprint(f"[green]✓ {success_msg}[/green]")
        else:
            rprint("[red]✗ Failed to clear diagnostic trouble codes[/red]")
        
        # End session
        session.end_session()
        connector.disconnect()
        
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@cli.command()
@click.option(
    '--procedure', '-p', required=True, help='Service procedure name'
)
@click.option('--adapter', '-a', default='ELM327', help='Adapter type')
@click.option('--port', default='COM1', help='Communication port')
@click.pass_context
def service(ctx, procedure, adapter, port):
    """Perform service procedure."""
    
    try:
        config = ctx.obj['config']
        
        # Create connector and session
        connector = FORScanConnector(config.get_forscan_config())
        session = DiagnosticSession(connector)
        
        # Connect and start session
        if not connector.connect(adapter, port):
            rprint(FAILED_CONNECT_MSG)
            return
        
        if not session.start_session():
            rprint(FAILED_SESSION_MSG)
            return
        
        # Perform service procedure
        rprint(f"[blue]Performing service procedure: {procedure}[/blue]")
        
        if session.perform_service_procedure(procedure):
            success_msg = f"Service procedure '{procedure}' completed successfully"
            rprint(f"[green]✓ {success_msg}[/green]")
        else:
            rprint(f"[red]✗ Service procedure '{procedure}' failed[/red]")
        
        # End session
        session.end_session()
        connector.disconnect()
        
    except Exception as e:
        rprint(f"[red]Error: {e}[/red]")


@cli.command()
@click.pass_context
def info(ctx):
    """Display system and configuration information."""
    
    config = ctx.obj['config']
    
    # Create info table
    table = Table(title="FORScan Python Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    # Adapter config
    adapter_config = config.get_adapter_config()
    table.add_row("Adapter Type", adapter_config['type'])
    table.add_row("Port", adapter_config['port'])
    table.add_row("Baudrate", str(adapter_config['baudrate']))
    
    # FORScan config
    forscan_config = config.get_forscan_config()
    table.add_row("Data Directory", forscan_config['data_dir'])
    table.add_row("Config Directory", forscan_config['config_dir'])
    table.add_row("Auto Connect", str(forscan_config['auto_connect']))
    
    console.print(table)


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()