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

kv = """
<MyMain>:
    orientation: "vertical"
    
MyMain:
    id: main
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: label1.texture_size[1]
        Button:
            id: label1
            text: "Capture"
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: main.capture()
        Label:
            text: ""
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
    RelativeLayout:
        Image:
            size_hint: None, None
            size: 960, 540
            #source: 'output/frame000001.png'
            id: image
"""

from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture

class MyMain(BoxLayout):
    def __init__(self, **kwargs):
        super(MyMain, self).__init__(**kwargs)

    def capture(self):
        frame = snapshot()
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.ids.image.texture = image_texture

class TestApp(App):
    def build(self):
        root = Builder.load_string(kv)
        return root
    
TestApp().run()
