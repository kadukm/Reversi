import sys
import unittest
import copy
sys.path.append('..')
from modules.GameModel import GameModel
from modules.ChipType import ChipType
from modules.EndGame import EndGame
from modules.MoveError import MoveError
from modules.RocksError import RocksError


class CheckBeginning(unittest.TestCase):
    def test_too_small_size(self):
        self._check_too_small_size(2, 2)
        self._check_too_small_size(1, 8)
        self._check_too_small_size(9, 1)

    def test_standard_size(self):
        game = GameModel()
        self.assertTrue(game.height == game.width == 8)
        self.assertTrue(game.map[3, 3].type ==
                        game.map[4, 4].type ==
                        ChipType.White)
        self.assertTrue(game.map[3, 4].type ==
                        game.map[4, 3].type ==
                        ChipType.Black)

    def test_scores(self):
        game = GameModel()
        self.assertTrue(game.score[ChipType.White] ==
                        game.score[ChipType.Black] == 2)

    def test_small_size_cases(self):
        self._check_small_size_case(7, 7)
        self._check_small_size_case(5, 8)
        self._check_small_size_case(4, 3)
        self._check_small_size_case(3, 2)
        self._check_small_size_case(8, 9)
        self._check_small_size_case(10000, 2)

    def test_large_size_cases(self):
        self._check_large_size_case(10, 10)
        self._check_large_size_case(100, 2341)
        self._check_large_size_case(1000, 9)

    def test_border_moves_count(self):
        self._check_border_moves_count_case(4, 4, 12)
        self._check_border_moves_count_case(5, 5, 12)
        self._check_border_moves_count_case(4, 10, 12)
        self._check_border_moves_count_case(100, 1213, 12)
        self._check_border_moves_count_case(100, 2, 4)
        self._check_border_moves_count_case(3, 123, 8)

    def test_border_moves_existence(self):
        self._check_border_moves_existence_case(3, 8)
        self._check_border_moves_existence_case(100, 100)
        self._check_border_moves_existence_case(123, 4)

    def _check_too_small_size(self, width, height):
        with self.assertRaises(Exception):
            game = GameModel(width, height)

    def _check_border_moves_existence_case(self, width, height):
        game = GameModel(width, height)
        for x0 in range(width):
            for y0 in range(height):
                if game.map_contains((x0, y0)) and game.map[x0, y0] is not None:
                    for dx in range(-1, 2):
                        for dy in range(-1, 2):
                            x1 = x0 + dx
                            y1 = y0 + dy
                            if (game.map_contains((x1, y1))
                                    and game.map[x1, y1] is None):
                                self.assertTrue((x1, y1) in game.border_moves)

    def _check_border_moves_count_case(self, width, height, exp_res):
        game = GameModel(width, height)
        self.assertEqual(len(game.border_moves), exp_res)

    def _check_small_size_case(self, height, width):
        game = GameModel(width, height)
        x = width // 2 - 1
        y = height // 2 - 1
        self.assertEqual(game.width, width)
        self.assertEqual(game.height, height)
        self.assertTrue(game.map[x, y].type ==
                        game.map[x + 1, y + 1].type ==
                        ChipType.White)
        self.assertTrue(game.map[x, y + 1].type ==
                        game.map[x + 1, y].type ==
                        ChipType.Black)

    def _check_large_size_case(self, height, width):
        game = GameModel(width, height)
        x = width // 2 - 1
        y = height // 2 - 1
        self.assertEqual(game.width, width)
        self.assertEqual(game.height, height)
        self.assertTrue(game.map[x, y].type ==
                        game.map[x + 1, y].type ==
                        ChipType.White)
        self.assertTrue(game.map[x, y + 1].type ==
                        game.map[x + 1, y + 1].type ==
                        ChipType.Black)


class CheckAvailableMoves(unittest.TestCase):
    def test_first_moves(self):
        game = GameModel()
        self.assertTrue((3, 2) in game.available_moves)
        self.assertFalse((4, 2) in game.available_moves)
        game.make_move_to((3, 2))
        self.assertTrue((4, 2) in game.available_moves)
        self.assertFalse((3, 2) in game.available_moves)

    def test_beginning_count(self):
        self._check_count(8, 8, 4)
        self._check_count(7, 5, 4)
        self._check_count(100, 2, 2)
        self._check_count(20, 25, 4)

    def test_small_field_count(self):
        game = GameModel(3, 2)
        self.assertEqual(1, len(game.available_moves))
        self.assertTrue((2, 1) in game.available_moves)
        self.assertFalse((2, 0) in game.available_moves)
        game.make_move_to((2, 1))
        self.assertEqual(1, len(game.available_moves))
        self.assertFalse((2, 1) in game.available_moves)
        self.assertTrue((2, 0) in game.available_moves)

    def test_moves_count_cant_be_zero(self):
        with self.assertRaises(EndGame):
            game = GameModel(3, 2)
            game.make_move_to((2, 1))
            game.make_move_to((2, 0))

    def test_particular_moves(self):
        self.assertTrue(self._check_particular_move(10, 10, (4, 3)))
        self.assertFalse(self._check_particular_move(10, 10, (4, 4)))

    def test_incorrect_moves(self):
        with self.assertRaises(MoveError):
            self._check_particular_move(23, 44, (100, 100))
        with self.assertRaises(MoveError):
            self._check_particular_move(9, 24, (0, -1))

    def _check_count(self, width, height, exp_res):
        game = GameModel(width, height)
        self.assertEqual(exp_res, len(game.available_moves))

    @staticmethod
    def _check_particular_move(width, height, move):
        game = GameModel(width, height)
        return game.move_is_correct_at(move)


class CheckUpdBorderMoves(unittest.TestCase):
    def test_first_moves(self):
        self._check_first_move_case(8, 8, (3, 2), [(2, 1), (3, 1), (4, 1)])
        self._check_first_move_case(10, 2, (3, 0), [(2, 0), (2, 1)])
        self._check_first_move_case(5, 5, (2, 3), [(1, 4), (2, 4), (3, 4)])

    def test_case_without_new_border_moves(self):
        game = GameModel(4, 4)
        prev_border_moves = copy.deepcopy(game.border_moves)
        game.make_move_to((3, 2))
        new_border_moves = game.border_moves
        self.assertNotEqual(len(prev_border_moves), len(new_border_moves))
        for move in new_border_moves:
            self.assertTrue(move in prev_border_moves)

    def test_big_case(self):
        game = GameModel()
        new_moves = [(3, 2),
                     (2, 2),
                     (5, 4),
                     (4, 2),
                     (3, 1),
                     (4, 5),
                     (5, 3)]
        new_border_moves = [[(2, 1), (3, 1), (4, 1)],
                            [(1, 1), (1, 2), (1, 3)],
                            [(6, 3), (6, 4), (6, 5)],
                            [(5, 1)],
                            [(2, 0), (3, 0), (4, 0)],
                            [(3, 6), (4, 6), (5, 6)],
                            [(6, 2)]]
        for i in range(len(new_moves)):
            game.make_move_to(new_moves[i])
            self._check_particular_move(game, new_moves[i], new_border_moves[i])

    def _check_first_move_case(self, width, height, move, new_moves):
        game = GameModel(width, height)
        game.make_move_to(move)
        self._check_particular_move(game, move, new_moves)

    def _check_particular_move(self, game, move, new_moves):
        self.assertFalse(move in game.border_moves)
        for cur_move in new_moves:
            self.assertTrue(cur_move in game.border_moves)


class CheckScore(unittest.TestCase):
    def test_beginnings(self):
        self._check_start_state_case(8, 8)
        self._check_start_state_case(5, 5)
        self._check_start_state_case(100, 3)
        self._check_start_state_case(6, 79)

    def test_first_moves(self):
        self._check_first_move(8, 8, (3, 2))
        self._check_first_move(15, 4, (6, 0))
        self._check_first_move(17, 19, (7, 7))
        self._check_first_move(50, 40, (24, 18))

    def test_two_directions(self):
        game = GameModel()
        moves = [(3, 2), (2, 2), (2, 3), (4, 2)]
        for i in range(len(moves) - 1):
            game.make_move_to(moves[i])
        prev_white_score = game.score[ChipType.White]
        game.make_move_to(moves[len(moves) - 1])
        cur_white_score = game.score[ChipType.White]
        self.assertEqual(cur_white_score - prev_white_score, 3)

    def test_long_reversed_sequence(self):
        game = GameModel()
        moves = [(3, 2), (2, 2), (2, 3), (4, 2), (5, 5), (6, 6)]
        for i in range(len(moves) - 1):
            game.make_move_to(moves[i])
        prev_white_score = game.score[ChipType.White]
        game.make_move_to(moves[len(moves) - 1])
        cur_white_score = game.score[ChipType.White]
        self.assertEqual(cur_white_score - prev_white_score, 4)

    def test_big_case(self):
        game = GameModel()
        moves = [(3, 2), (2, 2), (5, 4), (4, 2), (3, 1), (4, 5), (5, 3)]
        white_scores = [1, 3, 2, 4, 2, 5, 3]
        black_scores = [4, 3, 5, 4, 7, 5, 8]
        for i in range(len(moves)):
            game.make_move_to(moves[i])
            self.assertEqual(game.score[ChipType.White], white_scores[i])
            self.assertEqual(game.score[ChipType.Black], black_scores[i])

    def _check_start_state_case(self, width, height):
        game = GameModel(width, height)
        self.assertEqual(game.score[ChipType.Black], 2)
        self.assertEqual(game.score[ChipType.White], 2)

    def _check_first_move(self, width, height, move):
        game = GameModel(width, height)
        game.make_move_to(move)
        self.assertEqual(game.score[ChipType.White], 1)
        self.assertEqual(game.score[ChipType.Black], 4)


class CheckMoves(unittest.TestCase):
    def test_basic_moves(self):
        game = GameModel()
        self.assertTrue(game.map[3, 3].type == ChipType.White)
        game.make_move_to((3, 2))
        self.assertTrue(game.map[3, 3].type == ChipType.Black)
        game.make_move_to((2, 2))
        self.assertTrue(game.map[3, 3].type == ChipType.White)

    def test_two_directions(self):
        game = GameModel()
        moves = [(3, 2), (2, 2), (2, 3), (4, 2)]
        for i in range(len(moves) - 1):
            game.make_move_to(moves[i])
        self.assertTrue(game.map[3, 2].type == ChipType.Black)
        self.assertTrue(game.map[4, 3].type == ChipType.Black)
        game.make_move_to(moves[len(moves) - 1])
        self.assertTrue(game.map[3, 2].type == ChipType.White)
        self.assertTrue(game.map[4, 3].type == ChipType.White)

    def test_long_reversed_sequence(self):
        game = GameModel()
        moves = [(3, 2), (2, 2), (2, 3), (4, 2), (5, 5), (6, 6)]
        for i in range(len(moves) - 1):
            game.make_move_to(moves[i])
        for i in range(3, 6):
            self.assertTrue(game.map[i, i].type == ChipType.Black)
        game.make_move_to(moves[len(moves) - 1])
        for i in range(2, 7):
            self.assertTrue(game.map[i, i].type == ChipType.White)


class CheckRocks(unittest.TestCase):
    def test_too_much_rocks(self):
        with self.assertRaises(RocksError):
            game = GameModel(4, 4, 9)

    def test_move_into_rock(self):
        game = GameModel(4, 4, 1)
        res_pos = None
        for pos in game.map.keys():
            if (game.map[pos] is not None and
                    game.map[pos].type is ChipType.Rock):
                res_pos = pos
                break
        with self.assertRaises(MoveError):
            game.make_move_to(res_pos)

    def test_rocks_count(self):
        self._check_rocks_count(1)
        self._check_rocks_count(4)
        self._check_rocks_count(16)

    def _check_rocks_count(self, exp_count):
        res_count = 0
        game = GameModel(rocks_count=exp_count)
        for pos in game.map.keys():
            if (game.map[pos] is not None and
                    game.map[pos].type is ChipType.Rock):
                res_count += 1
        self.assertEqual(exp_count, res_count)


if __name__ == '__main__':
    unittest.main()
