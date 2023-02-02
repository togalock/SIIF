# Modified RESP Serialization 1
# Reference Implementation
# Build 0.0.1+A23131

# Based on
# L-EJ-ORG-ISM SIIF 27, 0.0.3+A23131

import base64
# Helper Functions
class ByteBuffer:
    def __init__(self, init_bytes):
        self.buffer = bytearray(init_bytes)
        self.buffer_i, self.total_i = 0, 0

    @classmethod
    def from_string(cls, s):
        return cls(bytes(s, "UTF-8"))

    def seek(self, i = 0, actual_i = None, delta = None):
        if delta is not None:
            if self.buffer_i + delta >= 0:
                self.buffer_i = self.buffer_i + delta
                return self.buffer_i
        else:
            to_get = i if actual_i is None else actual_i - total_i
            if 0 <= i < len(buffer):
                self.buffer_i = self.buffer_i + delta
                return self.buffer_i
        return False

    def tell(self):
        return (self.buffer_i, self.total_i, len(self.buffer))
    
    def peek(self, n = None, until = None):
        find_this = bytes(until, "UTF-8") if isinstance(until, str) else until

        to_index = -1 if find_this is None \
                   else self.buffer.find(find_this, self.buffer_i) + len(find_this)

        to_index = to_index if to_index > 0 \
                   else n if n is not None \
                   else len(self.buffer)

        to_index = min(len(self.buffer), to_index)

        bytes_read = to_index
        res = self.buffer[self.buffer_i:to_index]

        if isinstance(until, str):
            res = res.decode("UTF-8")
        
        return (bytes_read, res)

    def read(self, n = None, until = None, pop = True):
        bytes_read, res = self.peek(n, until)

        if pop:
            del self.buffer[:bytes_read]
            self.buffer_i, self.total_i = 0, self.total_i + bytes_read
            
        else:
            self.buffer_i += bytes_read
            
        return (bytes_read, res)
    
    def write(self, bytes_or_str):
        if isinstance(bytes_or_str, str):
            bytes_or_str = bytes_or_str.encode("UTF-8")
        self.buffer = self.buffer.join(bytes_)
        return len(bytes_)


# Parsing
def parse(byte_buffer):
    _, header = byte_buffer.read(until = "\n")
    header = header.strip()
    data_type, size_or_data = header[0], header[1::]

    if data_type == "S":
        return size_or_data
    
    elif data_type == "I":
        return int(size_or_data)
    
    elif data_type == "N":
        return float(size_or_data)
    
    elif data_type == "B":
        return {"T": True, "F": False, "N": None}[size_or_data]
    
    elif data_type == "U":
        size = int(size_or_data)
        return byte_buffer.read(size)
    
    elif data_type == "=":
        size = int(size_or_data)
        b64_string = byte_buffer.read(size)[1].encode("UTF-8")
        altchars = "-_" if any([c in b64_string for c in "-_"]) else None
        return base64.b64decode(b64_string, altchars)
    
    elif data_type == "L":
        size = int(size_or_data)
        return [parse(byte_buffer) for _ in range(size)]

    elif data_type == "D":
        size = int(size_or_data)
        return {parse(byte_buffer): parse(byte_buffer) for _ in range(size)}

    elif data_type == "X":
        size = int(size_or_data)
        return [parse(byte_buffer) for _ in range(size)]

    else:
        return ["X", 4010, "Data type not supported: %s" % data_type]


def encode(any_):
    if isinstance(any_, str):
        if any_.isascii() and any_.isprintable():
            return "S%s\n" % (any_, )
        else:
            str_size = len(bytes(any_))
            return "U%i\n%s\n" % (str_size, any_)
        
    elif isinstance(any_, bool) or any_ is None: # Boolean must go before int
        return "B%s\n" % ({True: "T", False: "F", None: "N"}[any_], )
        
    elif isinstance(any_, int):
        return "I%i\n" % (any_, )

    elif isinstance(any_, float):
        return "F%f\n" % (any_, )

    elif isinstance(any_, (list, tuple)):
        list_elements = "".join([encode(e) for e in any_])
        return "L%i\n%s" % (len(any_), list_elements)

    elif isinstance(any_, dict):
        dict_elements = "".join([[encode(key), encode(any_[key])] for key in any_])
        return "D%i\n%s" % (len(any_), dict_elements)

    elif isinstance(any_, bytes):
        b64_string = base64.b64encode(any_)
        return "=%i\n%s\n" % (len(b64_string), b64_string)

    elif isinstance(any_, Exception):
        return "X%i\n%s" % (len(any_.args), any_.args)

    else:
        raise TypeError("Unsupported Data Type %s" % type(s))

