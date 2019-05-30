#!/usr/bin/env python3

from sys import path
path.append('/usr/lib/python3/dist-packages')

import os
import cv2
import sys
from glob import glob

def load_frames(name):
    if not name.endswith(".anim"):
        print("error: file name does not end with .anim")
        return None
    base_name = os.path.splitext(name)[0]
    dir_name = "frames_for_" + base_name
    frame_files = glob(dir_name + "/*.png")
    for f in sorted(frame_files):
        #print("reading: ", f
        frame = cv2.imread(f)
        frames.append(frame)
    os.system('rm -rf {}_backup.anim {}_backup'.format(base_name, dir_name))
    os.system("cp -a {} {}_backup.anim".format(name, base_name))
    os.system("cp -a {} {}_backup".format(dir_name, dir_name))
    print("{} frames loaded from {}".format(len(frames), name))
    return frames

def save_frames(name, frames):
    if not frames:
        print("error: no frames to save")
        return
    base_name = os.path.splitext(name)[0]
    dir_name = "frames_for_" + base_name
    os.system('rm -rf {} {}'.format(name, dir_name))
    os.system('touch {}'.format(name))
    os.system('mkdir -p {}'.format(dir_name))
    for i, frame in enumerate(frames):
        cv2.imwrite('{}/frame{:06d}.png'.format(dir_name, i+1), frame)
    print("{} frames saved to {}".format(i+1, name))

def save_video(name, frames, fps):
    if not frames:
        print("nothing to write to video")
        return
    w = frames[0].shape[1]
    h = frames[0].shape[0]
    #fmt = 'XVID'
    fmt = 'MJPG'
    #fmt = 'WMV1'
    fourcc = cv2.VideoWriter_fourcc(*fmt)
    fname = '{}.avi'.format(os.path.splitext(name)[0])
    is_color = True
    print('writing video to {}'.format(fname))
    out = cv2.VideoWriter(fname, fourcc, fps, (w,h), is_color)
    for f in frames:
        out.write(f)
    out.release()

def launch_video(name):
    if not frames:
        print("no video frames to play")
        return
    os.system("totem {}.avi &".format(os.path.splitext(name)[0]))

def snapshot():
    cap = cv2.VideoCapture(camera_number)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return frame
    else:
        print("error")

def start_capture():
    cap = cv2.VideoCapture(camera_number)
    if cap.isOpened():
        return cap
    else:
        print("error")
        return None

def stop_capture(cap):
    if cap:
        cap.release()

def live_snapshot(cap):
    if cap:
        ret, frame = cap.read()
        return frame

kv = """
<FrameEditor>:
    orientation: "vertical"
    live_capture: False

FrameEditor:
    id: editor
    before_frames: 1
    after_frames: 0
    bg_opacity: bg_opacity_slider.value
    top_opacity: top_opacity_slider.value
    current_frame: frame_slider.value
    #n_frames: 0
    size_hint_y: None
    height: self.minimum_size[1]
    fps: 4
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: capture_button.texture_size[1]
        Button:
            id: capture_button
            text: "Quick Capture"
            background_color: 0,1,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.capture()
        Button:
            id: preview_capture_button
            text: "Preview Capture"
            color: (1,0,0,1) if editor.live_capture else (1,1,1,1)
            background_color: 0,1,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.preview_capture()
        Label:
            text: "FPS: {}".format(editor.fps)
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        Button:
            text: "<"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.decrease_fps()
        Button:
            text: ">"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.increase_fps()
        Button:
            text: "Play"
            background_color: 0,0,1,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.play()
        Button:
            text: "Save"
            background_color: 1,1,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.save()
        Button:
            text: "File"
            background_color: 0,1,1,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.file_menu()
        Label:
            text: ""
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: frame_label.texture_size[1]
        Label:
            id: frame_label
            text: "Frame {} / {}".format(editor.current_frame, editor.n_frames)
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        Button:
            text: "<"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.previous_frame()
        Button:
            text: ">"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.next_frame()
        Slider:
            id: frame_slider
            min: 1
            max: editor.n_frames
            step: 1
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: screen.height
        Button:
            text: "<-"
            padding: 10, 10
            on_press: editor.previous_frame()
        RelativeLayout:
            id: screen
            size_hint_y: None
            height: editor.frame_height #image.height
            size_hint_x: None
            width: editor.frame_width #image.width
            #Image:
            #    color: 0,0,0,1
            #    size_hint: None, None
            #    size: editor.frame_width, editor.frame_height #960, 540
            #    #source: 'output/frame000001.png'
            #    id: image
        Button:
            text: "->"
            padding: 10, 10
            on_press: editor.next_frame()
    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: delete_button.texture_size[1]
        Button:
            id: delete_button
            text: "Delete Frame"
            background_color: 1,0,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.delete_frame()
        Label:
            text: "Background Opacity:"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Slider:
            id: bg_opacity_slider
            min: 0
            max: 1
            value: 0.5
        Label:
            text: "Before:"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Button:
            text: "<"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.decrement_before_frames()
        Label:
            text: "{}".format(editor.before_frames)
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Button:
            text: ">"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.increment_before_frames()
        Label:
            text: "After:"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Button:
            text: "<"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.decrement_after_frames()
        Label:
            text: "{}".format(editor.after_frames)
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Button:
            text: ">"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.increment_after_frames()
        Label:
            text: "Top Opacity:"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Slider:
            id: top_opacity_slider
            min: 0
            max: 1
            value: 0.7
"""

from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.properties import BooleanProperty, NumericProperty, ListProperty, ObjectProperty
from kivy.clock import Clock

from kivy.config import Config
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '670')

cap = None
live_capture_index = None
frames = []
file_name = "output.anim"
camera_number = 0
if len(sys.argv) > 1:
    file_name = sys.argv[1]
    frames = load_frames(file_name)
if frames:
    frame_width = frames[0].shape[1]
    frame_height = frames[0].shape[0]
else:
    frame = snapshot()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]
print("frames are {}w x {}h".format(frame_width, frame_height))

class FrameEditor(BoxLayout):
    before_frames = NumericProperty()
    after_frames = NumericProperty()
    bg_opacity = NumericProperty()
    top_opacity = NumericProperty()
    current_frame = NumericProperty()
    n_frames = NumericProperty()
    frame_width= NumericProperty()
    frame_height= NumericProperty()
    fps= NumericProperty()
    live_capture=BooleanProperty()

    def __init__(self, **kwargs):
       self.initialized = False
       super(FrameEditor, self).__init__(**kwargs)
       self.frame_width = frame_width
       self.frame_height = frame_height
       self.n_frames = len(frames)
       self.initialized = True
       self.first_show = False

    def on_touch_down(self, touch):
        if self.ids.frame_slider.collide_point(*touch.pos):
            touch.grab(self)
        return super(FrameEditor, self).on_touch_down(touch)
        
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            #print("frame slider moved")
            self.show_frames()
            return
        return super(FrameEditor, self).on_touch_up(touch)
    
    def on_bg_opacity(self, *args, **kw):
        self.update_opacity()

    def on_top_opacity(self, *args, **kw):
        self.update_opacity()
        #print("top_opacity")

    def on_current_frame(self, *args, **kw):
        #print("current frame")
        if not self.first_show:
            self.first_show = True
            self.show_frames()
            return
        if self.n_frames < 1:
            return
        #print(self.current_frame)
        self.ids.screen.clear_widgets()
        self.show_frame(frames[self.current_frame-1])
        #for i, child in enumerate(reversed(self.ids.screen.children)):
        #    if i+1 == self.current_frame:
        #        child.color = [1,1,1,1]
        #    else:
        #        child.color = [1,1,1,0]

    def on_n_frames(self, *args, **kw):
        #print("n frames")
        self.show_frames()

    def next_frame(self):
        if self.ids.frame_slider.value < self.n_frames:
            self.ids.frame_slider.value += 1
            self.show_frames()

    def previous_frame(self):
        if self.ids.frame_slider.value > 1:
            self.ids.frame_slider.value -= 1
            self.show_frames()

    def increment_before_frames(self):
        self.before_frames += 1
        self.show_frames()

    def decrement_before_frames(self):
        if self.before_frames > 0:
            self.before_frames -= 1
            self.show_frames()

    def increment_after_frames(self):
        self.after_frames += 1
        self.show_frames()

    def decrement_after_frames(self):
        if self.after_frames > 0:
            self.after_frames -= 1
            self.show_frames()

    def increase_fps(self):
        self.fps += 1

    def decrease_fps(self):
        if self.fps >= 2:
            self.fps -= 1

    def show_frame(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        #self.ids.image.texture = image_texture
        new_image = Image()
        new_image.texture = image_texture
        #new_image.color = [1,1,1,self.bg_opacity]
        self.ids.screen.add_widget(new_image)

    def show_frames(self):
        if not self.initialized:
            return
        self.ids.screen.clear_widgets()
        if self.n_frames < 1:
            return
        current = self.current_frame
        low = max(current-self.before_frames, 1)
        high = min(current+self.after_frames, self.n_frames)
        maxdiff = max(abs(current - low),
                      abs(current - high))
        #print(low, high, "...", maxdiff)
        #for frame in frames:
        for i in reversed(range(1,maxdiff+1)):
            for j in [1, -1]:
                index = current + j*(i)
                if (index < low) or (index > high):
                    continue
                #print("add frame:", index)
                frame = frames[index-1]
                self.show_frame(frame)
        if current >= 1:
            #print("show", current-1)
            self.show_frame(frames[current-1])
        self.update_opacity()

    def update_opacity(self):
        indices = range(len(self.ids.screen.children))
        for index in indices:
            child = self.ids.screen.children[index]
            if index == indices[-1]:
                child.color = [1,1,1,1]
            elif index == indices[0]:
                child.color = [1,1,1,self.top_opacity]
                #child.color = [1,1,1,self.bg_opacity]
            else:
                child.color = [1,1,1,self.bg_opacity]

    def preview_capture(self):
        global cap
        if self.live_capture:
            stop_capture(cap)
            self.live_capture = False
        else:
            cap = start_capture()
            frame = live_snapshot(cap)
            current = self.current_frame
            frames.insert(self.current_frame, frame)
            self.n_frames += 1
            if current != 0:
                self.ids.frame_slider.value += 1
            global live_capture_index
            live_capture_index = self.ids.frame_slider.value
            self.show_frames()
            self.live_capture = True
            if cap:
                Clock.schedule_once(self.update_capture, 1.0 / 30.0)

    def update_capture(self, *args, **kw):
        #print(len(frames))
        #print("live capture index", live_capture_index)
        if not cap:
            return
        if not self.live_capture:
            return
        frame = live_snapshot(cap)
        if frame is not None:
            frames[live_capture_index-1] = frame
            self.show_frames()
        if cap and self.live_capture:
            Clock.schedule_once(self.update_capture, 1.0 / 30.0)

    def capture(self):
        if self.live_capture:
            return
        frame = snapshot()
        current = self.current_frame
        frames.insert(self.current_frame, frame)
        self.n_frames += 1
        if current != 0:
            self.ids.frame_slider.value += 1
        self.show_frames()
        return

        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        #self.ids.image.texture = image_texture
        new_image = Image()
        new_image.texture = image_texture
        new_image.color = [1,1,1,0.2]
        self.ids.screen.add_widget(new_image)
    
    def play(self):
        #print("play")
        save_video(file_name, frames, self.fps)
        launch_video(file_name)

    def delete_frame(self):
        if self.live_capture:
            return
        #print("delete frame")
        if self.n_frames < 1:
            return
        current = self.current_frame
        self.n_frames -= 1
        frames.pop(current-1)
        #if current != 0:
        #    self.ids.frame_slider.value += 1
        self.show_frames()
        
    def file_menu(self):
        print("file menu")
        
    def save(self):
        #print("save")
        save_frames(file_name, frames)

class TestApp(App):
    def build(self):
        root = Builder.load_string(kv)
        return root
    
TestApp().run()
