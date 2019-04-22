'''
This is the main function for video to convert to char video
Author: Zichen Liu
'''
import os
import cv2
import subprocess
import time
import platform
from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
from img2chars import *


def MAIN(filename):
    '''
    this is the main function to convert the video to char video.
    :param filename: input video file path
    :return: the name of the output video filename and the size of each frame
    '''
    # split the audio from video file
    if not os.path.exists("audio.mp3"):
        if platform.system() == 'Windows':
            command = "ffmpeg.exe -i %s -vn audio.mp3" % filename
        elif platform.system() == 'Linux':
            command = "ffmpeg -i %s -vn audio.mp3" % filename
        else:
            command = "ffmpeg -i %s -vn audio.mp3" % filename
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            print(line)
    else:
        pass
    # create video writer
    vc = cv2.VideoCapture(filename)
    fps = vc.get(cv2.CAP_PROP_FPS)
    fourcc = VideoWriter_fourcc('m', 'p', '4', 'v')
    size = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    vw = cv2.VideoWriter('out.mp4', fourcc, int(fps), size, True)
    # convert the file and write to out video file
    while vc.isOpened():
        status, frame = vc.read()
        if status is True:
            try:
                vw.write(img2chars(frame, put_original=True))
            except:
                break
        else:
            break
    vw.release()
    vc.release()
    # combine the audio with the out video file
    final = combine_audio_and_video(filename)
    os.remove('out.mp4')
    os.remove('audio.mp3')
    return final, size


def combine_audio_and_video(filename):
    '''
    This is the main function for combine the video and audio
    :param filename: the input video filename
    :return: the out video file name
    '''
    parse = filename.split('.')
    final_name = '%s_Final_char_video.flv' % parse[0]
    # combine the audio and video
    if not os.path.exists(final_name):
        if platform.system() == 'Windows':
            command = "ffmpeg.exe -i out.mp4 -i audio.mp3 %s" % final_name
        elif platform.system() == 'Linux':
            command = "ffmpeg -i out.mp4 -i audio.mp3 %s" % final_name
        else:
            command = "ffmpeg -i out.mp4 -i audio.mp3 %s" % final_name
        p = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            print(line)
    else:
        pass
    return final_name



if __name__=='__main__':
    start = time.time()
    # print(platform.system())
    MAIN('GokurakuJodoODMT_YouTube.flv')
    # combine_audio_and_video('bad_apple.flv')
    end = time.time()
    print(end - start)