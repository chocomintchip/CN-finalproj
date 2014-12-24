import select
import socket
import sys

HOST = ''
PORT = 12345
SOCKET_LIST = []
RECV_BUFFER = 4096
USERNAME = ''

if __name__ == '__main__':

	client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# client_sock.settimeout(10)

	try:
		client_sock.connect((HOST, PORT))
	except:
		print 'connect error'
		sys.exit()

	print 'client connected to server'

	# login / register

	login = False
	print 'enter \'login\' or \'register\' to continue'

	while 1:
		if login:
			SOCKET_LIST = [sys.stdin, client_sock]
		else:
			SOCKET_LIST = [sys.stdin]

		# select readable sockets
		read_sockets, write_sockets, error_sockets = select.select(SOCKET_LIST, [], [], 0)

		for sock in read_sockets:
			# receive message from server
			if sock == client_sock:
				data = sock.recv(RECV_BUFFER)
				if data:
					print '[server] ' + data
				else:
					print '[server] disconnected from server'
					sys.exit()

			# user enter message
			else:
				data = sys.stdin.readline().strip('\n')
				# send login request
				if not login:
					if data == 'login':
						client_sock.send('login')

						print 'enter username:'
						client_username = sys.stdin.readline().strip('\n')
						client_sock.send(client_username)

						print 'enter password:'
						client_password = sys.stdin.readline().strip('\n')
						client_sock.send(client_password)

						login_status = client_sock.recv(RECV_BUFFER)
						if login_status == 'login success':
							USERNAME = client_username
							login = True
						print '[server] ' + login_status

					# send register request
					elif data == 'register':
						client_sock.send('register')

						print 'enter username:'
						client_username = sys.stdin.readline().strip('\n')
						client_sock.send(client_username)
						
						print 'enter password:'
						client_password = sys.stdin.readline().strip('\n')
						client_sock.send(client_password)
						
						register_status = client_sock.recv(RECV_BUFFER)
						print '[server] ' + register_status

				# already login
				else:
					if data == 'knock':
						client_sock.send('knock')

						print 'enter knock username:'
						knock_username = sys.stdin.readline().strip('\n')
						client_sock.send(knock_username)

						knock_result = client_sock.recv(RECV_BUFFER)
						print '[server] ' + knock_result
						
					else:
						client_sock.send(USERNAME + '> ' + data)

	client_sock.close()


