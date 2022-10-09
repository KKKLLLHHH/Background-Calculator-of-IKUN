from os import getcwd
from win32con import HKEY_CURRENT_USER, REG_SZ
from win32api import RegOpenKey, RegSetValueEx, RegCloseKey

name = '计算器'
path = getcwd() + '\\runner.exe'
KeyName = 'Software\\Microsoft\\Windows\\CurrentVersion\\Run'

key = RegOpenKey(HKEY_CURRENT_USER, KeyName, 0, HKEY_CURRENT_USER)
RegSetValueEx(key, name, 0, REG_SZ, path)
RegCloseKey(key)