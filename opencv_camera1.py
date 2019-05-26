#!/usr/bin/env python3

from sys import path
path.append('/usr/lib/python3/dist-packages')

import os
import cv2

def save_frames(name, frames):
    os.system('rm -rf {}.backup'.format(name))
    os.system('cp -a {} {}.backup'.format(name, name))
    os.system('mkdir -p {}'.format(name))
    os.system('rm -f {}/frame*.png'.format(name))
    for i, frame in enumerate(frames):
        cv2.imwrite('{}/frame{:06d}.png'.format(name, i), frame)
    print("{} frames written to {}".format(i, name))

def save_video(name, frames, fps):
    if not frames:
        print("nothing to save")
        return
    w = frame.shape[1]
    h = frame.shape[0]
    #fmt = 'XVID'
    fmt = 'MJPG'
    #fmt = 'WMV1'
    fourcc = cv2.VideoWriter_fourcc(*fmt)
    fname = '{}.avi'.format(name)
    is_color = True
    print('saving to {}'.format(fname))
    out = cv2.VideoWriter(fname, fourcc, fps, (w,h), is_color)
    for f in frames:
        out.write(f)
    out.release()

def snapshot():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return frame
    else:
        print("error")

frames = []
while True:
    frame = snapshot()
    if frame is not None:
        cv2.imshow('frame',frame)
        frames.append(frame)
    else:
        print("error during camera read")
    k = cv2.waitKey(0)
    if k == ord('q'):
        break

cv2.destroyAllWindows()

save_frames("output", frames)
save_video("output", frames, 4.0)
