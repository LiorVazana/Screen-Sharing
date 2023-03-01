import socket


class StreamingServer:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__users_dict = {}
        self.__last_id = 0
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__server_socket.bind((self.__host, self.__port))

    def serve(self) -> None:
        while True:
            peer_msg, peer_addr = self.__server_socket.recvfrom(1024)

            if peer_msg.decode() == 'Sharing':  # Create screen share
                self.__users_dict[f'{self.__last_id}'] = peer_addr
                # Send back his id
                self.__server_socket.sendto(f'{self.__last_id}'.encode(), peer_addr)
                self.__last_id += 1
            elif peer_msg.decode() in self.__users_dict:  # Connect to screen share
                self.__users_dict[str(self.__last_id)] = peer_addr
                self.__server_socket.sendto(f'{peer_addr}'.encode(), self.__users_dict[peer_msg.decode()])
                self.__server_socket.sendto(f'{self.__users_dict[peer_msg.decode()]}'.encode(), peer_addr)
                self.__last_id += 1
            else:  # Unknown ID
                print('Unknown ID')


def main():
    server = StreamingServer('192.168.7.17', 45795)
    server.serve()


if __name__ == '__main__':
    main()
