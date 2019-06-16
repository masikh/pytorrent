from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from logging import basicConfig, INFO
from socket import inet_aton
from struct import pack
from urllib import urlopen
from urlparse import parse_qs
from simpledb import Client as Database


""" Return the decoded request string. 
"""


def decode_request(path):
    # Strip off the start characters
    if path[:1] == "?":
        path = path[1:]
    elif path[:2] == "/?":
        path = path[2:]

    return parse_qs(path)


""" Add the peer to the torrent database. 
"""


def add_peer(torrents, info_hash, peer_id, ip, port):
    # If we've heard of this, just add the peer
    if info_hash in torrents:
        # Only add the peer if they're not already in the database
        if (peer_id, ip, port) not in torrents[info_hash]:
            torrents[info_hash].append((peer_id, ip, port))
    # Otherwise, add the info_hash and the peer
    else:
       torrents[info_hash] = [(peer_id, ip, port)]


""" Return a compact peer string, given a list of peer details. 
"""


def make_compact_peer_list(peer_list):
    peer_string = ""
    for peer in peer_list:
        ip = inet_aton(peer[1])
        port = pack(">H", int(peer[2]))

        peer_string += (ip + port)

    return peer_string


""" Return an expanded peer list suitable for the client, given
    the peer list. 
"""


def make_peer_list(peer_list):
    peers = []
    for peer in peer_list:
        p = {'peer id': peer[0],
             'ip': peer[1],
             'port': int(peer[2])}
        peers.append(p)
    return peers


""" Depending on compact, dispatches to compact or expanded peer
    list functions. 
"""


def peer_list(peer_list, compact):
    if compact:
        return make_compact_peer_list(peer_list)
    else:
        return make_peer_list(peer_list)


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Just logging.
        return


class Tracker():
    def __init__(self,
                 host="",
                 port=9010,
                 interval=5,
                 log="tracker.log"):

        self.host = host
        self.port = port
        self.thread = None
        self.server_class = HTTPServer
        self.httpd = self.server_class((self.host, self.port), RequestHandler)
        self.running = False

        self.server_class.interval = interval

        # Set logging info
        basicConfig(filename=log, level=INFO)
        self.server_class.torrents = Database(None)

    """ Keep handling requests, until told to stop. 
    """

    def runner(self):
        while self.running:
            self.httpd.handle_request()
            print('got request')

    """ Start the runner, in a separate thread. 
    """

    def run(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target=self.runner)
            self.thread.start()

    """ Send a dummy request to the server. 
    """

    def send_dummy_request(self):
        # To finish off httpd.handle_request()
        address = "http://127.0.0.1:" + str(self.port)
        urlopen(address)

    """ Stop the thread, and join to it. 
    """

    def stop(self):
        if self.running:
            self.running = False
            self.send_dummy_request()
            self.thread.join()

    """ Stop the tracker thread, write the database. 
    """

    def __del__(self):
        self.stop()
        self.httpd.server_close()


if __name__ == "__main__":
    tracker = Tracker()
    tracker.run()
