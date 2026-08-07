# -*- coding: utf-8 -*-
import json
import time
import random
import requests
from typing import Optional, Dict, Any, List


class BitcoinClient:
    def __init__(self, rpc_endpoint: str, proxy: Optional[str] = None, timeout: int = 30):
        self.rpc_endpoint = rpc_endpoint.rstrip('/')
        self.proxy = proxy
        self.timeout = timeout
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy,
            }

    def _request(self, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.rpc_endpoint}{path}"
        headers = {'User-Agent': 'Bitcoin-Cracker/2.0'}
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def get_address_balance(self, address: str) -> Dict[str, Any]:
        path = f"/address/{address}"
        data = self._request(path)
        if 'error' in data:
            return {'error': data['error'], 'balance': 0, 'tx_count': 0}
        chain_stats = data.get('chain_stats', {})
        mempool_stats = data.get('mempool_stats', {})
        balance = chain_stats.get('funded_txo_sum', 0) - chain_stats.get('spent_txo_sum', 0)
        balance += mempool_stats.get('funded_txo_sum', 0) - mempool_stats.get('spent_txo_sum', 0)
        tx_count = chain_stats.get('tx_count', 0) + mempool_stats.get('tx_count', 0)
        return {
            'address': address,
            'balance_sat': balance,
            'balance_btc': balance / 1e8,
            'tx_count': tx_count,
            'chain_stats': chain_stats,
            'mempool_stats': mempool_stats
        }

    def get_address_transactions(self, address: str, limit: int = 50) -> List[Dict]:
        path = f"/address/{address}/txs"
        params = {'limit': limit}
        data = self._request(path, params)
        if 'error' in data:
            return []
        return data if isinstance(data, list) else []

    def get_blockchain_info(self) -> Dict:
        path = "/blocks/tip/height"
        height = self._request(path)
        if 'error' in height:
            return {'error': height['error']}
        return {'height': height}

    def get_utxos(self, address: str) -> List[Dict]:
        path = f"/address/{address}/utxo"
        data = self._request(path)
        if 'error' in data:
            return []
        return data if isinstance(data, list) else []

    def estimate_fee(self, target: int = 6) -> int:
        path = f"/fee-estimates"
        data = self._request(path)
        if 'error' in data:
            return 0
        return data.get(str(target), 0)