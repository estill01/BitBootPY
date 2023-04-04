import asyncio
import libtorrent as lt

class AsyncBitBoot:
    def __init__(self, unique_key, bootstrap_nodes=None):
        self.unique_key = unique_key
        self.bootstrap_nodes = bootstrap_nodes or [
            ("router.utorrent.com", 6881),
            ("router.bittorrent.com", 6881),
            ("dht.transmissionbt.com", 6881),
            ("dht.aelitis.com", 6881),
        ]
        self.ses = self.create_session()

    def create_session(self):
        ses = lt.session()
        ses.start_dht()

        # Add the specified bootstrap nodes
        for node in self.bootstrap_nodes:
            host, port = node
            ses.add_dht_bootstrap_node(host, port)

        return ses

    async def announce(self):
        entry = lt.create_torrent()
        entry.add_tracker("udp://tracker.openbittorrent.com:80/announce", 0)
        entry.set_comment("Announcing peer with unique key")
        entry.set_creator("Python BitBoot-like")
        entry.add_url_seed("http://retracker.local/announce")

        torrent_info = lt.bdecode(entry.generate())
        info_hash = lt.sha1_hash(torrent_info.info_hash())

        self.ses.async_add_torrent({
            "ti": lt.torrent_info(torrent_info),
            "save_path": "./",
            "seed_mode": True,
            "storage_mode": lt.storage_mode_t.storage_mode_sparse,
            "paused": False,
            "auto_managed": True,
            "duplicate_is_error": True
        })

        return info_hash

    async def lookup(self, info_hash, num_searches=10, delay=5):
        found_peers = set()
        for _ in range(num_searches):
            print("Searching for peers...")
            await asyncio.sleep(delay)
            results = self.ses.dht_get_peers(info_hash)
            if results:
                for peer in results:
                    found_peers.add(peer)
                    print(f"Found a peer: {peer[0]}:{peer[1]}")
        return found_peers

    def stop(self):
        self.ses.stop_dht()
        self.ses.pause()

