import socket
import time
from . import ConsoleUI as consUI
from .ChipType import ChipType
from .EndGame import EndGame
from .MoveError import MoveError


MAX_DATA_LEN = 1024


class Server:
    def __init__(self, port, game):
        self.game = game
        self.port = port
        self.host = socket.gethostbyname(socket.gethostname())
        self.clients = {}
        self._init_socket()

    def _init_socket(self):
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        self.socket.listen(2)

    def start(self):
        conn_b, addr_b = self.socket.accept()
        self.clients[ChipType.Black] = conn_b
        conn_b.send(('Вы успешно подключились к серверу '
                     + str(self.host) + ':' + str(self.port) +
                    '. Пожалуйста, дождитесь подключения соперника.').encode())
        conn_w, addr_w = self.socket.accept()
        self.clients[ChipType.White] = conn_w
        conn_w.send(('Вы успешно подключились к серверу '
                     + str(self.host) + ':' + str(self.port) +
                    '. Ваш противник к серверу уже подключился').encode())
        conn_b.send('Игра началась. Вы будете играть за черных. Удачи!'
                    .encode())
        conn_w.send('Игра началась. Вы будете играть за белых. Удачи!'
                    .encode())
        time.sleep(0.1)

        self.start_game()

        conn_b.close()
        conn_w.close()
        self.socket.close()

    def start_game(self):
        while True:
            try:
                self.send_cur_game_condition()
                self.make_move_by(self.clients[self.game.get_cur_chip_type])
            except EndGame:
                self.tell_clients_about_ending()
                break

    def make_move_by(self, conn):
        while True:
            try:
                conn.send('GET'.encode())
                str_move = conn.recv(MAX_DATA_LEN).decode()
                move = self.parse_str_move(str_move)
                self.game.make_move_to(move)
                break
            except MoveError as e:
                conn.send(str(e).encode())

    def send_cur_game_condition(self):
        encoded_cur_condition = consUI.get_cur_condition(self.game).encode()
        self.clients[ChipType.Black].send(encoded_cur_condition)
        self.clients[ChipType.White].send(encoded_cur_condition)

    def tell_clients_about_ending(self):
        res_msg_list = []
        res_msg_list.append(consUI.get_cur_condition(self.game))
        res_msg_list.append('Спасибо за игру!')
        res_encoded_msg = ''.join(res_msg_list).encode()
        self.clients[ChipType.Black].send(res_encoded_msg)
        self.clients[ChipType.White].send(res_encoded_msg)
        time.sleep(3)
        self.clients[ChipType.Black].send('END'.encode())
        self.clients[ChipType.White].send('END'.encode())

    @staticmethod
    def parse_str_move(str_move):
        try:
            first_num = ''
            sec_num = ''
            first_num_found = False
            for c in str_move:
                if c.isdigit():
                    if first_num_found:
                        sec_num += c
                    else:
                        first_num += c
                elif len(sec_num) == 0:
                    first_num_found = True
            x = int(first_num)
            y = int(sec_num)
            return x, y
        except Exception:
            raise MoveError(
                'Невозможно распознать ход. Проверьте качество ввода')
