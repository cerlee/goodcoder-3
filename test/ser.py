import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("127.0.01", 8001))
sock.send('{"NODES":"GCC3"}#')
got_data = ""
print 'start get data'
got_data = sock.recv(100)
print '*'*20
print 'got data', got_data
print '*'*20
sock.send('{"OUTPUT":"Success"}#')
