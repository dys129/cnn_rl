import os
import sys
import glob
import pygame
import numpy as np
import pandas as pd
import win32gui, win32ui, win32con, win32api
from PIL import Image
from time import sleep
import util
import h5py
import uuid
#from inputs import get_gamepad


#0 - A
#1 - B
#2 - X
#3 - Y
#4 - LB
#5 - RB

#axis 0 - left L/R
#axis 1 - left T/B
#axis 2 - trigger -1 - 0 left 0 - 1 right
#axis 3 - right L/R
#axis 4 - right T/B

data_path = 'D:/tf/rl/data/'


def get_input(joystick):
    buttons = [float(joystick.get_button(i)) for i in range(6)]
    axis = [float(joystick.get_axis(i)) for i in range(3)]
    xinput = buttons + axis
    return np.asarray(xinput, dtype='float32')

def save_data_to_file(recorded_image, recorded_input):
    filename = uuid.uuid4().hex + '.hdf5'
    file = h5py.File(util.CAPTURE_PATH + filename, "w")
    #file = h5py.File(filename, 'w')
    data_count = len(recorded_input)
    print('Saving captures: ', data_count, ' to :' + filename)
    img_dtype = h5py.special_dtype(vlen=np.dtype('uint8'))
    input_dtype = h5py.special_dtype(vlen=np.dtype('float32'))
    file.create_dataset('images', (data_count,), dtype=img_dtype)
    file.create_dataset('input', (data_count,), dtype=input_dtype)
    file.attrs['img_size'] = util.SCREENSHOT_SIZE
    file.attrs['count'] = data_count

    for i in range(data_count):
        file['images'][i] = recorded_image[i].flatten()
        file['input'][i] = recorded_input[i]
    
    file.flush()
    file.close()

def main(argv):
    print('Initializing...')
    start_counter = 0
    counter = 0
    os.environ["SDL_VIDEODRIVER"] = "dummy"
        # init pygame
    pygame.init()
        # create a 1x1 pixel screen, its not used so it doesnt matter
    screen = pygame.display.set_mode((1, 1))
    
    pygame.joystick.init()

    #continue_capture = any("-c" in s for s in argv)
    #capture_file = h5py.File(util.CAPTURE_FILE, "a" if continue_capture else "w")
    #valid_file = False
    '''
    if continue_capture and not util.is_valid_capture_file(capture_file):
        print(util.CAPTURE_FILE + ' is not valid, cannot continue')
        return

    if continue_capture:
        start_counter = capture_file.attrs['count']
        print('Continue capture from: ', start_counter)
    '''
    recorded_input = []
    recorded_image = []
    recording = False
    joystick = None
    
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        name = joy.get_name()
        print("Joystick name: {}".format(name) )
        axes = joy.get_numaxes()
        print("Number of axes: {}".format(axes) )
        buttons = joy.get_numbuttons()
        print("Number of buttons: {}".format(buttons) )
        if 'XBOX' in joy.get_name():
            joystick = joy

    print('Ready to capture... (r - capture, q - quit)')
    while True:
        hwnd = win32gui.GetForegroundWindow()
        hwnd_name = win32gui.GetWindowText(hwnd);
        #if hwnd_name.contains("Rocket League"):
        if "Rocket League" in hwnd_name:
            if(win32api.GetAsyncKeyState(0x52)): #r
                recording = not recording
                if(recording): print('Started recording')
                else:
                    print('Stopped recording at', counter)

            if(recording):    
                im = util.get_screenshot(hwnd)
                xinput = get_input(joystick)
                
                name = data_path + 'scr_' + str(counter) +'.png'
                #im.save(name)
                recorded_image.append(np.asarray(im))
                recorded_input.append(xinput)
                
                counter += 1

                if counter % 100 == 0:
                    print('Current count: ', counter)

            #for event in pygame.event.get():
             #   print(event)
            pygame.event.pump()
            sleep(0.1)
        if win32api.GetAsyncKeyState(0x45): #e
            if(recording): print('Cannot save data during recording')
            else:
                save_data_to_file(recorded_image, recorded_input)
                recorded_image.clear()
                recorded_input.clear()
            
        if win32api.GetAsyncKeyState(0x51): #q
                print('Quitting')
                break

    pygame.quit()
    data_count = len(recorded_input)
    if data_count>0:
        save_data_to_file(recorded_image, recorded_input)
'''
    data_count = len(recorded_input)
    total_count = start_counter + data_count
    print('Saving captures: ', data_count, ' Total: ', total_count)
    if not continue_capture:
        img_dtype = h5py.special_dtype(vlen=np.dtype('uint8'))
        input_dtype = h5py.special_dtype(vlen=np.dtype('float32'))
        capture_file.create_dataset('images', (data_count,), maxshape=(None,), dtype=img_dtype)
        capture_file.create_dataset('input', (data_count,), maxshape=(None,), dtype=input_dtype)
        capture_file.attrs['img_size'] = util.SCREENSHOT_SIZE
        capture_file.attrs['count'] = data_count
    else:
        capture_file['images'].resize((total_count,))
        capture_file['input'].resize((total_count,))
        capture_file.attrs['count'] = total_count
        
    for i in range(start_counter, total_count):
        capture_file['images'][i] = recorded_image[i-start_counter].flatten()
        capture_file['input'][i] = recorded_input[i-start_counter]

    
    '''
    

    #capture_file.flush()
    #capture_file.close()
        


if __name__ == '__main__':
    main(sys.argv)
