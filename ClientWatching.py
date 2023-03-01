import socket
import cv2
import pickle
import struct
import threading
import time

class ClientWatching:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__remote_peer_tuple = ()
        self.__peer_socket = socket.socket()
        self.__is_watching = False
        self.__chunk_size = 4096

    def establish_p2p_connection(self, init_msg: str) -> None:
        # Create socket between first peer to server
        self.__peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Add NTT record by sending packet to the server
        self.__peer_socket.sendto(init_msg.encode(), (self.__host, self.__port))

        print(f'send to the server {init_msg}')

        # Get the second peer's external host and port
        remote_peer_tuple_bytes, server_addr = self.__peer_socket.recvfrom(1024)
        self.__remote_peer_tuple = eval(remote_peer_tuple_bytes.decode())  # (host, port)

        print(f'received from server {self.__remote_peer_tuple}')

        hole_punched = threading.Event()
        punch_hole_thread = threading.Thread(target=self.punch_hole, args=(hole_punched,))
        punch_hole_thread.start()

        msg, addr = self.__peer_socket.recvfrom(1024)
        self.__peer_socket.sendto(b'ACK', self.__remote_peer_tuple)

        hole_punched.set()

        while self.__peer_socket.recvfrom(1024)[0] == b'Punch Hole':
            pass

    def punch_hole(self, stop_event: threading.Event):
        while not stop_event.wait(1):
            self.__peer_socket.sendto(b'Punch Hole', self.__remote_peer_tuple)

            time.sleep(1)

    def show_stream(self, peer_id: str) -> None:
        self.establish_p2p_connection(peer_id)

        payload_size = struct.calcsize('>L')

        self.__is_watching = True

        self.__peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 650000000)

        while self.__is_watching:
            packed_msg_size, addr = self.__peer_socket.recvfrom(payload_size)
            if packed_msg_size == b'':
                self.__peer_socket.close()
                break

            msg_size = struct.unpack(">L", packed_msg_size)[0]

            print(f'the size given is: {msg_size}')

            frame_data = b""

            while len(frame_data) < msg_size:
                chunk_size = self.__chunk_size if msg_size - len(frame_data) > self.__chunk_size else msg_size - len(
                    frame_data)
                frame_data += self.__peer_socket.recv(chunk_size)

            print(f'the frame length is: {len(frame_data)}')

            frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow('VAZANA\'s screen share', frame)

            if cv2.waitKey(1) == ord('q'):
                self.__peer_socket.close()
                break


def main():
    watching_client = ClientWatching('192.168.7.17', 45795)
    watching_client.show_stream(input('Enter the stream ID: '))


if __name__ == '__main__':
    main()
