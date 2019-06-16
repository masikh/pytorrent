import bencode
import hashlib
import os
import binascii
from argparse import ArgumentParser


""" Feed a torrent file and get the magnet hash

    e.g.: 
    
        http://releases.ubuntu.com/19.04/ubuntu-19.04-desktop-amd64.iso.torrent
        
        translates to:
        
        d540fc48eb12f2833163eed6421d449dd8f1ce1f 
"""


class Torrent2Magnet:
    def __init__(self, torrent):
        self.torrent = torrent

    def create_magnet(self):
        if not os.path.isfile(self.torrent):
            return None

        data = open(self.torrent, 'r').read()
        metadata = bencode.bdecode(data)

        hashcontents = bencode.bencode(metadata['info'])
        digest = hashlib.sha1(hashcontents).digest()
        return binascii.b2a_hex(digest)


if __name__ == "__main__":
    parser = ArgumentParser(description="Convert torrent to magnet link hash")
    parser.add_argument("-t", "--torrent",
                        dest="torrent", required=True,
                        help="Torrent file", metavar="FILE")
    args = parser.parse_args()
    torrent = args.torrent

    torrent2magnet = Torrent2Magnet(torrent)
    magnet = torrent2magnet.create_magnet()
    print(magnet)
