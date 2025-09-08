import socket
import threading


class ChatServer:
    def __init__(self, host='127.0.0.1', port=12346):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = {}

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f'Server started on {self.host}:{self.port}')
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Connection from {client_address}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        nickname = client_socket.recv(1024).decode('utf-8')
        self.clients.append(client_socket)
        self.nicknames[client_socket] = nickname
        self.broadcast(f'{nickname}님이 입장하셨습니다.', client_socket)
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message == '/종료':
                    self.remove_client(client_socket)
                    break
                elif message.startswith('/w '):
                    self.whisper(message, client_socket)
                else:
                    self.broadcast(f'{nickname}> {message}', client_socket)
            except:
                self.remove_client(client_socket)
                break

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    self.remove_client(client)

    def whisper(self, message, sender_socket):
        parts = message.split(' ', 2)
        if len(parts) < 3:
            sender_socket.send('귓속말 형식: /w 닉네임 메시지'.encode('utf-8'))
            return
        target_nickname = parts[1]
        whisper_message = parts[2]
        sender_nickname = self.nicknames[sender_socket]
        for client, nickname in self.nicknames.items():
            if nickname == target_nickname:
                try:
                    client.send(f'[귓속말 from {sender_nickname}] {whisper_message}'.encode('utf-8'))
                    sender_socket.send(f'[귓속말 to {target_nickname}] {whisper_message}'.encode('utf-8'))
                except:
                    self.remove_client(client)
                return
        sender_socket.send(f'{target_nickname}님을 찾을 수 없습니다.'.encode('utf-8'))

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            nickname = self.nicknames[client_socket]
            self.clients.remove(client_socket)
            del self.nicknames[client_socket]
            client_socket.close()
            self.broadcast(f'{nickname}님이 퇴장하셨습니다.')


if __name__ == '__main__':
    server = ChatServer()
    server.start_server()
