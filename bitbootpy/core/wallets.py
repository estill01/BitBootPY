"""Helpers for loading blockchain key material from environment variables."""

from __future__ import annotations

import json
import os

from bitcoinlib.keys import Key as BTCKey
from eth_keys import keys as eth_keys
from solders.keypair import Keypair as SolanaKeypair
from arweave import Wallet


def _require_env(var: str) -> str:
    value = os.getenv(var)
    if value:
        return value
    raise RuntimeError(f"{var} environment variable is not set")


def get_bitcoin_key() -> BTCKey:
    """Return a Bitcoin ``Key`` from ``BITBOOTPY_BITCOIN_KEY``."""
    key_str = _require_env("BITBOOTPY_BITCOIN_KEY")
    return BTCKey(key_str)


def get_bitcoin_rpc_url() -> str:
    """Return the Bitcoin RPC URL from ``BITBOOTPY_BITCOIN_RPC_URL``."""
    return _require_env("BITBOOTPY_BITCOIN_RPC_URL")


def get_ethereum_key() -> eth_keys.PrivateKey:
    """Return an Ethereum ``PrivateKey`` from ``BITBOOTPY_ETHEREUM_KEY``."""
    key_str = _require_env("BITBOOTPY_ETHEREUM_KEY")
    if key_str.startswith("0x") or key_str.startswith("0X"):
        key_str = key_str[2:]
    key_bytes = bytes.fromhex(key_str)
    return eth_keys.PrivateKey(key_bytes)


def get_solana_keypair() -> SolanaKeypair:
    """Return a Solana ``Keypair`` from ``BITBOOTPY_SOLANA_KEYPAIR``."""
    key_str = _require_env("BITBOOTPY_SOLANA_KEYPAIR")
    try:
        data = json.loads(key_str)
        if isinstance(data, list):
            secret = bytes(data)
        else:
            raise ValueError("Solana keypair JSON must be an array of integers")
    except json.JSONDecodeError:
        from base58 import b58decode

        secret = b58decode(key_str)
    return SolanaKeypair.from_bytes(secret)


def get_arweave_wallet() -> Wallet:
    """Return an Arweave ``Wallet`` from ``BITBOOTPY_ARWEAVE_WALLET``."""
    key_str = _require_env("BITBOOTPY_ARWEAVE_WALLET")
    jwk_data = json.loads(key_str)
    return Wallet.from_data(jwk_data)
