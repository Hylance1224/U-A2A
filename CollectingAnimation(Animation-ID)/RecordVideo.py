from PIL import ImageGrab
import numpy as np
import cv2
import time

def record_video(path):
    width = 712
    height = 1282
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(path +'.mp4', fourcc, 6, (width, height))
    start_time = time.time()
    while True:
        im = ImageGrab.grab(bbox=(0, 0, width, height))
        imm = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        video.write(imm)
        jiange = int(time.time()) - int(start_time)
        if jiange == 5:
            break
    video.release()
    cv2.destroyAllWindows()


def record_screenshots(d, path):
    images = []
    tmp_path = path + 'tmp/'
    print(tmp_path)
    import os
    os.makedirs(tmp_path)
    for i in range(25):
        image = d.screenshot(format='raw')
        images.append(image)
    for i in range(25):
        open(tmp_path + str(i) + ".jpg", "wb").write(images[i])


