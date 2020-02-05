import socket, threading, time, json, re

key = 8194

shutdown = False
join = True


def receving(name, sock):
	global join
	while not shutdown:
		try:
			while True:
				bytes, addr = sock.recvfrom(1024)
				json_string = bytes.decode("utf-8")
				data = json.loads(json_string)
				if "event" in data:
					if data["event"] == "timeout":
						print(data["message"])
						if data['who'] == alias:
							join = False
							print("Enter to resume")

					elif data['event'] == 'cmd':
						print(f"cmd: {data['cmd']}\n")
						print(data["message"])
				else:
					print(data["message"])

				# # Begin
				# decrypt = ""; k = False
				# for i in data.decode("utf-8"):
				# 	if i == ":":
				# 		k = True
				# 		decrypt += i
				# 	elif k == False or i == " ":
				# 		decrypt += i
				# 	else:
				# 		decrypt += chr(ord(i)^key)
				# print(data.decode("utf-8"))
				# # End

				time.sleep(0.2)
		except:
			pass


host = socket.gethostbyname(socket.gethostname())
# host = "localhost"
port = 0

server = (host, 9091)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
# s.setblocking(0)

alias = input("Name: ")

rT = threading.Thread(target=receving, args=("RecvThread", s))
rT.start()


def encode_pair(dict):
	return json.dumps(dict).encode("utf-8")


def send_to_server(dict):
	s.sendto(encode_pair({'name': alias, **dict}), server)


def send_cmd(cmd_type, cmd_message=None):
	d = {'event': 'cmd', 'cmd': cmd_type}
	if cmd_message is not None:
		d['message'] = cmd_message
	send_to_server(d)


def onresume():
	global join
	if not join:
		join = True if not shutdown else join
		send_cmd("resume")


send_to_server({"event": "cmd", "cmd": 'resume'})

while not shutdown:
	try:
		message = input().strip()

		# # Begin
		# crypt = ""
		# for i in message:
		# 	crypt += chr(ord(i)^key)
		# message = crypt
		# # End
		if re.match(r"^[/\\!]", message):
			cmd = message[1:]
			if cmd == "quit":
				shutdown = True
				# print(join)
				if join == True:
					join = False
					send_cmd(cmd)
			elif cmd == 'pause':
				if join == True:
					send_cmd(cmd)
			else:
				onresume()
				send_cmd(cmd)
		else:
			if not join:
				join = True
				send_cmd("resume")
			elif message != '':
				send_to_server({"message": message})
			elif message == '':
				send_cmd("i'm_here")

		time.sleep(0.2)
	except Exception as e:
		print(e)
		shutdown = True
if join == True:
	send_to_server({"event": "cmd", 'cmd': 'quit'})
s.close()
rT.join()
