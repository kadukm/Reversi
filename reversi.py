import argparse
import time
import socket

from threading import Thread

from modules import ConsoleUI as consUI
from modules.ChipType import ChipType
from modules.EndGame import EndGame
from modules.GameModel import GameModel
from modules.GameType import GameType
from modules.MoveError import MoveError
from modules.Server import Server


MAX_DATA_LEN = 1024


def main():
    parser = argparse.ArgumentParser()
    set_parser(parser)
    args = parser.parse_args()
    game_type = get_game_type(args)

    if game_type == GameType.Offline:
        game_args = parse_args_for_game(args)
        play_offline(GameModel(*game_args), parse_ai_chiptype(args))
    elif game_type == GameType.Online_server:
        game_args = parse_args_for_game(args)
        play_online(args.port, args.address, GameModel(*game_args))
    else:
        play_online(args.port, args.address)


def play_online(port, address, game=None):
    if port is not None:
        server = Server(port, game)
        server_thread = Thread(target=server.start)
        server_thread.start()
        address = server.host
    else:
        address, port = parse_address(address)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((address, port))

    while True:
        data = client_socket.recv(MAX_DATA_LEN).decode()
        if data == 'GET':
            str_move = ""
            while not str_move:
                str_move = input('Ваш ход: ')
            client_socket.send(str_move.encode())
        elif data == 'END':
            break
        else:
            print(data)

    client_socket.close()


def parse_address(address):
    res_address, str_port = address.split(':')
    port = int(str_port)
    return res_address, port


def play_offline(game, ai_chiptype):
    while True:
        try:
            print(consUI.get_cur_condition(game))
            if ai_chiptype == game.get_cur_chip_type:
                make_move_by_ai(game)
            else:
                make_move_by_human(game)
        except MoveError as e:
            print(str(e))
        except EndGame:
            print(consUI.get_cur_condition(game))
            answer = input('Хотите сыграть еще раз с такими же '
                           'игровыми параметрами (y/N)? ')
            if answer.lower() == 'y':
                game = GameModel(game.width, game.height, game.rocks_count)
                continue
            else:
                break


def make_move_by_human(game):
    str_move = input('Ваш ход: ')
    move = Server.parse_str_move(str_move)
    game.make_move_to(move)


def make_move_by_ai(game):
    for move in game.available_moves:
        time.sleep(3)
        print('Ход ИИ: ' + str(move)[1:-1])
        game.make_move_to(move)
        break


def set_parser(parser):
    parser.add_argument('-s', '--size', type=str, help='set size of the game')
    parser.add_argument("-r", "--rocks", action="count", default=0,
                        help='add rocks to the game')
    chiptype_group = parser.add_mutually_exclusive_group()
    chiptype_group.add_argument('-b', '--black', action='store_true',
                                help='enemy\'s side')
    chiptype_group.add_argument('-w', '--white', action='store_true',
                                help='enemy\'s side')
    gametype_group = parser.add_mutually_exclusive_group()
    gametype_group.add_argument('-a', '--ai', action='store_true',
                                help='game with artificial intelligence')
    gametype_group.add_argument('-n', '--newgame', dest='port', type=int,
                                help='create new online-game')
    gametype_group.add_argument('-c', '--connect', dest='address', type=str,
                                help='connect to existing online-game')


def parse_ai_chiptype(args):
    if (args.black or args.white) and not args.ai:
        raise Exception('Нельзя указывать сторону для ИИ, '
                        'при этом не играя против ИИ')
    elif args.black:
        return ChipType.Black
    elif args.ai:
        return ChipType.White
    else:
        return None


def parse_args_for_game(args):
    width, height, rocks_count = 8, 8, 0
    if args.size is not None:
        size_str = args.size.split('x')
        width = int(size_str[0])
        height = int(size_str[1])
    if args.rocks is not None:
        rocks_count = args.rocks
    return width, height, rocks_count


def get_game_type(args):
    if args.port is not None:
        return GameType.Online_server
    elif args.address is not None:
        return GameType.Online_connect
    else:
        return GameType.Offline


if __name__ == '__main__':
    main()
