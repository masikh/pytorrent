import libtorrent
import time
import sys

ses = libtorrent.session()
ses.listen_on(6881, 6891)
ses.set_local_upload_rate_limit(1000000)
ses.set_local_download_rate_limit(1000000)

info = libtorrent.torrent_info('/home/robert/Desktop/test.torrent')
h = ses.add_torrent({'ti': info, 'save_path': '/libraries/TVShows/Westworld/'})
h.set_download_limit(1000000)
h.set_upload_limit(1000000)

print('starting', h.name())

count = 1
while True:
    s = h.status()
    state_str = ['queued', 'checking', 'downloading metadata', 'downloading',
                 'finished', 'seeding', 'allocating', 'checking fastresume']
    dots = '.' * count
    print('\r%.2f%% complete (down/up: %.1f/%.1f kB/s peers: %d seeds: %d leeches: %d) %s %s' % (s.progress * 100, s.download_rate / 1000,
                                                                                                 s.upload_rate / 1000, s.num_peers,
                                                                                                 s.num_seeds, s.num_uploads,
                                                                                                 state_str[s.state], dots)),
    sys.stdout.flush()
    time.sleep(1)
    count += 1
    if count > 3:
        count = 1

print(h.name(), 'complete')
