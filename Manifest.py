from torf import Torrent
import os
import time
import queue


""" Create a torrent file for the content folder. If metadata parameter is true, a special metadata only torrent 
    is created 
"""


class Manifest:
    def __init__(self, files_path, trackers=None, comment=None, log_queue=queue.Queue(), metadata=False):
        self.log_queue = log_queue
        self.trackers = trackers
        self.comment = comment

        self.files = files_path
        self.manifest_file = '{path}/content.manifest'.format(path=files_path)
        if metadata:
            self.manifest_file = '{path}/metadata.manifest'.format(path=files_path)
            self.files = '{path}/json.zlib'.format(path=files_path)

    def create(self):
        def callback(torrent, path, pieces_done, pieces_total):
            percentage = f'{pieces_done/pieces_total * 100:3.1f}%'

            info = {
                'progress': percentage,
                'name': torrent.name,
                'path': torrent.path,
                'comment': torrent.comment,
            }
            self.log_queue.put_nowait(info)

        exclude = ['*.torrent', '*.manifest']
        manifest = Torrent(path=self.files, exclude=exclude, trackers=self.trackers, comment=self.comment)
        manifest.private = True
        manifest.generate(callback=callback, interval=1)
        manifest.write(self.manifest_file, overwrite=True)

    def content(self):
        try:
            if os.path.isfile(self.manifest_file):
                manifest = Torrent.read(self.manifest_file)
                self.log_queue.put(manifest.filetree)
        except:
            pass

    def info(self):
        try:
            if os.path.isfile(self.manifest_file):
                manifest = Torrent.read(self.manifest_file)
                self.log_queue.put({
                    'comment': self.manifest.comment,
                    'infohash': self.manifest.infohash,
                    'info': {
                        'files': self.manifest._metainfo['info']['files'],
                        'name': self.manifest._metainfo['info']['name'],
                        'piece_length': self.manifest._metainfo['info']['piece length'],
                        'pieces': self.manifest.pieces,
                        'private': self.manifest._metainfo['info']['private']
                    },
                    'size': manifest.size
                })
        except Exception as error:
            pass

    def magnet(self):
        try:
            if os.path.isfile(self.manifest_file):
                manifest = Torrent.read(self.manifest_file)
                self.log_queue.put(manifest.magnet())
        except:
            pass


def dump_log(queue):
    while not queue.empty():
        print('*')
        print('*' * 80)
        print(queue.get())
        print('*' * 80)
        print('*')


if __name__ == '__main__':
    queue = queue.Queue()

    trackers = ['https://tracker1.example.org:1234/announce', 'https://tracker2.example.org:5678/announce']

    manifest = Manifest('/Users/robert/Desktop/test', trackers, 'Movie', log_queue=queue, metadata=True)
    manifest.create()
    dump_log(queue)

    manifest = Manifest('/Users/robert/Desktop/test', trackers, 'Movie', log_queue=queue, metadata=False)
    manifest.create()
    dump_log(queue)

    manifest = Manifest('/Users/robert/Desktop/test', log_queue=queue, metadata=False)
    manifest.content()
    manifest.info()
    manifest.magnet()
    dump_log(queue)
