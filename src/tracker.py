import socket
import struct

import requests
import os
from bencoding import decoder,encoder
from torrent import TorrentReader


# torrent = TorrentReader("ubuntu-26.04.torrent")
# print(f"Tracker: {torrent.tracker_url}")
# print(f"Info Hash: {torrent.info_hash.hex()}")
# print(f"Total Size: {torrent.total_size / (1024**2):.2f} MB")
# if peers:
        #     for peer in peers:
        #         ip=peer[b'ip'].decode()
        #         port=peer[b'port']
        #         print(f"Peer: {ip}:{port}")
        # else:
        #     print("No peers found in tracker response.")
        # print("Tracker response:", tracker_response)
def get_peers(torrent_file):
    torrent = TorrentReader(torrent_file)
    print(f"Total Size: {torrent.total_size / (1024**2):.2f} MB")
    peer_id= b'-PC0007-'+ b'123456789000'
    params={
        "info_hash":torrent.info_hash,
        'peer_id':peer_id,
        'port':6881,
        'uploaded':0,
        'downloaded':0,
        'left':torrent.total_size,
        'compact':1,
        'event':'started'
    }
    try:
        response = requests.get(torrent.tracker_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error contacting tracker: {e}")
    else:
        peers_list=[]
        tracker_response = decoder(response.content)
        peers=tracker_response.get(b'peers')
        if isinstance(peers, bytes):
            for i in range(0, len(peers), 6):
                ip = socket.inet_aton(peers[i:i+4])
                port= struct.unpack('!H',peers[i+4:i+6])[0]
                peers_list.append((ip,port))
        elif isinstance(peers, list):
            for peer in peers:
                ip=peer[b'ip'].decode()
                port=peer[b'port']
                peers_list.append((ip,port))
                
        else:
            print("No peers found in tracker response.")
        print(f"Peers: {len(peers) if peers else 0}")
        
        return peers_list

if __name__ == "__main__":
    file="ubuntu-26.04.torrent"
    peers=get_peers(file)
    print(peers)