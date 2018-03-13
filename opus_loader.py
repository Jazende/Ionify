from discord import opus
from ctypes.util import find_library


def load_opus_library():
    if opus.is_loaded():
        return True
    try:
        find_library('opus')
        return
    except:
        return False
    return False
