# pytorrent-tracker.py
# A bittorrent tracker

from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from logging import basicConfig, info, INFO
from socket import inet_aton
from struct import pack
from urllib.request import urlopen

from urllib.parse import parse_qs
from bencode import encode
# from simpledb import Database


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
        p = {}
        p["peer id"] = peer[0]
        p["ip"] = peer[1]
        p["port"] = int(peer[2])

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


""" Take a request, do some some database work, return a peer
    list response. 
"""


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        # Decode the request
        package = decode_request(s.path)

        if not package:
            s.send_error(403)
            return

        # Get the necessary info out of the request
        info_hash = package["info_hash"][0]
        compact = bool(package["compact"][0])
        ip = s.client_address[0]
        port = package["port"][0]
        peer_id = package["peer_id"][0]

        add_peer(s.server.torrents, info_hash, peer_id, ip, port)

        # Generate a response
        response = {}
        response["interval"] = s.server.interval
        response["complete"] = 0
        response["incomplete"] = 0
        response["peers"] = peer_list(s.server.torrents[info_hash], compact)

        # Send off the response
        s.send_response(200)
        s.end_headers()
        s.wfile.write(encode(response))

        # Log the request, and what we send back
        info("PACKAGE: %s", package)
        info("RESPONSE: %s", response)

    """ Just supress logging. 
    """

    def log_message(self, format, *args):

        return


""" Read in the initial values, load the database. 
"""


class Tracker:
    def __init__(self, host="", port=9010, interval=5, torrent_db="tracker.db", log="tracker.log", inmemory=True):
        self.host = host
        self.port = port

        self.inmemory = inmemory

        self.server_class = HTTPServer
        self.httpd = self.server_class((self.host, self.port), RequestHandler)

        self.running = False	# We're not running to begin with

        self.server_class.interval = interval

        # Set logging info
        basicConfig(filename = log, level = INFO)

        # If not in memory, give the database a file, otherwise it
        # will stay in memory
        # if not self.inmemory:
        #     self.server_class.torrents = Database(torrent_db)
        # else:
        #     self.server_class.torrents = Database(None)
        self.server_class.torrents = list()

    """ Keep handling requests, until told to stop. 
    """

    def runner(self):

        while self.running:
            self.httpd.handle_request()

    """ Start the runner, in a seperate thread. 
    """

    def run(self):
        if not self.running:
            self.running = True
            self.thread = Thread(target = self.runner)
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
