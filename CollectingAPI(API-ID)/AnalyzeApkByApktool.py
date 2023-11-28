#encoding : utf-8


import os
import sys


path = 'F:/apk/'
apk_name = 'test.apk'
try:
    os.system('apktool d ' + path + apk_name + '.apk -o ' + path + 'res/' + s)
except:
    pass
