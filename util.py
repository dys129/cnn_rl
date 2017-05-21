import numpy as np
import pandas as pd
import win32gui, win32ui, win32con, win32api
from PIL import Image

CAPTURE_FILE = 'capture_data.hdf5'
CAPTURE_PATH = 'capture/'
SCREENSHOT_SIZE = (215, 310, 3)

def is_valid_capture_file(file):
    return 'images' in file and 'input' in file and 'count' in file.attrs and 'img_size' in file.attrs

#returns size of 215, 310, 3
def get_screenshot(hwnd):
    l,t,r,b = win32gui.GetWindowRect(hwnd)
    height = b-t
    width = r-l
    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)
    bmpstr = bmp.GetBitmapBits(True)
                    #img = np.fromstring(signedIntsArray, dtype='uint8')
                    #img.shape = (height,width,4)
    im = Image.frombuffer('RGB', (width, height), bmpstr, 'raw', 'BGRX', 0, 1)
    w, h = 320, 240
    im = im.resize( (w, h), Image.NEAREST)
    im = im.crop( (5, 20, w-5, h-5) )
    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return im
