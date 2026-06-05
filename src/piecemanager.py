'''Manages all the pieces of the torrent file, including downloading and verifying them.'''
from torrent import TorrentReader
from collections import defaultdict
import math,hashlib
class PieceManager:

    def __init__(self,torrent):
        self.file_size= torrent.total_size
        self.piece_length = torrent.piece_length
        self.num_pieces = math.ceil(self.file_size/self.piece_length)
        self.bitfield=['MISSING']*self.num_pieces
        self.peer_maps = {}
        self.torrent= torrent

    def get_piece_length(self, piece_index):
        ''' 
        Returns the exact byte length of a piece.
        All pieces are standard length except the very last one.
        '''
        if piece_index == self.num_pieces - 1:
            remainder = self.file_size % self.piece_length
            if remainder == 0:
                return self.piece_length
            return remainder
        return self.piece_length
    
    def mark_piece_pending(self,piece_index):
        ''' 
        Marks the pieces PENDING when downloading from a peer so that we dont
        use other peers to download the same piece.'''

        self.bitfield[piece_index] = 'PENDING'

    def reset_piece(self, piece_index):
        ''' Marks piece MISSING if the the download crashes midway'''

        self.bitfield[piece_index] = 'MISSING'
    
    def get_block_length(self, piece_index, buffer_offset):
        '''
        Returns the exact block length to request
        safely handles the end of file and non standard piece sizes.'''

        piece_length = self.get_piece_length(piece_index)

        remaining_bytes = piece_length - buffer_offset

        return min(16384, remaining_bytes)

    def update_peer_bitfield(self, peer_id, raw_bitfield_bytes):
        """Converts a raw bitfield payload into a boolean array and stores it."""
        peer_pieces = [False]*self.num_pieces

        for i in range(self.num_pieces):
            byte_index = i//8
            bit_index = i % 8
            mask = 1 << (7-bit_index)

            if byte_index < len(raw_bitfield_bytes):
                has_piece = (raw_bitfield_bytes[byte_index] & mask) != 0
                peer_pieces[i]=has_piece
        
        self.peer_maps[peer_id] = peer_pieces

    def get_next_piece_to_download(self, peer_id):
        ''' Returns the index of the first piece we need that this specific peer has.
        Returns None if this peer has nothing we want.'''

        if peer_id not in self.peer_maps:
            return None
        
        peer_bitfield = self.peer_maps[peer_id]

        for i in range(self.num_pieces):
            if self.bitfield[i] & peer_bitfield[i]:
                return i
        return None
    
    def validate_piece(self, piece_index, raw_downloaded_bytes):
        '''
        Returns True if the sha1 of downloaded piece matches
        '''
        actual = hashlib.sha1(raw_downloaded_bytes).digest()
        expected_hash = self.torrent.piece_hashes[piece_index]
        
        if actual == expected_hash:
            self.bitfield[piece_index]='COMPLETE'
            return True
        else:
            return False
        
    def is_complete(self):
        """Returns True if every single piece is marked COMPLETE."""
        return all(status == 'COMPLETE' for status in self.bitfield)