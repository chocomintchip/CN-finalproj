import socket
import select

HOST = ''
PORT = 12345
MAX_CONNECTION = 10
SOCKET_LIST = []
RECV_BUFFER = 4096

USER_LIST = [('1', '123'), ('2', '123')]
USER_STATUS = {'1': False, '2': False}

def client_login(sock):

	login_username = sock.recv(RECV_BUFFER)
	login_password = sock.recv(RECV_BUFFER)
	sock.send(login_check(login_username, login_password))
	return

def login_check(login_username, login_password):

	for username, password in USER_LIST:
		if username == login_username and password == login_password:
			if USER_STATUS[login_username]:
				return 'login fail'
			else:
				USER_STATUS[login_username] = True
				return 'login success'

	return 'login fail'

def client_register(sock):

	register_username = sock.recv(RECV_BUFFER)
	register_password = sock.recv(RECV_BUFFER)
	sock.send(register_user(register_username, register_password))
	return

def register_user(register_username, register_password):

	for username, password in USER_LIST:
		if username == register_username:
			return 'register fail'

	USER_LIST.append((register_username, register_password))
	USER_STATUS[register_username] = False
	return 'register success'

def client_knock(sock):

	knock_username = sock.recv(RECV_BUFFER)
	sock.send(knock_user(knock_username))
	return

def knock_user(knock_username):

	if knock_username not in USER_STATUS:
	 	return knock_username + ' is not registered'
	
	if USER_STATUS[knock_username]:
		return knock_username + ' is online'
	else:
		return knock_username + ' is offline'

def broadcast_data(sender_sock, sender_data):

	msg = str(sender_sock.getpeername()) + ':' + sender_data

	for sock in SOCKET_LIST:
		if sock != server_sock and sock != sender_sock:
			try:
				sock.send(sender_data)
				# sock.send(msg)
			# handle broken connection
			except:
				sock.close()
				SOCKET_LIST.remove(sock)


if __name__ == '__main__':

	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# reuse TCP connection
	server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# socket bind
	server_sock.bind((HOST, PORT))
	# socket max # of connection
	server_sock.listen(MAX_CONNECTION)
	# server_sock.settimeout(10)

	# put master socket in SOCKET_LIST
	SOCKET_LIST.append(server_sock)

	print 'server starts'

	while 1:
		# select readable sockets
		read_sockets, write_sockets, error_sockets = select.select(SOCKET_LIST, [], [], 0)

		for sock in read_sockets:
			# new connection
			if sock == server_sock:
				client_sock, addr = sock.accept()
				print '[server] new client accepted'
				SOCKET_LIST.append(client_sock)

			# receive message from client
			else:
				try:
					data = sock.recv(RECV_BUFFER)
					if data:
						print '[client] ' + data

						# handle user login
						if data == 'login':
							client_login(sock)

						# handle user register
						elif data == 'register':
							client_register(sock)

						# handle knock event
						elif data == 'knock':
							client_knock(sock)

						# client is talking
						else:
							# broadcast to anyone except master socket and this socket
							broadcast_data(sock, data)

				# handle client offline situation
				except:
					#print 'client offline'
					#sock.close()
					#SOCKET_LIST.remove(sock)
					continue
	server_sock.close()


