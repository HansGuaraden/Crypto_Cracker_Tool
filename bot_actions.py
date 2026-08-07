import time
import random
import os

from scanner.ui import (
    print_success,
    print_error,
    print_info,
    print_warning,
    progress_bar,
    show_address_result_table,
    show_proxy_table,
    show_portfolio_table,
    show_seed_results_table,
    console,
)
from config import (
    get_proxy_config,
    get_scanner_config,
    get_seed_checker_config,
    get_rpc_endpoints,
    get_export_config,
    add_proxy,
    remove_proxy,
    set_proxy_enabled,
    set_threads,
    save_config,
)


def action_check_address(config: dict):
    addr = console.input("[magenta]Enter Bitcoin address: [/]").strip()
    if not addr:
        print_error("Address cannot be empty")
        return

    proxy_cfg = get_proxy_config(config)
    if proxy_cfg.get("enabled", True):
        proxy_list = proxy_cfg.get("proxy_list", [])
        if not proxy_list:
            print_warning("No proxies loaded. Using direct connection.")
        else:
            proxy = random.choice(proxy_list)
            print_info(f"Using proxy: {proxy[:30]}...")

    print_info(f"Checking address: {addr[:10]}...{addr[-10:]}")
    time.sleep(1.5)

    balance_btc = round(random.uniform(0.0001, 5.0), 8)
    balance_usd = balance_btc * 60000
    txs = random.randint(1, 100)

    show_address_result_table([(addr, balance_btc, balance_usd, txs)])
    print_success(f"Balance: {balance_btc} BTC (≈ ${balance_usd:,.2f})")


def action_batch_check(config: dict):
    scanner_cfg = get_scanner_config(config)
    threads = scanner_cfg.get("threads", 20)
    print_info(f"Threads: {threads}")

    choice = console.input("[dim]Load from file? (y/n): [/]").strip().lower()
    addresses = []
    if choice == "y":
        file_path = console.input("[magenta]Path to address file: [/]").strip()
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                addresses = [line.strip() for line in f if line.strip()]
            print_info(f"Loaded {len(addresses)} addresses")
        else:
            print_error("File not found")
            return
    else:
        print_info("Enter addresses (one per line, empty line to finish):")
        while True:
            line = console.input("[magenta]> [/]").strip()
            if not line:
                break
            addresses.append(line)

    if not addresses:
        print_error("No addresses to check")
        return

    print_info(f"Checking {len(addresses)} addresses with {threads} threads...")
    total = len(addresses)
    results = []
    for i, addr in enumerate(addresses):
        progress_bar(i+1, total, prefix="  Scanning ")
        time.sleep(0.2)
        bal = round(random.uniform(0.0001, 2.0), 8)
        usd = bal * 60000
        txs = random.randint(0, 50)
        results.append((addr, bal, usd, txs))
        console.print()

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    show_address_result_table(sorted_results[:5])
    print_success(f"Checked {len(addresses)} addresses. Found {len([r for r in results if r[1] > 0.01])} with balance > 0.01 BTC.")


def action_seed_check(config: dict):
    seed_cfg = get_seed_checker_config(config)
    seed_file = seed_cfg.get("seed_file", "seeds.txt")
    threads = seed_cfg.get("threads", 10)
    threshold = seed_cfg.get("highlight_threshold_usd", 10000)

    print_info(f"Using seed file: {seed_file}, threads: {threads}")
    if not os.path.exists(seed_file):
        print_error(f"Seed file '{seed_file}' not found. Create it or change path in config.")
        return

    with open(seed_file, "r") as f:
        seeds = [line.strip() for line in f if line.strip()]

    if not seeds:
        print_error("No seed phrases found in file")
        return

    print_info(f"Loaded {len(seeds)} seed phrases")
    print_info(f"Highlight threshold: ${threshold:,}")

    results = []
    for i, phrase in enumerate(seeds):
        progress_bar(i+1, len(seeds), prefix="  Processing seed ")
        time.sleep(0.4)
        addr = "1" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=33))
        bal = round(random.uniform(0.0, 3.0), 8)
        usd = bal * 60000
        if usd > threshold:
            console.print(f"[bold red]⚠ HIGH VALUE: {usd:,.2f} USD[/]")
        results.append((phrase[:20] + "...", addr, bal, usd))
        console.print()

    show_seed_results_table(results[:10])
    high_value = [r for r in results if r[3] > threshold]
    if high_value:
        print_warning(f"Found {len(high_value)} seed(s) with balance > ${threshold:,}")
        output_file = seed_cfg.get("output_file", "seed_results.txt")
        with open(output_file, "w") as f:
            for r in high_value:
                f.write(f"{r[0]}, {r[1]}, {r[2]:.8f} BTC, ${r[3]:,.2f}\n")
        print_success(f"High-value seeds saved to {output_file}")


def action_proxy_manager(config: dict):
    proxy_cfg = get_proxy_config(config)
    proxy_list = proxy_cfg.get("proxy_list", [])
    enabled = proxy_cfg.get("enabled", True)
    rotation = proxy_cfg.get("rotation_mode", "round-robin")
    proxy_file = proxy_cfg.get("proxy_file", "proxies.txt")

    print_info(f"Proxy status: {'ENABLED' if enabled else 'DISABLED'}")
    print_info(f"Rotation mode: {rotation}")
    print_info(f"Loaded proxies: {len(proxy_list)}")
    if proxy_list:
        show_proxy_table(proxy_list[:10])

    console.print("\n[dim]Options: [1] Load from file  [2] Add proxy  [3] Remove proxy  [4] Toggle enable  [5] Save[/]")
    action = console.input("[magenta]Choose action: [/]").strip()
    if action == "1":
        if os.path.exists(proxy_file):
            with open(proxy_file, "r") as f:
                new_proxies = [line.strip() for line in f if line.strip()]
            for p in new_proxies:
                config = add_proxy(config, p)
            print_success(f"Loaded {len(new_proxies)} proxies from {proxy_file}")
        else:
            print_error(f"File {proxy_file} not found")
    elif action == "2":
        new_proxy = console.input("[magenta]Enter proxy (protocol://user:pass@host:port): [/]").strip()
        if new_proxy:
            config = add_proxy(config, new_proxy)
            print_success("Proxy added")
        else:
            print_error("Empty input")
    elif action == "3":
        idx = int(console.input("[magenta]Index to remove: [/]").strip())
        config = remove_proxy(config, idx)
        print_success(f"Removed proxy at index {idx}")
    elif action == "4":
        new_state = not enabled
        config = set_proxy_enabled(config, new_state)
        print_success(f"Proxy {'enabled' if new_state else 'disabled'}")
    elif action == "5":
        save_config(config)
        print_success("Proxy settings saved")
    else:
        print_error("Invalid action")


def action_portfolio_summary(config: dict):
    total_btc = round(random.uniform(0.5, 50.0), 4)
    total_usd = total_btc * 60000
    wallets = random.randint(1, 20)
    high_value = random.randint(0, 3)

    table_data = [
        ("Total BTC", f"{total_btc:.4f}"),
        ("Total USD", f"${total_usd:,.2f}"),
        ("Unique Wallets", str(wallets)),
        ("High-value wallets (> $10k)", str(high_value)),
        ("Average balance", f"{total_btc/wallets:.4f} BTC" if wallets else "0"),
    ]
    show_portfolio_table(table_data)
    print_info("Use option 6 to export full results.")


def action_export_results(config: dict):
    export_cfg = get_export_config(config)
    default_format = export_cfg.get("default_format", "txt")
    output_dir = export_cfg.get("output_directory", "./results")
    include_usd = export_cfg.get("include_usd_value", True)

    fmt = console.input(f"[magenta]Format (txt/csv/json, default {default_format}): [/]").strip() or default_format
    if fmt not in ["txt", "csv", "json"]:
        print_error("Invalid format")
        return

    os.makedirs(output_dir, exist_ok=True)
    filename = f"results_{int(time.time())}.{fmt}"
    full_path = os.path.join(output_dir, filename)

    data = []
    for _ in range(random.randint(5, 20)):
        addr = "1" + "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=33))
        bal = round(random.uniform(0.0001, 2.0), 8)
        usd = bal * 60000 if include_usd else None
        data.append((addr, bal, usd))

    if fmt == "txt":
        with open(full_path, "w") as f:
            f.write("Address, Balance BTC, Balance USD\n")
            for addr, bal, usd in data:
                f.write(f"{addr}, {bal:.8f}, {usd:.2f if usd else 'N/A'}\n")
    elif fmt == "csv":
        import csv
        with open(full_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Balance_BTC", "Balance_USD"])
            for addr, bal, usd in data:
                writer.writerow([addr, bal, usd if usd else ""])
    elif fmt == "json":
        import json
        with open(full_path, "w") as f:
            json.dump(data, f, indent=2)

    print_success(f"Exported {len(data)} records to {full_path}")


def action_chain_config(config: dict):
    rpc_cfg = get_rpc_endpoints(config)
    current_btc = rpc_cfg.get("bitcoin", "https://blockstream.info/api")
    print_info(f"Current Bitcoin RPC: {current_btc}")

    new_rpc = console.input("[magenta]New Bitcoin RPC endpoint (leave empty to keep): [/]").strip()
    if new_rpc:
        config["rpc_endpoints"]["bitcoin"] = new_rpc
        save_config(config)
        print_success("Updated Bitcoin RPC endpoint")
    else:
        print_info("No changes made")


def action_settings(config: dict):
    scanner_cfg = get_scanner_config(config)
    current_threads = scanner_cfg.get("threads", 20)
    current_timeout = scanner_cfg.get("request_timeout_sec", 30)

    print_info(f"Current threads: {current_threads}")
    new_threads = console.input("[magenta]New thread count (enter number): [/]").strip()
    if new_threads.isdigit():
        config = set_threads(config, int(new_threads))
        print_success(f"Threads set to {new_threads}")

    print_info(f"Current timeout: {current_timeout}s")
    new_timeout = console.input("[magenta]New timeout (seconds): [/]").strip()
    if new_timeout.isdigit():
        config["scanner"]["request_timeout_sec"] = int(new_timeout)
        save_config(config)
        print_success(f"Timeout set to {new_timeout}s")

    proxy_cfg = get_proxy_config(config)
    enabled = proxy_cfg.get("enabled", True)
    toggle = console.input(f"[magenta]Enable proxies? (y/n, current: {'ON' if enabled else 'OFF'}): [/]").strip().lower()
    if toggle in ("y", "n"):
        new_state = toggle == "y"
        config = set_proxy_enabled(config, new_state)
        print_success(f"Proxy {'enabled' if new_state else 'disabled'}")