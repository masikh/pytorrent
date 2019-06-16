from btdht import DHT
import binascii
import time
from argparse import ArgumentParser


""" Get peers for a given magnet link
"""


class DistributedHashTable:
    def __init__(self):
        ignored_net = [
            '127.0.0.0/8', '169.254.0.0/16',    # Localhost and dhcp self assigned
            '224.0.0.0/4', '240.0.0.0/4',       # Multicast networks
            '255.255.255.255/32'                # Wide broadcast
        ]
        self.dht = DHT(ignored_net=ignored_net)
        self.dht.start()
        self.dht.bootstarp()

    def stop(self):
        self.dht.stop()

    def get_peers(self, magnet):
        peers = self.dht.get_peers(binascii.a2b_hex(magnet))
        return peers


if __name__ == "__main__":
    parser = ArgumentParser(description="Get peers for magnet link")
    parser.add_argument("-m", "--magnet",
                        dest="magnet", required=True,
                        help="Magnet link hash", metavar="HASH")
    args = parser.parse_args()
    magnet = args.magnet

    distributed_hash_table = DistributedHashTable()

    now = time.time()
    while True:
        peers = distributed_hash_table.get_peers(magnet)
        if peers is None or time.time() - now > 300:
            print('found 0 peers')
        else:
            print('found {amount} peers'.format(amount=len(peers)))
            if len(peers) > 300 or time.time() - now > 300:
                break
        time.sleep(5)
