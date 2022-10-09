import ctypes
from os import getcwd
from pygame import mixer
from random import randint
from win32api import GetSystemMetrics
from PIL import Image, ImageDraw, ImageFont
from pynput.mouse import Controller, Listener
from win32gui import GetForegroundWindow, GetWindowText


def path(filename):
    return getcwd() + '\\' + filename


def tmp_image(filename):
    return path('tmp\\' + filename + tp)


def Font(name, size):
    return ImageFont.truetype(name, size, encoding='utf-8')


def change(num):
    num = float(num)
    if 'e' in str(num):
        return num
    return int(num) if int(num) == num else num


def updateButton():
    for button in numberButtonList:
        button.update()
    for button in symbolButtonList:
        button.update()
    for button in otherButtonList:
        button.update()


def update():
    background.paste(Image.open(img), (0, 0))
    updateButton()
    background.paste(Image.open(path('image/cxk.png')), (400, 300))
    background.save(tmp_image('tmp'))
    ctypes.windll.user32.SystemParametersInfoW(20, 0, tmp_image('tmp'), 0)


def on_click(x, y, btn, pressed):
    window_name = GetWindowText(GetForegroundWindow())
    if window_name and window_name != 'Program Manager':
        return
    for button in numberButtonList:
        button.press(x, y) if pressed else button.release(x, y)
    for button in symbolButtonList:
        if pressed:
            button.press(x, y)
    for button in otherButtonList:
        button.press(x, y) if pressed else button.release(x, y)
    update()
    print(number_one, symbol, number_two, flag_one, flag_two, last_symbol, last_number, error)


def calculate():
    global number_one, symbol, number_two, flag_one, flag_two, last_symbol, last_number
    if number_one is None:
        number_one = change(otherButtonList[2].getText().strip())
    else:
        number_two = change(otherButtonList[2].getText().strip()) if flag_two else \
            (last_number if last_number else number_one)
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
            last_number = number_two
            symbol = ''
            flag_one = False
            flag_two = False
            number_two = None
        finally:
            release()
            otherButtonList[2].setText(str(number_one))


def calculate2():
    global number_one, symbol, number_two, flag_one, flag_two, last_symbol
    if number_one is None:
        number_one = change(otherButtonList[2].getText().strip())
    elif flag_two:
        number_two = change(otherButtonList[2].getText().strip()) if flag_two else number_one
    if number_one and symbol and number_two:
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
            flag_one = False
            flag_two = False
            number_two = None
        finally:
            release()
            otherButtonList[2].setText(str(number_one))


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
        super()._released()
        if error:
            ClearButton.clear()
        tmp = otherButtonList[2].getText().strip()
        if not symbol:
            global flag_one, number_one
            tmp = self._text if not flag_one or tmp == '0' else tmp + self._text
            if not flag_one:
                number_one = None
            flag_one = True
        else:
            global flag_two
            tmp = self._text if not flag_two or tmp == '0' else tmp + self._text
            flag_two = True
        otherButtonList[2].setText(tmp)


class SymbolButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _fontColor(self):
        return (150, 150, 150) if error else (0, 0, 0)

    def _pressed(self):
        if error:
            return
        global symbol, last_number
        calculate2()
        super()._pressed()
        for button in symbolButtonList:
            if button != self:
                button._released()
        if error:
            self._released()
        last_number = None
        symbol = self._text

    def released(self):
        self._released()


class EqualButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        if error:
            ClearButton.clear()
            return
        calculate()


class Edit(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def update(self):
        super().update()

    def getText(self):
        return self._text

    def setText(self, text):
        if error == 'ZeroDivisionError':
            self._text = error
            self._font = Font('font/consola.ttf', 40)
            return
        elif error == 'OverflowError':
            self._text = error
            self._font = Font('font/consola.ttf', 50)
            return
        if len(text) <= 10:
            self._font = Font('font/consola.ttf', 60)
            self._text = text.rjust(10)
        elif len(text) <= 20:
            self._font = Font('font/consola.ttf', 30)
            self._text = text.rjust(20)
        elif len(text) <= 30:
            self._font = Font('font/consola.ttf', 20)
            self._text = text.rjust(30)
        else:
            self._font = Font('font/consola.ttf', 15)
            self._text = text.rjust(50)

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
        if not flag_one:
            return
        tmp = otherButtonList[2].getText().strip()[:-1]
        if not tmp:
            tmp = '0'
        otherButtonList[2].setText(tmp)


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
                number_one = None
                flag_one = True
                otherButtonList[2].setText('0')
            else:
                global number_two, flag_two
                flag_two = True
                number_two = None
                otherButtonList[2].setText('0')

    def _setMode(self):
        tmp = otherButtonList[2].getText().strip()
        if error:
            self._text = 'C'
        elif not symbol:
            self._text = 'CE' if tmp != '0' else 'C'
        else:
            self._text = 'CE' if (not flag_two) or tmp != '0' else 'C'

    @staticmethod
    def clear():
        global number_one, symbol, number_two, flag_one, flag_two, error, last_symbol, last_number
        number_one = number_two = None
        error = ''
        symbol = ''
        flag_one = True
        flag_two = False
        last_number = None
        last_symbol = ''
        otherButtonList[2].setText('0')


class PointButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        if error:
            ClearButton.clear()
        tmp = otherButtonList[2].getText().strip()
        if tmp.count('.'):
            return
        if not symbol:
            global flag_one, number_one
            tmp = '0.' if not flag_one or tmp == '0' else tmp + self._text
            if not flag_one:
                number_one = None
            flag_one = True
        else:
            global flag_two
            tmp = '0.' if not flag_two or tmp == '0' else tmp + self._text
            flag_two = True
        otherButtonList[2].setText(tmp)


class CxkButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        mixer.music.load('audio/%s.mp3' % ('ji' if randint(0, 1) else '你干嘛'))
        mixer.music.play()


class ExitButton(Button):
    def __init__(self, x, y, width, height, color, text, font):
        Button.__init__(self, x, y, width, height, color, text, font)

    def _released(self):
        super()._released()
        assert True is False


if __name__ == '__main__':
    mixer.init()

    with open(getcwd() + '/data/backgroundImage', 'r', encoding='utf-8') as f:
        img = f.readlines()[0].strip()
    tp = img.split('.')
    tp = '.' + tp[len(tp) - 1].strip()
    print(tp)

    ctypes.windll.user32.SystemParametersInfoW(20, 0, img, 0)
    Image.open(img).save(tmp_image('tmp'))

    background = Image.open(tmp_image('tmp'))
    w, h = GetSystemMetrics(0), GetSystemMetrics(1)
    background = background.resize((w, h))
    print(background.size)
    painter = ImageDraw.Draw(background)

    mouse = Controller()

    number_one = None
    number_two = None
    flag_one = True
    flag_two = False
    symbol = ''
    last_symbol = ''
    last_number = None
    error = ''

    symbolDict = {
        '+': '+',
        '-': '-',
        '×': '*',
        '÷': '/'
    }

    numberButtonList = (
        NumberButton(400, 400, 90, 90, (200, 200, 200), '7', Font('font/consola.ttf', 60)),
        NumberButton(500, 400, 90, 90, (200, 200, 200), '8', Font('font/consola.ttf', 60)),
        NumberButton(600, 400, 90, 90, (200, 200, 200), '9', Font('font/consola.ttf', 60)),
        NumberButton(400, 500, 90, 90, (200, 200, 200), '4', Font('font/consola.ttf', 60)),
        NumberButton(500, 500, 90, 90, (200, 200, 200), '5', Font('font/consola.ttf', 60)),
        NumberButton(600, 500, 90, 90, (200, 200, 200), '6', Font('font/consola.ttf', 60)),
        NumberButton(400, 600, 90, 90, (200, 200, 200), '1', Font('font/consola.ttf', 60)),
        NumberButton(500, 600, 90, 90, (200, 200, 200), '2', Font('font/consola.ttf', 60)),
        NumberButton(600, 600, 90, 90, (200, 200, 200), '3', Font('font/consola.ttf', 60)),
        NumberButton(400, 700, 90, 90, (200, 200, 200), '0', Font('font/consola.ttf', 60))
    )
    symbolButtonList = (
        SymbolButton(700, 600, 90, 90, (200, 200, 200), '+', Font('font/consola.ttf', 60)),
        SymbolButton(700, 500, 90, 90, (200, 200, 200), '-', Font('font/consola.ttf', 60)),
        SymbolButton(700, 400, 90, 90, (200, 200, 200), '×', Font('font/consola.ttf', 60)),
        SymbolButton(700, 300, 90, 90, (200, 200, 200), '÷', Font('font/consola.ttf', 60))
    )
    otherButtonList = (
        EqualButton(600, 700, 190, 90, (200, 200, 200), '=', Font('font/consola.ttf', 60)),
        ClearButton(500, 300, 90, 90, (200, 200, 200), 'C', Font('font/consola.ttf', 60)),
        Edit(400, 200, 390, 90, (200, 200, 200), '0'.rjust(10), Font('font/consola.ttf', 60)),
        PointButton(500, 700, 90, 90, (200, 200, 200), '.', Font('font/consola.ttf', 60)),
        BackspaceButton(600, 300, 90, 90, (200, 200, 200), '←', Font('font/consola.ttf', 60)),
        CxkButton(400, 300, 90, 90, (200, 200, 200), '', Font('font/consola.ttf', 20)),
        ExitButton(800, 200, 30, 30, (255, 0, 0), 'x', Font('font/consola.ttf', 20))
    )

    update()

    while True:
        with Listener(on_click=on_click) as listener:
            listener.join()
