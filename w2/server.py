import socket
import threading
import time
import random


class ChatServer:
    def __init__(self, host='127.0.0.1', port=12346):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = {}
        self.colors = {}
        self.banned = []
        self.admin_nick = 'admin'
        self.games = {}  # For simple games like rps

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f'Server started on {self.host}:{self.port}')
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f'Connection from {client_address}')
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            nickname = client_socket.recv(1024).decode('utf-8')
            if nickname in self.banned:
                client_socket.send('당신은 밴되었습니다.'.encode('utf-8'))
                client_socket.close()
                return
            self.clients.append(client_socket)
            self.nicknames[client_socket] = nickname
            self.colors[client_socket] = '\033[0m'  # Default color
            self.broadcast(f'{nickname}님이 입장하셨습니다.', client_socket)
            self.send_help(client_socket)
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if message == '/종료':
                    self.remove_client(client_socket)
                    break
                elif message.startswith('/msg '):
                    self.whisper(message, client_socket)
                elif message.startswith('/help'):
                    self.send_help(client_socket)
                elif message.startswith('/list'):
                    self.send_user_list(client_socket)
                elif message.startswith('/nick '):
                    self.change_nickname(message, client_socket)
                elif message.startswith('/roll '):
                    self.roll_dice(message, client_socket)
                elif message.startswith('/time'):
                    self.send_time(client_socket)
                elif message.startswith('/color '):
                    self.change_color(message, client_socket)
                elif message.startswith('/kick '):
                    self.kick_user(message, client_socket)
                elif message.startswith('/ban '):
                    self.ban_user(message, client_socket)
                elif message.startswith('/unban '):
                    self.unban_user(message, client_socket)
                elif message.startswith('/game '):
                    self.handle_game(message, client_socket)
                else:
                    self.broadcast(f'{nickname}> {message}', client_socket)
        except:
            self.remove_client(client_socket)

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:
                try:
                    color = self.colors.get(client, '\033[0m')
                    client.send(f'{color}{message}\033[0m'.encode('utf-8'))
                except:
                    self.remove_client(client)

    def whisper(self, message, sender_socket):
        parts = message.split(' ', 2)
        if len(parts) < 3:
            sender_socket.send('귓속말 형식: /msg 닉네임 메시지'.encode('utf-8'))
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

    def send_help(self, client_socket):
        help_msg = """
사용 가능한 명령어:
- /help: 이 도움말 표시
- /list: 접속자 목록 표시
- /nick <새닉네임>: 닉네임 변경
- /msg <닉네임> <메시지>: 귓속말
- /roll <면수>: 주사위 굴림 (기본 6)
- /time: 현재 시간 표시
- /color <색상>: 메시지 색상 변경 (red, green, blue, yellow, magenta, cyan)
- /kick <닉네임>: 사용자 추방 (관리자만)
- /ban <닉네임>: 사용자 밴 (관리자만)
- /unban <닉네임>: 사용자 언밴 (관리자만)
- /game rps <선택>: 가위바위보 (rock, paper, scissors)
- /종료: 연결 종료
        """
        client_socket.send(help_msg.encode('utf-8'))

    def send_user_list(self, client_socket):
        user_list = '접속자 목록:\n' + '\n'.join(self.nicknames.values())
        client_socket.send(user_list.encode('utf-8'))

    def change_nickname(self, message, client_socket):
        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.send('닉네임 변경 형식: /nick 새닉네임'.encode('utf-8'))
            return
        new_nick = parts[1]
        old_nick = self.nicknames[client_socket]
        if new_nick in self.nicknames.values():
            client_socket.send('이미 사용중인 닉네임입니다.'.encode('utf-8'))
            return
        self.nicknames[client_socket] = new_nick
        self.broadcast(f'{old_nick}님이 {new_nick}으로 닉네임을 변경하셨습니다.', client_socket)
        client_socket.send(f'닉네임이 {new_nick}으로 변경되었습니다.'.encode('utf-8'))

    def roll_dice(self, message, client_socket):
        parts = message.split(' ', 1)
        sides = 6
        if len(parts) > 1:
            try:
                sides = int(parts[1])
            except:
                sides = 6
        result = random.randint(1, sides)
        nickname = self.nicknames[client_socket]
        self.broadcast(f'{nickname}님이 {sides}면 주사위를 굴렸습니다: {result}', client_socket)
        client_socket.send(f'주사위 결과: {result}'.encode('utf-8'))

    def send_time(self, client_socket):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        client_socket.send(f'현재 시간: {current_time}'.encode('utf-8'))

    def change_color(self, message, client_socket):
        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.send('색상 변경 형식: /color 색상'.encode('utf-8'))
            return
        color = parts[1].lower()
        color_codes = {
            'red': '\033[91m',
            'green': '\033[92m',
            'blue': '\033[94m',
            'yellow': '\033[93m',
            'magenta': '\033[95m',
            'cyan': '\033[96m'
        }
        if color in color_codes:
            self.colors[client_socket] = color_codes[color]
            client_socket.send(f'색상이 {color}으로 변경되었습니다.'.encode('utf-8'))
        else:
            client_socket.send('지원되는 색상: red, green, blue, yellow, magenta, cyan'.encode('utf-8'))

    def kick_user(self, message, client_socket):
        if self.nicknames[client_socket] != self.admin_nick:
            client_socket.send('관리자만 사용할 수 있습니다.'.encode('utf-8'))
            return
        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.send('추방 형식: /kick 닉네임'.encode('utf-8'))
            return
        target_nick = parts[1]
        for sock, nick in self.nicknames.items():
            if nick == target_nick:
                self.remove_client(sock)
                self.broadcast(f'{target_nick}님이 관리자에 의해 추방되었습니다.')
                return
        client_socket.send(f'{target_nick}님을 찾을 수 없습니다.'.encode('utf-8'))

    def ban_user(self, message, client_socket):
        if self.nicknames[client_socket] != self.admin_nick:
            client_socket.send('관리자만 사용할 수 있습니다.'.encode('utf-8'))
            return
        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.send('밴 형식: /ban 닉네임'.encode('utf-8'))
            return
        target_nick = parts[1]
        if target_nick not in self.banned:
            self.banned.append(target_nick)
            client_socket.send(f'{target_nick}님이 밴되었습니다.'.encode('utf-8'))
            for sock, nick in self.nicknames.items():
                if nick == target_nick:
                    self.remove_client(sock)
                    self.broadcast(f'{target_nick}님이 밴되었습니다.')
                    break
        else:
            client_socket.send(f'{target_nick}님은 이미 밴되었습니다.'.encode('utf-8'))

    def unban_user(self, message, client_socket):
        if self.nicknames[client_socket] != self.admin_nick:
            client_socket.send('관리자만 사용할 수 있습니다.'.encode('utf-8'))
            return
        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.send('언밴 형식: /unban 닉네임'.encode('utf-8'))
            return
        target_nick = parts[1]
        if target_nick in self.banned:
            self.banned.remove(target_nick)
            client_socket.send(f'{target_nick}님의 밴이 해제되었습니다.'.encode('utf-8'))
        else:
            client_socket.send(f'{target_nick}님은 밴되지 않았습니다.'.encode('utf-8'))

    def handle_game(self, message, client_socket):
        parts = message.split(' ', 2)
        if len(parts) < 2:
            client_socket.send('게임 형식: /game rps <rock|paper|scissors>'.encode('utf-8'))
            return
        game_type = parts[1]
        if game_type == 'rps':
            if len(parts) < 3:
                client_socket.send('가위바위보 형식: /game rps <rock|paper|scissors>'.encode('utf-8'))
                return
            choice = parts[2].lower()
            if choice not in ['rock', 'paper', 'scissors']:
                client_socket.send('선택: rock, paper, scissors'.encode('utf-8'))
                return
            server_choice = random.choice(['rock', 'paper', 'scissors'])
            nickname = self.nicknames[client_socket]
            result = self.determine_rps_winner(choice, server_choice)
            self.broadcast(f'{nickname}님이 가위바위보를 했습니다: {choice} vs {server_choice} - {result}', client_socket)
            client_socket.send(f'결과: {choice} vs {server_choice} - {result}'.encode('utf-8'))

    def determine_rps_winner(self, user, server):
        if user == server:
            return '무승부'
        elif (user == 'rock' and server == 'scissors') or \
             (user == 'paper' and server == 'rock') or \
             (user == 'scissors' and server == 'paper'):
            return '승리'
        else:
            return '패배'

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            nickname = self.nicknames[client_socket]
            self.clients.remove(client_socket)
            del self.nicknames[client_socket]
            if client_socket in self.colors:
                del self.colors[client_socket]
            client_socket.close()
            self.broadcast(f'{nickname}님이 퇴장하셨습니다.')


if __name__ == '__main__':
    server = ChatServer()
    server.start_server()
