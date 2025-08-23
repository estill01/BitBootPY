"""Backward compatibility wrapper for the old ``known_hosts`` module.

The project originally exposed helper functions and data structures from a
module named :mod:`known_hosts`.  As part of the DHT network refactor the new
implementation lives in :mod:`dht_network`, but some external imports and tests
still reference :mod:`known_hosts`.  To ease the transition we simply re-export
everything here.
"""

from .dht_network import *  # noqa: F401,F403

