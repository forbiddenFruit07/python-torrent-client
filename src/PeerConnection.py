'''This class is responsible for managing the connection with peers.'''

import struct
import asyncio

import tracker
from torrent import TorrentReader
class PeerConnection:
    def __init__(self, peer_ip, peer_port, peer_id, info_hash):
        self.ip = peer_ip
        self.port = peer_port
        self.my_peer_id = peer_id
        self.info_hash = info_hash

        self.reader=None
        self.writer=None

    def create_handshake(self):
        pstrln=19
        pstr=b'BitTorrent protocol'
        reserved = b'\x00' * 8
        format_str = '>B19s8s20s20s'

        handshake = struct.pack(format_str, pstrln, pstr, reserved, self.info_hash, self.my_peer_id)
        return handshake
    
    async def connect_and_handshake(self):
        '''Returns the result of the handshake process. 
           True if successful, False otherwise.'''
        
        try:
            self.reader,self.writer= await asyncio.wait_for(
                asyncio.open_connection(self.ip,self.port),
                timeout=5.0   
            )

            handshake=self.create_handshake()
            self.writer.write(handshake)
            await self.writer.drain()

            response = await asyncio.wait_for(self.reader.readexactly(68),timeout=5.0)

            peer_info_hash = struct.unpack('>B19s8s20s20s', response)[3]

            if peer_info_hash == self.info_hash:
                print(f"{self.ip} : success , info hash matched")
                return True
            else:
                print(f'{self.ip} : failure, mismatched info hash')
                return False
            
        except asyncio.TimeoutError:
            print("Connection Timeout!")
        except ConnectionResetError:
            print("Connection reset by peer!")
        except Exception as e:
            print(f"Error connecting to peer: {e}")
        await self.disconnect()
        return False
    
    async def message_loop(self):
        print("Listening for messages from peer...")
        try:
            while True:

                length_bytes = await self.reader.readexactly(4)

                message_length = struct.unpack('>I', length_bytes)[0]

                if message_length == 0:
                    print("Received keep-alive message")
                    continue
                message = await self.reader.readexactly(message_length)
                


    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send_message(self, message):
        if self.writer:
            self.writer.write(message)
            await self.writer.drain()
            
    
async def main():
    file="ubuntu-26.04.torrent"
    torrent=TorrentReader(file)
    peer_id= b'-PC0007-' + b'123456789000'
    torrent=TorrentReader(file)
    info_hash=torrent.info_hash
    parsed_peers=tracker.get_peers(file)

    peers= [PeerConnection(peer[0],peer[1],peer_id,info_hash) for peer in parsed_peers[:5]]

    tasks=[peer.connect_and_handshake() for peer in peers]

    results=await asyncio.gather(*tasks)
    print(f"Handshake results: {results}")

    print("test completed, closing connections...")

    close_tasks=[]
    for peer, success in zip(peers, results):
        if success:
            close_tasks.append(peer.disconnect())
    
    if close_tasks:
        await asyncio.gather(*close_tasks)
    print("All connections closed.")

if __name__ == '__main__':
    asyncio.run(main())