import socket
import threading


def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print('연결이 끊어졌습니다.')
            client_socket.close()
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12346))
    nickname = input('닉네임을 입력하세요: ')
    client_socket.send(nickname.encode('utf-8'))
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    while True:
        message = input()
        if message == '/종료':
            client_socket.send(message.encode('utf-8'))
            break
        client_socket.send(message.encode('utf-8'))
    client_socket.close()


if __name__ == '__main__':
    main()
