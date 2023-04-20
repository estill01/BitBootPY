import bitbootpy

if __name__ == "__main__":
    bitboot = BitBoot()

    # Announce peer
    bitboot.announce_peer("example_network", 6881)

    # Discover peers
    for discovered_peer in bitboot.lookup("example_network"):
        print("Discovered peer:", discovered_peer)
