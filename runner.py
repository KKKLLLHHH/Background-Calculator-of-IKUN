import ctypes
from PIL import Image
from tkinter import Tk
from os import system, getcwd
from tkinter.filedialog import askopenfilename


def getFile():
    root = Tk()
    filename = askopenfilename()
    root.destroy()
    with open(getcwd() + '/data/backgroundImage', 'w', encoding='utf-8') as f:
        f.write(filename)


def setAuto():
    system('setAuto.exe')


def reset():
    ctypes.windll.user32.SystemParametersInfoW(20, 0, img, 0)


if __name__ == '__main__':
    try:
        with open(getcwd() + '/data/backgroundImage', 'r', encoding='utf-8') as f:
            img = f.readlines()[0].strip()
        Image.open(img)
    except FileNotFoundError:
        getFile()
    except PermissionError:
        getFile()
    mode = input('Mode: ')
    if mode in ['R', 'r', 'Run', 'run']:
        system('calculator2.exe')
        reset()
    elif mode in ['S', 's', 'Set', 'set']:
        getFile()
    elif mode in ['A', 'a', 'Auto', 'auto']:
        setAuto()
    elif mode in ['reset', 'Reset']:
        reset()
