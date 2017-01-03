import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("127.0.01", 8001))
sock.send('{"TASKS":{"m":"baidu/base/ub", "e":"GCC3", "o":".", "c":"pwd"}}#')
got_data = ""
got_data = sock.recv(20)
print '*'*20
print 'output is', got_data
print '*'*20
