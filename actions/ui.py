# -*- coding: utf-8 -*-
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box

console = Console(force_terminal=True, color_system="auto")

LOGO = r"""
██████╗ ██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗     ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗██║████╗  ██║    ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██████╔╝██║   ██║   ██║   ██║██████╔╝██║██╔██╗ ██║    ██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██╗██║   ██║   ██║   ██║██╔══██╗██║██║╚██╗██║    ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██████╔╝██║   ██║   ╚██████╔╝██║  ██║██║██║ ╚████║    ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""


def print_banner():
    panel = Panel(
        Text.from_markup(
            f"[bold yellow]{LOGO}[/]\n\n"
            "[bold white]MULTI-THREAD ADDRESS & SEED SCANNER[/]\n"
            "[dim]Bitcoin  |  Proxy Rotation  |  Bulk Check  |  Windows[/]"
        ),
        box=box.ROUNDED,
        border_style="yellow",
        padding=(0, 2),
        title="[bold white on yellow] BITCOIN-CRACKER [/]",
        title_align="center",
    )
    console.print(panel)


def show_menu_table(menu_items: list) -> str:
    console.print()
    console.print(Rule("[bold yellow]MENU[/]", style="yellow"))
    table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="dim",
        box=box.SIMPLE,
        expand=True,
    )
    table.add_column("[#]", style="bold", justify="center", width=4)
    table.add_column("Action", style="green")
    table.add_column("Description", style="dim")

    for key, action, desc in menu_items:
        table.add_row(key, action, desc)

    console.print(table)
    return console.input("\n[bold yellow]Select action [#]: [/]").strip()


def show_load_status_table(config: dict):
    console.print()
    console.print(Rule("[bold yellow]STATUS[/]", style="yellow"))
    table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="dim",
        box=box.SIMPLE,
    )
    table.add_column("Parameter", style="green")
    table.add_column("Value", justify="center")
    table.add_column("Status", justify="center", style="bold")

    proxy_cfg = config.get("proxies", {})
    proxy_enabled = proxy_cfg.get("enabled", True)
    proxy_count = len(proxy_cfg.get("proxy_list", []))
    scanner_cfg = config.get("scanner", {})
    threads = scanner_cfg.get("threads", 20)
    seed_file = config.get("seed_checker", {}).get("seed_file", "seeds.txt")

    table.add_row("Proxies", f"{proxy_count} loaded", "[green]ENABLED[/]" if proxy_enabled else "[red]DISABLED[/]")
    table.add_row("Threads", str(threads), "[green]READY[/]")
    table.add_row("Seed File", seed_file, "[green]OK[/]" if os.path.exists(seed_file) else "[red]MISSING[/]")
    table.add_row("RPC", config.get("rpc_endpoints", {}).get("bitcoin", "N/A"), "[green]CONFIGURED[/]")

    console.print(table)
    console.print()


def show_address_result_table(rows: list):
    console.print()
    console.print(Rule("[bold yellow]ADDRESS RESULTS[/]", style="yellow"))
    table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="dim",
        box=box.SIMPLE,
    )
    table.add_column("Address", style="cyan")
    table.add_column("Balance (BTC)", style="green", justify="right")
    table.add_column("Balance (USD)", style="green", justify="right")
    table.add_column("Transactions", justify="center")

    for row in rows:
        addr, bal, usd, txs = row
        table.add_row(addr[:8] + "..." + addr[-8:], f"{bal:.8f}", f"${usd:,.2f}", str(txs))

    console.print(table)
    console.print()


def show_proxy_table(rows: list):
    console.print()
    console.print(Rule("[bold yellow]PROXY LIST[/]", style="yellow"))
    table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="dim",
        box=box.SIMPLE,
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Proxy", style="cyan")

    for i, proxy in enumerate(rows):
        table.add_row(str(i+1), proxy[:50] + ("..." if len(proxy) > 50 else ""))

    console.print(table)
    console.print()


def show_portfolio_table(rows: list):
    console.print()
    console.print(Rule("[bold yellow]PORTFOLIO SUMMARY[/]", style="yellow"))
    table = Table(
        show_header=False,
        border_style="dim",
        box=box.SIMPLE,
    )
    table.add_column("Metric", style="green")
    table.add_column("Value", style="cyan", justify="right")

    for metric, value in rows:
        table.add_row(metric, value)

    console.print(table)
    console.print()


def show_seed_results_table(rows: list):
    console.print()
    console.print(Rule("[bold yellow]SEED RESULTS[/]", style="yellow"))
    table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="dim",
        box=box.SIMPLE,
    )
    table.add_column("Seed", style="cyan")
    table.add_column("Address", style="green")
    table.add_column("Balance (BTC)", style="green", justify="right")
    table.add_column("Balance (USD)", style="green", justify="right")

    for row in rows:
        seed, addr, bal, usd = row
        table.add_row(seed, addr[:8] + "..." + addr[-8:], f"{bal:.8f}", f"${usd:,.2f}")

    console.print(table)
    console.print()


def print_success(msg: str):
    console.print(f"[green]✓[/] {msg}")


def print_error(msg: str):
    console.print(f"[red]✗[/] {msg}")


def print_info(msg: str):
    console.print(f"[cyan]i[/] {msg}")


def print_warning(msg: str):
    console.print(f"[yellow]![/] {msg}")


def separator(char: str = "─", length: int = 58):
    console.print(Rule(style="dim"))


def progress_bar(current: int, total: int, width: int = 30, prefix: str = ""):
    filled = int(width * current / total) if total > 0 else 0
    pct = (current / total * 100) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    console.print(f"\r{prefix}[yellow]{bar}[/] [dim]{pct:.0f}%[/]", end="")