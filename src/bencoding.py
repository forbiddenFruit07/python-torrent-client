import string
def decode(source: bytes):
    """
    Decodes bencoded data.
    Example: b'i42e' -> 42
    """
    # In Python, a single byte from a bytes object is an integer.
    # ASCII 'i' is 105.
    if source.startswith(b'i'):
        return decode_int(source)
    elif source[:1].isdigit():
        return decode_string(source)
    else:
        raise ValueError("Unknown format")

def decode_int(source: bytes):
    # TODO:
    # 1. Find the position of the 'e' (end marker)
    # 2. Extract the number part between 'i' and 'e'
    # 3. Convert that part to a python int and return it
    end_index=source.find(b'e')
    if end_index==-1:
        raise ValueError("Invalid Integer: e not found")
    num_part=source[1:end_index]
    return int(num_part)

def decode_string(source: bytes):
    colon_index = source.find(b':')
    if colon_index == -1:
        raise ValueError("Invalid string: colon not found")
    length=source[colon_index-1]
    end_pos=colon_index+1+length
    str_part= source[colon_index+1:end_pos]
    return str_part


# Simple test to run this file
if __name__ == "__main__":
    print(decode(b"i42e"))
    print(decode(b'4:spam'))
