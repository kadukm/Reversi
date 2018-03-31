from .ChipType import ChipType
from .Chip import Chip
import math


def _get_field(game):
    res = []
    chip_dict = {ChipType.White: '\u25cb',
                 ChipType.Black: '\u25cf',
                 ChipType.Rock: '#'}
    tab_len = math.ceil(math.log10(game.height - 1)) + 1
    nums_tip = ' ' * tab_len + ''.join([str(i)[-1] for i in range(game.width)])
    res.append(nums_tip)
    for y in range(game.height):
        line = str(y) + ' ' * (tab_len - len(str(y)))
        for x in range(game.width):
            if isinstance(game.map[x, y], Chip):
                cur_c = chip_dict[game.map[x, y].type]
            elif (x, y) in game.available_moves:
                cur_c = '.'
            else:
                cur_c = '-'
            line += cur_c
        res.append(line)
    res.append(nums_tip)
    res.append('')
    return '\n'.join(res)


def _get_score(game):
    return ('Белые: ' + str(game.score[ChipType.White]) + '\n' +
            'Черные: ' + str(game.score[ChipType.Black]) + '\n')


def _get_cur_player(game):
    cur_player = ('Белые (\u25cb)' if game.get_cur_chip_type == ChipType.White
                  else 'Черные (\u25cf)')
    return 'Текущий игрок: {}\n'.format(cur_player)


def _get_separator():
    return '---------------------------------' \
           '----------------------------------\n'


def get_cur_condition(game):
    res = [_get_separator(), _get_score(game), _get_cur_player(game),
           _get_field(game)]
    if not game.is_running:
        res.append(_get_message_about_ending(game))
    return ''.join(res)


def _get_message_about_ending(game):
    beginning_of_result = 'Доступных ходов нет. Игра закончена.\n'
    score_b = game.score[ChipType.Black]
    score_w = game.score[ChipType.White]
    if score_b == score_w:
        return beginning_of_result + 'Ничья!'
    winner = 'белые' if score_w > score_b else 'черные'
    return beginning_of_result + ('Победили {} со счетом {}:{}.\n'
                                  .format(winner, str(score_b), str(score_w)))
