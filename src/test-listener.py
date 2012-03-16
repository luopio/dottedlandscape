import socket, struct
import sys

HOST = None # Symbolic name meaning all available interfaces
PORT = 2323
# magic, w, h, channels, max_val
HEADER_STRUCT = struct.Struct('!IHHHH')
DATA_STRUCT = None # constructed on first contact, when we know size
s = None

for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_DGRAM, 0, socket.AI_PASSIVE):
    print "found", res
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
        print af, socktype, proto
    except socket.error, msg:
        s = None
        continue
    try:
        s.bind(sa)
        # s.listen(1)
    except socket.error, msg:
        s.close()
        s = None
        continue
    break
    
if s is None:
    print 'could not open socket'
    sys.exit(1)
    

print "waiting for conn..."
# conn, addr = s.accept()
# print 'Connected by', addr
while 1:
    data = s.recv(0xfff) # 4095 bytes
    if not data: break
    # print repr(data)
    header = HEADER_STRUCT.unpack(data[:12])
    print header
    if not DATA_STRUCT:
        DATA_STRUCT = struct.Struct('B' * header[1] * header[2] * header[3])
    print DATA_STRUCT.unpack(data[12:])
    print '-'.join([repr(r) for r in data[:12]])
    print
    print
    # conn.send(data)
conn.close()
