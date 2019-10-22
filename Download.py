#!/usr/bin/env python3
import libtorrent
import time
from argparse import ArgumentParser


class Download:
    def __init__(self, magnet):
        self.magnet = magnet
        self.state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 
                          'finished', 'seeding', 'allocating', 'checking fastresume']

    def progress(self, status):
        progress = status.progress * 100
        dl_rate = status.download_rate / 1000
        up_rate = status.upload_rate / 1000
        peers = status.num_peers
        state = self.state_str[status.state]
        white = ' ' * 10
        print('\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s%s\r' % (progress,
                                                                                      dl_rate,
                                                                                      up_rate,
                                                                                      peers,
                                                                                      state,
                                                                                      white), end='', flush=True)

    def start(self):
        params = libtorrent.parse_magnet_uri(self.magnet)
        params['save_path'] = './'
        session = libtorrent.session()
        session.listen_on(6681, 6891)
        handle = session.add_torrent(params)

        print('Starting download of: "{name}"'.format(name=handle.name()))
        try:
            while not handle.is_seed():
                self.progress(handle.status())
                time.sleep(0.1)
            print('Download of "{name}" complete'.format(name=handle.name()))
        except KeyboardInterrupt:
            session.remove_torrent(handle)
            print('\rDownload of "{name}" aborted{white}'.format(name=handle.name(), white=' ' * 40))


if __name__ == '__main__':
    parser = ArgumentParser(description="Download magnet")
    parser.add_argument("-m", "--magnet",
                        dest="magnet", required=True,
                        help="magnet", metavar="String")
    args = parser.parse_args()
    magnet = args.magnet
    Download(magnet).start()
