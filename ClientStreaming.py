import socket
import numpy as np
import pyautogui
import cv2
import pickle
import struct
import threading
import time


class ClientStreaming:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__remote_peer_tuple = ()
        self.__peer_socket = socket.socket()
        self.__id = 0
        self.__encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.__is_streaming = False
        self.__x_res, self.__y_res = pyautogui.size()#(1024, 576)
        self.__chunk_size = 4096

    def stream(self) -> None:
        self.establish_p2p_connection('Sharing')

        self.__is_streaming = True

        while self.__is_streaming:
            current_frame = self._get_frame()
            result, current_frame = cv2.imencode('.jpg', current_frame, self.__encoding_parameters)
            data = pickle.dumps(current_frame, 0)
            size = len(data)

            print(f'sent size: {size}')

            try:
                self.__peer_socket.sendto(struct.pack('>L', size), self.__remote_peer_tuple)
                for i in range(0, size, self.__chunk_size):
                    self.__peer_socket.sendto(data[i:i + self.__chunk_size], self.__remote_peer_tuple)
            except Exception as e:
                print(e)
                self.__is_streaming = False

        cv2.destroyAllWindows()

    def establish_p2p_connection(self, init_msg: str) -> None:
        # Create socket between first peer to server
        self.__peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Add NTT record by sending packet to the server
        self.__peer_socket.sendto(init_msg.encode(), (self.__host, self.__port))

        print(f'send to the server {init_msg}')

        # Get the stream ID
        remote_peer_tuple_bytes, server_addr = self.__peer_socket.recvfrom(1024)
        self.__id = eval(remote_peer_tuple_bytes.decode())

        print(f'Your id is: {self.__id}')

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

    def _get_frame(self):
        print('got frame')
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_res, self.__y_res), interpolation=cv2.INTER_AREA)
        return frame


def main():
    streaming_client = ClientStreaming('192.168.7.17', 45795)
    streaming_client.stream()


if __name__ == '__main__':
    main()
