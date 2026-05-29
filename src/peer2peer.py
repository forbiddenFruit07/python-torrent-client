import socket
import struct
import tracker
from torrent import TorrentReader

def create_handshake(peer_id,info_hash):
    
    pstrln=19
    pstr=b'BitTorrent protocol'
    reserved = b'\x00' * 8
    format_str = '>B19s8s20s20s'

    handshake = struct.pack(format_str, pstrln, pstr, reserved, info_hash, peer_id)
    return handshake

def parse_handshake(handshake):
    format_str = f'>B19s8s20s20s'
    unpacked_data = struct.unpack(format_str, handshake)
    pstrln, pstr, reserved, info_hash, peer_id = unpacked_data
    return info_hash

def connect_to_peer(peer_ip, peer_port, handshake,info_hash):
    if ':' in peer_ip:
        add_type=socket.AF_INET6
    else:
        add_type=socket.AF_INET

    with socket.socket(add_type, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        try:
            sock.connect((peer_ip, peer_port))
            print('TCP connection successful! Sending Handshake')
            sock.sendall(handshake)

            print('Waiting for Response..')
            response=sock.recv(68)
            if len(response)<68:
                print('Partial data received')
                return
            r_info_hash=parse_handshake(response)
            if r_info_hash==info_hash:
                print("The peer has the required data")
                print(f'peer_id: {response[48:].hex()}')
            else:
                print('Info hash mismatch!')
        except socket.timeout:
            print(f'Error: Connection timed out')
        except ConnectionRefusedError:
            print(f'Connection refused by the peer!')
        except Exception as e:
            print(f'Network error occured : {e}')

if __name__ == '__main__':
    file="ubuntu-26.04.torrent"
    torrent=TorrentReader(file)
    peers=tracker.get_peers(file)
    info_hash=torrent.info_hash
    peer_id= b'-PC0007-' + b'123456789000'
    handshake=create_handshake(peer_id,info_hash)
    if peers:
        first_peer = peers[0]
        
        peer_ip = first_peer[0]
        peer_port = first_peer[1]
        
        connect_to_peer(peer_ip, peer_port, handshake, info_hash)
