import os
import cv2
import subprocess
import time
import platform
from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
from PIL import Image, ImageFont, ImageDraw

def MAIN(filename):
    if not os.path.exists("audio.mp3"):
        if platform.system() == 'Windows':
            command = "ffmpeg.exe -i %s -vn audio.mp3" % filename
        elif platform.system() == 'Linux':
            command = "ffmpeg -i %s -vn audio.mp3" % filename
        else:
            command = "ffmpeg -i %s -vn audio.mp3" % filename
        subprocess.call(command, shell=True)
    else:
        pass
    vc = cv2.VideoCapture(filename)
    fps = vc.get(cv2.CAP_PROP_FPS)
    fourcc = VideoWriter_fourcc(*'mpeg')
    size = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    vw = cv2.VideoWriter('out.mp4', fourcc, int(fps), size, True)
    while vc.isOpened():
        status, frame = vc.read()
        # ##########################
        #                          #
        #   Add main function here #
        #                          #
        # ##########################
        if status is True:
            try:
                vw.write(frame)
            except:
                break
        else:
            break
    vw.release()
    combine_audio_and_video(filename)

def combine_audio_and_video(filename):
    final_name = 'Final_char_%s.mp4' % filename.split('.')[0]
    if not os.path.exists(final_name):
        if platform.system() == 'Windows':
            command = "ffmpeg.exe -i out.mp4 -i audio.mp3 %s" % final_name
        elif platform.system() == 'Linux':
            command = "ffmpeg -i out.mp4 -i audio.mp3 %s" % final_name
        else:
            command = "ffmpeg -i out.mp4 -i audio.mp3 %s" % final_name
        subprocess.call(command, shell=True)
    else:
        pass



if __name__=='__main__':
    start = time.time()
    # print(platform.system())
    MAIN('bad_apple.flv')
    # combine_audio_and_video('bad_apple.flv')
    end = time.time()
    print(end - start)