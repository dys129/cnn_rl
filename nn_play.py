import pyvjoy
import win32api
import time
import tensorflow as tf
import win32gui, win32ui, win32con, win32api
import util
import numpy as np
from skimage import img_as_float

#HID_USAGE_X 0.0 LS max L 
#HID_USAGE_X 0.5 LS center
#HID_USAGE_X 1.0 LS max R

#HID_USAGE_Y 1.0 LS max B
#HID_USAGE_Y 0.5 LS center
#HID_USAGE_Y 0.0 LS max T

#HID_USAGE_Z 0.0 - RT 1.0
#HID_USAGE_Z 0.5 - RT 0.0, LT 0.0
#HID_USAGE_Z 1.0 - LT 1.0

def control_vjoy_from_cnn(j, cnn_output):
    MAX_JOY = 0x8000
    t = 0.5
    j.set_button(1, int(cnn_output[0]>t))
    j.set_button(2, int(cnn_output[1]>t))
    j.set_button(3, int(cnn_output[2]>t))
    j.set_button(4, int(cnn_output[3]>t))
    j.set_button(5, int(cnn_output[4]>t))
    j.set_button(6, int(cnn_output[5]>t))

    j.set_axis(pyvjoy.HID_USAGE_X, int(MAX_JOY * np.clip(cnn_output[6] * 0.5 + 0.5, 0.0, 1.0)))
    j.set_axis(pyvjoy.HID_USAGE_Y, int(MAX_JOY * np.clip(cnn_output[7] * 0.5 + 0.5, 0.0, 1.0)))
    j.set_axis(pyvjoy.HID_USAGE_Z, int(MAX_JOY * np.clip(cnn_output[8] * 0.5 + 0.5, 0.0, 1.0)))           
def main():
    j = pyvjoy.VJoyDevice(1)

    sess = tf.Session()

    new_saver = tf.train.import_meta_graph('cnn_model.meta')
    new_saver.restore(sess, './cnn_model')
    print("Model loaded")
    model_col = tf.get_collection('model')
    cnn_out = model_col[1]
    cnn_X = model_col[0]
    
    print('cnn_out: ', cnn_out)
    print('cnn_X: ', cnn_X)
    xa = 0.5
    cnn_playing = False
    while True:
        
        buttons = {'A':0, 'B':0, 'X':0, 'Y':0}
        MAX_JOY = 0x8000
        if win32api.GetAsyncKeyState(0x41):
            cnn_playing = not cnn_playing
            print('pressed P - Is CNN in control: ', cnn_playing)
            buttons['A'] = 1
        if win32api.GetAsyncKeyState(0x4F):
            print('pressed O - xa: ', xa)
            xa += 0.01
        if win32api.GetAsyncKeyState(0x4C):
            print('pressed O - xa: ', xa)
            xa -= 0.01
        #j.set_button(1,buttons['A'])
        #j.set_button(2,buttons['B'])

        hwnd = win32gui.GetForegroundWindow()
        hwnd_name = win32gui.GetWindowText(hwnd);
        if "Rocket League" in hwnd_name:
            im = util.get_screenshot(hwnd)
            im_arr = np.array(img_as_float(im))
            im_arr.shape = (1, im_arr.shape[0], im_arr.shape[1], im_arr.shape[2])
            if cnn_playing:
                cnn_dir = sess.run(cnn_out, feed_dict = {cnn_X: im_arr})
                print(cnn_dir[0])
                control_vjoy_from_cnn(j, cnn_dir[0])
        '''   
        xa = max(xa, 0.0)
        xa = min(xa, 1.0)
        j.set_axis(pyvjoy.HID_USAGE_X, int(MAX_JOY * 0.5))
        j.set_axis(pyvjoy.HID_USAGE_Y, int(MAX_JOY * xa))
        j.set_axis(pyvjoy.HID_USAGE_Z, int(MAX_JOY * 0.3)) #LT/BT

        j.set_axis(pyvjoy.HID_USAGE_RX, int(MAX_JOY * 0.5))
        j.set_axis(pyvjoy.HID_USAGE_RY, int(MAX_JOY * 0.5))
        j.set_axis(pyvjoy.HID_USAGE_RZ, int(MAX_JOY * 0.5))

        j.set_axis(pyvjoy.HID_USAGE_SL0, int(MAX_JOY * 0.5))
        j.set_axis(pyvjoy.HID_USAGE_SL1, int(MAX_JOY * 0.5))
        j.set_axis(pyvjoy.HID_USAGE_WHL, int(MAX_JOY * 0.5))
        '''
        time.sleep(0.03)

if __name__ == '__main__':
    main()
