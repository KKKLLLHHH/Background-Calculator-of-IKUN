import os
import ctypes
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from pynput.mouse import Controller, Listener


def path(filename):
    return os.getcwd() + '\\' + filename


def Font(name, size):
    return ImageFont.truetype(name, size, encoding='utf-8')


def change(num):
    num = float(num)
    return int(num) if int(num) == num else num


def updateButton():
    for button in numberButtonList:
        button.update()
    for button in symbolButtonList:
        button.update()
    for button in otherButtonList:
        button.update()


def update():
    updateButton()
    background.save(path('image/tmp.jpg'))
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path('image/tmp.jpg'), 0)


def on_click(x, y, btn, pressed):
    for button in numberButtonList:
        button.press(x, y) if pressed else button.release(x, y)
    for button in symbolButtonList:
        if pressed:
            button.press(x, y)
    for button in otherButtonList:
        button.press(x, y) if pressed else button.release(x, y)
    update()
    print(number_one, symbol, number_two, flag_one, flag_two, error)


def calculate(flag1=False):
    global number_one, symbol, number_two, flag_one, flag_two, last_symbol
    if not flag_two:
        number_two = number_one
    if not symbol:
        symbol = last_symbol
    if symbol:
        global error
        try:
            number_one = eval('{0}{1}{2}'.format(number_one, symbolDict[symbol], number_two))
            number_one = change(number_one)
        except ZeroDivisionError:
            error = 'ZeroDivisionError'
        except OverflowError:
            error = 'OverflowError'
        else:
            last_symbol = symbol
            symbol = ''
            flag_one = flag1
            flag_two = False
            number_two = 0
        finally:
            release()


def release():
    for button in symbolButtonList:
        button.released()


class Button:
    def __init__(self, x, y, width, height, color, text, font):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._color = color
        self._darker = color[0] - 50, color[1] - 50, color[2] - 50
        self._text = text
        self._font = font
        self._state = 0

    def _backgroundColor(self):
        return self._color if self._state == 0 else self._darker

    def _fontColor(self):
        return 0, 0, 0

    def update(self):
        painter.rounded_rectangle((self._x, self._y, self._x + self._width, self._y + self._height), 7.5,
                                  self._backgroundColor())
        text_w = self._font.size * len(self._text) * 0.55
        text_h = self._font.size
        painter.text((self._x + (self._width - text_w) / 2, self._y + (self._height - text_h) / 2),
                     self._text, self._fontColor(), self._font)

    def press(self, x, y):
        if self._x <= x <= self._x + self._width and self._y <= y <= self._y + self._height:
            self._pressed()

    def release(self, x, y):
        if self._x <= x <= self._x + self._width and self._y <= y <= self._y + self._height:
            self._released()

    def _pressed(self):
        self._state = 1

    def _released(self):
        self._state = 0


class NumberButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        global number_one, number_two
        super()._released()
        if error:
            ClearButton.clear()
        if not symbol:
            global flag_one
            if not flag_one:
                flag_one = True
                number_one = int(self._text)
            else:
                number_one = change(str(number_one) + self._text)
        else:
            global flag_two
            if not flag_two:
                flag_two = True
                number_two = int(self._text)
            else:
                number_two = change(str(number_two) + self._text)


class SymbolButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _fontColor(self):
        return (150, 150, 150) if error else (0, 0, 0)

    def _pressed(self):
        global error
        if error:
            return
        calculate(True)
        super()._pressed()
        for button in symbolButtonList:
            if button != self:
                button._released()
        if error:
            self._released()
        symbol = self._text

    def released(self):
        self._released()


class EqualButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        global error
        if error:
            ClearButton.clear()
            return
        calculate()


class Edit(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def update(self):
        self._setText()
        super().update()

    def _setText(self):
        if error == 'ZeroDivisionError':
            self._text = error
            self._font = Font('consola.ttf', 40)
            return
        elif error == 'OverflowError':
            self._text = error
            self._font = Font('consola.ttf', 50)
            return
        text = str(number_one if not flag_two else number_two)
        if len(text) > 12:
            self._font = Font('consola.ttf', int(700 / len(text)))
            self._text = text
        else:
            self._font = Font('consola.ttf', 60)
            self._text = text.rjust(10)

    def _pressed(self):
        pass

    def _released(self):
        pass


class BackspaceButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        if error:
            ClearButton.clear()
            return
        if not symbol:
            global number_one
            number_one = str(number_one)[:-1]
            number_one = 0 if not number_one else change(number_one)
        else:
            global number_two
            number_two = str(number_two)[:-1]
            number_two = 0 if not number_two else change(number_two)


class ClearButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def update(self):
        self._setMode()
        super().update()

    def _released(self):
        super()._released()
        if error:
            ClearButton.clear()
            return
        if self._text == 'C':
            self.clear()
            release()
        elif self._text == 'CE':
            if not symbol:
                global number_one, flag_one
                number_one = 0
                flag_one = True
            else:
                global number_two, flag_two
                flag_two = True
                number_two = 0

    def _setMode(self):
        if error:
            self._text = 'C'
        elif not symbol:
            self._text = 'CE' if number_one else 'C'
        else:
            self._text = 'CE' if (not flag_two) or number_two else 'C'

    @staticmethod
    def clear():
        global number_one, symbol, number_two, flag_one, flag_two, error, last_symbol
        number_one = number_two = 0
        error = ''
        symbol = ''
        flag_one = True
        flag_two = False
        last_symbol = ''


class PointButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        global number_one, number_two
        super()._released()
        if error:
            ClearButton.clear()
        if not symbol:
            global flag_one
            if not flag_one:
                flag_one = True
                number_one = int(self._text)
            else:
                number_one = change(str(number_one) + self._text)
        else:
            global flag_two
            if not flag_two:
                flag_two = True
                number_two = int(self._text)
            else:
                number_two = change(str(number_two) + self._text)


if __name__ == '__main__':
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path('image/background.jpg'), 0)
    Image.open(path('image/background.jpg')).save(path('image/tmp.jpg'))

    background = Image.open(path('image/tmp.jpg'))
    painter = ImageDraw.Draw(background)

    mouse = Controller()

    number_one = 0
    number_two = 0
    flag_one = True
    flag_two = False
    symbol = ''
    last_symbol = ''
    error = ''

    symbolDict = {
        '+': '+',
        '-': '-',
        '×': '*',
        '÷': '/'
    }

    numberButtonList = (
        NumberButton(400, 400, 90, 90, (200, 200, 200), '7', Font('consola.ttf', 60)),
        NumberButton(500, 400, 90, 90, (200, 200, 200), '8', Font('consola.ttf', 60)),
        NumberButton(600, 400, 90, 90, (200, 200, 200), '9', Font('consola.ttf', 60)),
        NumberButton(400, 500, 90, 90, (200, 200, 200), '4', Font('consola.ttf', 60)),
        NumberButton(500, 500, 90, 90, (200, 200, 200), '5', Font('consola.ttf', 60)),
        NumberButton(600, 500, 90, 90, (200, 200, 200), '6', Font('consola.ttf', 60)),
        NumberButton(400, 600, 90, 90, (200, 200, 200), '1', Font('consola.ttf', 60)),
        NumberButton(500, 600, 90, 90, (200, 200, 200), '2', Font('consola.ttf', 60)),
        NumberButton(600, 600, 90, 90, (200, 200, 200), '3', Font('consola.ttf', 60)),
        NumberButton(400, 700, 90, 90, (200, 200, 200), '0', Font('consola.ttf', 60))
    )
    symbolButtonList = (
        SymbolButton(700, 600, 90, 90, (200, 200, 200), '+', Font('consola.ttf', 60)),
        SymbolButton(700, 500, 90, 90, (200, 200, 200), '-', Font('consola.ttf', 60)),
        SymbolButton(700, 400, 90, 90, (200, 200, 200), '×', Font('consola.ttf', 60)),
        SymbolButton(700, 300, 90, 90, (200, 200, 200), '÷', Font('consola.ttf', 60))
    )
    otherButtonList = (
        EqualButton(600, 700, 190, 90, (200, 200, 200), '=', Font('consola.ttf', 60)),
        ClearButton(500, 300, 90, 90, (200, 200, 200), 'C', Font('consola.ttf', 60)),
        Edit(400, 200, 390, 90, (200, 200, 200), '0'.rjust(10), Font('consola.ttf', 60)),
        PointButton(500, 700, 90, 90, (200, 200, 200), '.', Font('consola.ttf', 60)),
        BackspaceButton(600, 300, 90, 90, (200, 200, 200), '←', Font('consola.ttf', 60)),
        Button(400, 300, 90, 90, (200, 200, 200), '', Font('consola.ttf', 15))
    )

    update()

    while True:
        with Listener(on_click=on_click) as listener:
            listener.join()
