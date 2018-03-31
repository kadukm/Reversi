from .ChipType import ChipType
from .Chip import Chip
from .MoveError import MoveError
from .EndGame import EndGame
from .RocksError import RocksError
import random


class GameModel:
    def __init__(self, width=8, height=8, rocks_count=0):
        self.width = width
        self.height = height
        self.rocks_count = rocks_count
        self.cur_player_is_black = True
        self.is_running = True
        self.map = {}
        self.score = {}
        self.border_moves = set()
        self.available_moves = set()
        self._init_map()
        self._init_score()
        self._init_beginning()
        self._init_rocks()

    def _init_map(self):
        if self.width < 2 or self.height < 2 or self.width + self.height == 4:
            raise Exception('Слишком маленькие размеры игрового поля')
        for x in range(self.width):
            for y in range(self.height):
                self.map[x, y] = None

    def _init_score(self):
        self.score[ChipType.Black] = 2
        self.score[ChipType.White] = 2

    def _init_beginning(self):
        x = self.width // 2 - 1
        y = self.height // 2 - 1
        if self.width <= 8 or self.height <= 8:
            self.map[x, y] = Chip(ChipType.White)
            self.map[x + 1, y + 1] = Chip(ChipType.White)
            self.map[x + 1, y] = Chip(ChipType.Black)
            self.map[x, y + 1] = Chip(ChipType.Black)
        else:
            self.map[x, y] = Chip(ChipType.White)
            self.map[x + 1, y] = Chip(ChipType.White)
            self.map[x, y + 1] = Chip(ChipType.Black)
            self.map[x + 1, y + 1] = Chip(ChipType.Black)
        self._init_border_moves()
        self._upd_available_moves()

    def _init_rocks(self):
        if self.rocks_count == 0:
            return
        all_poss = {
            (x, y) for x in range(self.width) for y in range(self.height)}
        available_poss = all_poss.difference(self.available_moves)
        for x in range(self.width // 2 - 1, self.width // 2 + 1):
            for y in range(self.height // 2 - 1, self.height // 2 + 1):
                available_poss.remove((x, y))
        if len(available_poss) < self.rocks_count:
            raise RocksError("Кол-во камней больше, чем места для них")
        rock_poss = random.sample(available_poss, self.rocks_count)
        for rock_pos in rock_poss:
            self.map[rock_pos] = Chip(ChipType.Rock)
            if rock_pos in self.border_moves:
                self.border_moves.remove(rock_pos)

    def _init_border_moves(self):
        x = self.width // 2 - 2
        y = self.height // 2 - 2
        for dx in range(4):
            for dy in range(4):
                if (self.map_contains((x + dx, y + dy))
                        and self.map[x + dx, y + dy] is None):
                    self.border_moves.add((x + dx, y + dy))

    def _upd_border_moves_with(self, move):
        x, y = move
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if (self.map_contains((x + dx, y + dy)) and
                        self.map[x + dx, y + dy] is None):
                    self.border_moves.add((x + dx, y + dy))
        self.border_moves.remove((x, y))

    def map_contains(self, point):
        return point in self.map

    def _upd_available_moves(self):
        self.available_moves.clear()
        for cur_move in self.border_moves:
            if self.move_is_correct_at(cur_move):
                self.available_moves.add(cur_move)

    def move_is_correct_at(self, point):
        if not self.map_contains(point):
            raise MoveError('Ход выходит за пределы игрового поля')
        x, y = point
        cur_type = self.get_cur_chip_type
        enemy_type = self.get_enemy_chip_type
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    cur_x = x + dx
                    cur_y = y + dy
                    enemy_exists = False
                    while (self.map_contains((cur_x, cur_y)) and
                           self.map[cur_x, cur_y] is not None and
                           self.map[cur_x, cur_y].type == enemy_type):
                        cur_x += dx
                        cur_y += dy
                        enemy_exists = True
                    if (not self.map_contains((cur_x, cur_y)) or
                            self.map[cur_x, cur_y] is None):
                        continue
                    if self.map[cur_x, cur_y].type == cur_type and enemy_exists:
                        return True
        return False

    def make_move_to(self, point):
        if point not in self.available_moves:
            raise MoveError('Неверная позиция для хода')
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx != 0 or dy != 0:
                    self.check_direction(point, dx, dy)
        self.score[self.get_cur_chip_type] += 1
        self.map[point] = Chip(self.get_cur_chip_type)
        self._upd_border_moves_with(point)
        self.upd_condition()

    def upd_condition(self):
        self.cur_player_is_black = not self.cur_player_is_black
        self._upd_available_moves()
        if len(self.available_moves) == 0:
            self.cur_player_is_black = not self.cur_player_is_black
            self._upd_available_moves()
            if len(self.available_moves) == 0:
                self.is_running = False
                raise EndGame('Доступных ходов нет. Игра закончена')

    def check_direction(self, point, dx, dy):
        x, y = point
        self._direction_is_right((x + dx, y + dy), dx, dy)

    def _direction_is_right(self, point, dx, dy):
        if not self.map_contains(point) or self.map[point] is None:
            return False
        elif self.map[point].type == self.get_cur_chip_type:
            return True
        elif self.map[point].type == self.get_enemy_chip_type:
            success = self._direction_is_right((point[0] + dx, point[1] + dy),
                                               dx, dy)
            if success:
                self.map[point].reverse()
                self.score[self.get_cur_chip_type] += 1
                self.score[self.get_enemy_chip_type] -= 1
            return success

    @property
    def get_cur_chip_type(self):
        return ChipType.Black if self.cur_player_is_black else ChipType.White

    @property
    def get_enemy_chip_type(self):
        return ChipType.White if self.cur_player_is_black else ChipType.Black
