from socket import *


class SocketListener:

    @staticmethod
    def listen_socket():
        udp_sock = socket(AF_INET, SOCK_DGRAM)
        udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        udp_sock.bind(("255.255.255.255", 2018))
        while True:
            data, address = udp_sock.recvfrom(2018)
            if not data: break
            print(data, address)
        udp_sock.close()


SocketListener.listen_socket()