import requests
import os
from bencoding import decoder,encoder
from torrent import TorrentReader


torrent = TorrentReader("ubuntu-26.04-desktop-amd64.iso.torrent")
print(f"Tracker: {torrent.tracker_url}")
print(f"Info Hash: {torrent.info_hash.hex()}")
print(f"Total Size: {torrent.total_size / (1024**2):.2f} MB")


peer_id= os.urandom(20)
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
    response = requests.get(torrent.tracker_url, params=params)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error contacting tracker: {e}")
else:
    tracker_response = decoder(response.content)
    peers=tracker_response.get(b'peers')
    print(type(peers))
    print(f"Peers: {len(peers) if peers else 0}")
    if peers:
        for peer in peers:
            ip=peer[b'ip'].decode()
            port=peer[b'port']
            print(f"Peer: {ip}:{port}")
    else:
        print("No peers found in tracker response.")
    # print("Tracker response:", tracker_response)
    print("Tracker response keys:", tracker_response.keys())
    
    
