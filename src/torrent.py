from bencoding import decoder,encoder
import hashlib
class TorrentReader:
    def __init__(self,file_path):
        with open(file_path,"rb") as file:
            file_content=file.read()
        self.meta_info = decoder(file_content)
        self.tracker_url=self.meta_info[b'announce'].decode()
        self.info=self.meta_info[b'info']
        encoded_info=encoder(self.info)
        self.info_hash=hashlib.sha1(encoded_info).digest()

    @property
    def total_size(self):
        size=0
        if b'files' in self.info:
            for file in self.info[b'files']:
                size+=file[b'length']
        else:
            size+=self.info[b'length']
        return size

#simple test:
if __name__=="__main__":
    try:
        torrent = TorrentReader("ubuntu-24.04.3.torrent")
        print(f"Tracker: {torrent.tracker_url}")
        print(f"Info Hash: {torrent.info_hash.hex()}")
        print(f"Total Size: {torrent.total_size / (1024**2):.2f} MB")
    except Exception as e:
        print(f"Error: {e}")