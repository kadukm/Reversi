from .ChipType import ChipType


class Chip:
    def __init__(self, chip_type):
        self.type = chip_type

    def reverse(self):
        if self.type == ChipType.Black:
            self.type = ChipType.White
        elif self.type == ChipType.White:
            self.type = ChipType.Black
        else:
            raise TypeError('Неизвестный тип фишки')
