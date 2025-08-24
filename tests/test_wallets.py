import base64
import json
import os

import pytest
from bitcoinlib.keys import Key as BTCKey
from eth_keys import keys as eth_keys
from solders.keypair import Keypair as SolanaKeypair
from arweave import Wallet
from Crypto.PublicKey import RSA

from bitbootpy.core.wallets import (
    get_btc_key,
    get_eth_key,
    get_solana_keypair,
    get_arweave_wallet,
)
from bitbootpy.core.backends.ethereum_discv5 import EthereumDiscv5Backend
from bitbootpy.core.backends.solana_backend import SolanaBackend


def test_missing_env(monkeypatch):
    monkeypatch.delenv("BITBOOTPY_BTC_KEY", raising=False)
    monkeypatch.delenv("BITBOOTPY_ETH_KEY", raising=False)
    monkeypatch.delenv("BITBOOTPY_SOLANA_KEYPAIR", raising=False)
    monkeypatch.delenv("BITBOOTPY_ARWEAVE_WALLET", raising=False)

    with pytest.raises(RuntimeError):
        get_btc_key()
    with pytest.raises(RuntimeError):
        get_eth_key()
    with pytest.raises(RuntimeError):
        get_solana_keypair()
    with pytest.raises(RuntimeError):
        get_arweave_wallet()


def test_get_btc_key(monkeypatch):
    k = BTCKey()
    monkeypatch.setenv("BITBOOTPY_BTC_KEY", k.wif())
    loaded = get_btc_key()
    assert isinstance(loaded, BTCKey)
    assert loaded.wif() == k.wif()


def test_get_eth_key(monkeypatch):
    pk = eth_keys.PrivateKey(os.urandom(32))
    monkeypatch.setenv("BITBOOTPY_ETH_KEY", pk.to_hex())
    loaded = get_eth_key()
    assert isinstance(loaded, eth_keys.PrivateKey)
    assert loaded == pk


def test_get_solana_keypair(monkeypatch):
    kp = SolanaKeypair()
    monkeypatch.setenv("BITBOOTPY_SOLANA_KEYPAIR", json.dumps(list(bytes(kp))))
    loaded = get_solana_keypair()
    assert isinstance(loaded, SolanaKeypair)
    assert bytes(loaded) == bytes(kp)


def _b64(x: bytes) -> str:
    return base64.urlsafe_b64encode(x).decode().rstrip("=")


def test_get_arweave_wallet(monkeypatch):
    k = RSA.generate(1024)
    jwk = {
        "kty": "RSA",
        "n": _b64(k.n.to_bytes((k.n.bit_length()+7)//8, "big")),
        "e": _b64(k.e.to_bytes((k.e.bit_length()+7)//8, "big")),
        "d": _b64(k.d.to_bytes((k.d.bit_length()+7)//8, "big")),
        "p": _b64(k.p.to_bytes((k.p.bit_length()+7)//8, "big")),
        "q": _b64(k.q.to_bytes((k.q.bit_length()+7)//8, "big")),
        "dp": _b64((k.d % (k.p-1)).to_bytes((k.d % (k.p-1)).bit_length()//8+1, "big")),
        "dq": _b64((k.d % (k.q-1)).to_bytes((k.d % (k.q-1)).bit_length()//8+1, "big")),
        "qi": _b64(pow(k.q, -1, k.p).to_bytes((pow(k.q,-1,k.p).bit_length()+7)//8, "big")),
    }
    monkeypatch.setenv("BITBOOTPY_ARWEAVE_WALLET", json.dumps(jwk))
    loaded = get_arweave_wallet()
    assert isinstance(loaded, Wallet)
    assert loaded.address == Wallet.from_data(jwk).address


def test_ethereum_backend_uses_helper(monkeypatch):
    pk = eth_keys.PrivateKey(os.urandom(32))
    monkeypatch.setenv("BITBOOTPY_ETH_KEY", pk.to_hex())
    backend = EthereumDiscv5Backend()
    assert backend.key == pk


def test_solana_backend_uses_helper(monkeypatch):
    kp = SolanaKeypair()
    monkeypatch.setenv("BITBOOTPY_SOLANA_KEYPAIR", json.dumps(list(bytes(kp))))
    backend = SolanaBackend()
    assert bytes(backend.keypair) == bytes(kp)
