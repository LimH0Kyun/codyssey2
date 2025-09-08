import socket
import threading
import os
import time


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # ANSI escape codes for colors
            print(message)
        except:
            print('연결이 끊어졌습니다.')
            client_socket.close()
            break


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            # ANSI escape codes for colors
            print(message)
        except:
            print('연결이 끊어졌습니다. 재연결을 시도합니다...')
            client_socket.close()
            break


def main():
    # Enable ANSI colors in Windows
    if os.name == 'nt':
        os.system('color')
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 12345))
            nickname = input('닉네임을 입력하세요: ')
            client_socket.send(nickname.encode('utf-8'))
            threading.Thread(target=receive_messages, args=(client_socket,)).start()
            print('채팅을 시작합니다. /help로 명령어 확인.')
            while True:
                message = input()
                if message == '/종료':
                    client_socket.send(message.encode('utf-8'))
                    break
                client_socket.send(message.encode('utf-8'))
            client_socket.close()
            break  # 정상 종료
        except ConnectionRefusedError:
            print('서버에 연결할 수 없습니다. 5초 후 재시도합니다...')
            time.sleep(5)
        except KeyboardInterrupt:
            print('클라이언트를 종료합니다.')
            break


if __name__ == '__main__':
    main()
