"""
Example SYJ Scholar AI Plugin
File: plugins/example_plugin/plugin.py

Copy this directory to ~/.local/share/SYJScholarAI/plugins/my_plugin/
then restart Scholar AI to auto-load it.
"""

import typer
from rich.console import Console

PLUGIN_NAME    = "example-plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR  = "Your Name"

console = Console()


def register(app: typer.Typer) -> None:
    """Called by Scholar AI on startup to register plugin commands."""

    @app.command("hello", help="[Plugin] Example hello command.")
    def hello_cmd(
        name: str = typer.Argument("World", help="Who to greet"),
    ):
        console.print(f"[bold cyan]Hello, {name}! from the example plugin 🎉[/bold cyan]")
