class BDecoder:
    def __init__(self,data):
        self.data=data
        self.index=0
    def decode(self):
        """
        Decodes bencoded data.
        Example: b'i42e' -> 42
        """
        c = self.peek()

        if c is None:
            raise EOFError("End of data")

        if c==b'i':
            return self.decode_int()
        elif c.isdigit():
            return self.decode_string()
        elif c==b'l':
            return self.decode_list()
        elif c==b'd':
            return self.decode_dict()
        else:
            raise ValueError("Unknown format")

    def peek(self):
        if self.index+1>len(self.data):
            return None
        else:
            return self.data[self.index:self.index+1]
        
    def consume(self,num_bytes=1):
        self.index+=num_bytes

    def decode_int(self):
        self.consume()
        end_index=self.data.find(b'e',self.index)
        if end_index==-1:
            raise ValueError("Invalid Integer: e not found")
        num_part=self.data[self.index:end_index]
        self.index=end_index
        self.consume()
        return int(num_part)

    def decode_string(self):
        colon_index = self.data.find(b':',self.index)
        if colon_index == -1:
            raise ValueError("Invalid string: colon not found")
        length_bytes=self.data[self.index:colon_index]
        length=int(length_bytes)
        start_pos=colon_index+1
        end_pos=start_pos+length
        str_part= self.data[start_pos:end_pos]
        self.index=end_pos
        return str_part

    def decode_list(self)-> list:
        self.consume()
        output=[]
        while True:
            if self.peek()==b'e':
                break
            if self.peek() is None:
                raise EOFError("unexpected end of line. No b'e' found.")
            output.append(self.decode())
        self.consume()
        return output
    
    def decode_dict(self)-> dict:
        self.consume()
        output={}
        while True:
            if self.peek()==b'e':
                break
            if self.peek() is None:
                raise EOFError("unexpected end of line. No b'e' found.")
            key=self.decode_string()
            value=self.decode()
            output[key]=value
        self.consume()
        return output
        


def decode(source: bytes):
    decoder = BDecoder(source)
    return decoder.decode()

def encoder(data):
    if isinstance(data,int):
        return b'i'+str(data).encode()+b'e'
    
    elif isinstance(data,str):
        return str(len(data)).encode()+b':'+data.encode()
    
    elif isinstance(data,bytes):
        return str(len(data)).encode()+b':'+data
    
    elif isinstance(data,list):
        res=b'l'
        for i in data:
            res+=encoder(i)
        return res+b'e'
    
    elif isinstance(data,dict):
        res=b'd'
        for i in sorted(data):
            res+=encoder(i)
            res+=encoder(data[i])
        return res+b'e'
    
    else:
        raise TypeError(f'Cannot encode data of type: {type(data)}')
    
# Simple test to run this file
if __name__ == "__main__":
    # Test everything
    print(decode(b"li42e4:spame")) 
    # Output: [42, b'spam']
    
    print(decode(b"d3:foo3:bar5:helloi52ee")) 

    # Output: {b'foo': b'bar', b'hello': 52}
    print(encoder([42, b'spam']))
    print(encoder({b'foo': b'bar', b'hello': 52}))
