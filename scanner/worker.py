# -*- coding: utf-8 -*-
import threading
import queue
import time
import random
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .client import BitcoinClient
from .env import get_proxy_env, set_proxy_env, clear_proxy_env


class ScannerWorker:
    def __init__(self, rpc_endpoint: str, proxy_list: List[str], threads: int = 20, timeout: int = 30):
        self.rpc_endpoint = rpc_endpoint
        self.proxy_list = proxy_list
        self.threads = threads
        self.timeout = timeout
        self.results = []
        self.lock = threading.Lock()
        self.proxy_index = 0
        self.proxy_lock = threading.Lock()

    def _get_next_proxy(self) -> Optional[str]:
        with self.proxy_lock:
            if not self.proxy_list:
                return None
            proxy = self.proxy_list[self.proxy_index % len(self.proxy_list)]
            self.proxy_index += 1
            return proxy

    def _check_address(self, address: str, proxy: Optional[str] = None) -> Dict[str, Any]:
        client = BitcoinClient(self.rpc_endpoint, proxy=proxy, timeout=self.timeout)
        return client.get_address_balance(address)

    def check_single(self, address: str, use_proxy: bool = True) -> Dict[str, Any]:
        proxy = None
        if use_proxy and self.proxy_list:
            proxy = self._get_next_proxy()
        return self._check_address(address, proxy)

    def check_batch(self, addresses: List[str], use_proxy: bool = True, progress_callback=None) -> List[Dict[str, Any]]:
        results = []
        total = len(addresses)
        completed = 0

        def _process_address(addr):
            nonlocal completed
            proxy = None
            if use_proxy and self.proxy_list:
                proxy = self._get_next_proxy()
            result = self._check_address(addr, proxy)
            with self.lock:
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, addr)
            return result

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(_process_address, addr): addr for addr in addresses}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    addr = futures[future]
                    results.append({'address': addr, 'error': str(e), 'balance_btc': 0, 'tx_count': 0})

        return results

    def check_seed_derived_addresses(self, seed_phrases: List[str], derivation_paths: List[str],
                                     use_proxy: bool = True, progress_callback=None) -> Dict[str, List[Dict]]:
        from mnemonic import Mnemonic
        from bip32 import BIP32
        import hashlib

        results = {}
        total = len(seed_phrases) * len(derivation_paths)
        completed = 0

        def _process_seed(seed):
            nonlocal completed
            seed_results = []
            try:
                mnemo = Mnemonic("english")
                if not mnemo.check(seed):
                    return {'error': 'Invalid mnemonic', 'seed': seed, 'addresses': []}
                seed_bytes = mnemo.to_seed(seed)
                bip32 = BIP32.from_seed(seed_bytes)
                for path in derivation_paths:
                    key = bip32.get_derivation_path(path)
                    address = key.get_public_key().to_address()  # simplified; actual BTC address derivation needed
                    proxy = None
                    if use_proxy and self.proxy_list:
                        proxy = self._get_next_proxy()
                    client = BitcoinClient(self.rpc_endpoint, proxy=proxy, timeout=self.timeout)
                    balance_data = client.get_address_balance(address)
                    seed_results.append({
                        'path': path,
                        'address': address,
                        'balance_btc': balance_data.get('balance_btc', 0),
                        'tx_count': balance_data.get('tx_count', 0)
                    })
                    with self.lock:
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total, seed[:20] + "...")
            except Exception as e:
                return {'error': str(e), 'seed': seed, 'addresses': []}
            return {'seed': seed, 'addresses': seed_results}

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(_process_seed, seed): seed for seed in seed_phrases}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results[result.get('seed', 'unknown')] = result.get('addresses', [])
                except Exception as e:
                    seed = futures[future]
                    results[seed] = [{'error': str(e)}]

        return results