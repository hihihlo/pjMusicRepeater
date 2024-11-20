import numpy as np
import os, sys
vna = 11


    # print(f'file={__file__}')
    # # file=C:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice\pjMusicRepeater\tmp.py
    # print(f'absp={os.path.abspath(__file__)}')
    # # absp=C:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice\pjMusicRepeater\tmp.py
    # SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # print(f'SCRI={SCRIPT_DIR}')
    # # SCRI=C:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice\pjMusicRepeater
    # print(f'dirn={os.path.dirname(SCRIPT_DIR)}')
    # # dirn=C:\DriveD\MyPro\DataProc\Parser_Script\Python\+media\+voice
    #
    # sys.path.append(SCRIPT_DIR)

# from plum import dispatch  # pip install plum-dispatch
# import importlib
# tmp2 = importlib.import_module('tmp2')
# from . import tmp2
# from tmp2 import finb
# from pjMusicRepeater.tmp2 import finb

if __name__ == '__main__':   # can avoid tmp2 > import tmp > run below again !!!
    import tmp2
    print(tmp2.finb())
