#!/usr/bin/env python3

from sys import path
path.append('/usr/lib/python3/dist-packages')

import os
import cv2
import sys
import numpy as np
from glob import glob

def load_frames(name):
    frames = []
    if not name.endswith(".anim"):
        print("error: file name does not end with .anim")
        return None, None
    base_name = os.path.splitext(name)[0]
    dir_name = "frames_for_" + base_name
    frame_files = glob(dir_name + "/frame*.png")
    for f in sorted(frame_files):
        #print("reading: ", f
        frame = cv2.imread(f)
        frames.append(frame)
    background_frame_name = glob(dir_name + "/background.png")
    if background_frame_name:
        background_frame = cv2.imread(background_frame_name[0])
    else:
        background_frame = None
    os.system('rm -rf {}_backup.anim {}_backup'.format(base_name, dir_name))
    os.system("cp -a {} {}_backup.anim".format(name, base_name))
    os.system("cp -a {} {}_backup".format(dir_name, dir_name))
    print("{} frames loaded from {}".format(len(frames), name))
    return frames, background_frame

def save_frames(name, frames, background):
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
    if background is not None:
        cv2.imwrite('{}/background.png'.format(dir_name), background)
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

def launch_video(name, frames):
    if not frames:
        print("no video frames to play")
        return
    os.system("totem {}.avi &".format(os.path.splitext(name)[0]))

def snapshot(camera_number):
    cap = cv2.VideoCapture(camera_number)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return frame
    else:
        print("error")

def start_capture(camera_number):
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
    capturing_frame: False
    capturing_background: False
    moving_frame_slider:False
    before_frames: 1
    after_frames: 0
    fps: 8
    n_frames: 0
    has_background_frame: False

FrameEditor:
    id: editor
    bg_opacity: bg_opacity_slider.value
    bg_ratio: bg_ratio_slider.value
    current_frame: frame_slider.value
    subtract_bg: subtract_background_button.active
    onion_skin: onion_skin_button.active
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
            text: "Stop Capture" if editor.capturing_frame else "Start Capture"
            color: (1,0,0,1) if editor.capturing_frame else (1,1,1,1)
            background_color: 0,1,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.preview_capture()
        Label:
            text: ""
        Label:
            text: "FPS:"
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        Button:
            text: "<"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.decrease_fps()
        Label:
            text: "{}".format(editor.fps)
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        Button:
            text: ">"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
            on_press: editor.fps += 1
        Button:
            text: "Play"
            background_color: 0,0,1,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.play()
        Label:
            text: ""
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
        Label:
            text: "Onion Skin"
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        CheckBox:
            id: onion_skin_button
            active: True
            size_hint_x: None
            width: 30
            on_press: editor.show_frames()
        Label:
            text: ""
        Label:
            text: "Subtract Background"
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
        CheckBox:
            id: subtract_background_button
            active: True
            disabled: not editor.has_background_frame
            size_hint_x: None
            width: 30
        Button:
            id: capture_background_button
            text: "Stop Capture" if editor.capturing_background else "Capture Background"
            color: (1,0,0,1) if editor.capturing_background else (1,1,1,1)
            background_color: 0,1,0,1
            size_hint_x: None
            width: self.texture_size[0]
            padding: 10, 10
            on_press: editor.capture_background()
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
        Button:
            text: "<-"
            padding: 10, 10
            on_press: editor.previous_frame()
            size_hint_x: None
            width: self.texture_size[0]
        RelativeLayout:
            id: screen
        Button:
            text: "->"
            padding: 10, 10
            on_press: editor.next_frame()
            size_hint_x: None
            width: self.texture_size[0]
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
            value: 0.8
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
            on_press: editor.before_frames += 1
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
            on_press: editor.after_frames += 1
        Label:
            text: "Background Ratio:"
            padding: 10, 10
            size_hint_x: None
            width: self.texture_size[0]
        Slider:
            id: bg_ratio_slider
            min: 0
            max: 1
            value: 0.01
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

class FrameEditor(BoxLayout):
    before_frames = NumericProperty()
    after_frames = NumericProperty()
    bg_opacity = NumericProperty()
    bg_ratio = NumericProperty()
    current_frame = NumericProperty()
    n_frames = NumericProperty()
    fps= NumericProperty()
    live_capture=BooleanProperty()
    capturing_frame=BooleanProperty()
    capturing_background=BooleanProperty()
    moving_frame_slider=BooleanProperty()
    subtract_bg=BooleanProperty()
    has_background_frame=BooleanProperty()
    onion_skin=BooleanProperty()

    def __init__(self, **kwargs):
        self.initialized = False
        super(FrameEditor, self).__init__(**kwargs)
        self.frames = []
        self.n_frames = len(self.frames)
        self.initialized = True
        self.live_capture_index = None
        self.cap = None
        self.file_name = "unnamed.anim"
        self.background_frame = None
        self.camera_number = 0
        self.fgbg = None
        #self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(1,5,0.01,0)

    def on_touch_down(self, touch):
        if self.ids.frame_slider.collide_point(*touch.pos):
            touch.grab(self)
            self.moving_frame_slider = True
        return super(FrameEditor, self).on_touch_down(touch)
        
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.moving_frame_slider = False
            self.show_frames()
            return
        return super(FrameEditor, self).on_touch_up(touch)
    
    def on_bg_opacity(self, *args, **kw):
        self.show_frames()

    def on_bg_ratio(self, *args, **kw):
        #self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(1,5,self.bg_ratio,0)
        self.fgbg = cv2.bgsegm.createBackgroundSubtractorMOG(1,5,0.01,0)
        if self.has_background_frame:
            self.fgbg.apply(self.background_frame)
            self.fgbg.apply(self.background_frame)
        self.show_frames()

    def on_current_frame(self, *args, **kw):
        self.show_frames()
        return

    def on_n_frames(self, *args, **kw):
        self.show_frames()

    def next_frame(self):
        if self.ids.frame_slider.value < self.n_frames:
            self.ids.frame_slider.value += 1

    def previous_frame(self):
        if self.ids.frame_slider.value > 1:
            self.ids.frame_slider.value -= 1

    def on_before_frames(self, *args, **kw):
        self.show_frames()

    def decrement_before_frames(self):
        if self.before_frames > 0:
            self.before_frames -= 1

    def on_after_frames(self, *args, **kw):
        self.show_frames()

    def decrement_after_frames(self):
        if self.after_frames > 0:
            self.after_frames -= 1

    def decrease_fps(self):
        if self.fps >= 2:
            self.fps -= 1

    def on_has_background_frame(self, *args, **kw):
        if self.has_background_frame:
            self.fgbg.apply(self.background_frame)
            self.fgbg.apply(self.background_frame)
        self.show_frames()

    def on_subtract_bg(self, *args, **kw):
        self.show_frames()

    def show_frame_bgr(self, frame, opacity=1.0):
        b, g, r = cv2.split(frame)
        a = np.ones_like(r)*int(255*opacity)
        rgba = [b,g,r,a]
        frame = cv2.merge(rgba,4)
        self.show_frame_bgra(frame)

    def show_frame_bgra(self, frame):
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        #image_texture = Texture.create(
        #    size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        #image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        image_texture = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt='bgra')
        image_texture.blit_buffer(buf, colorfmt='bgra', bufferfmt='ubyte')
        #self.ids.image.texture = image_texture
        new_image = Image()
        new_image.texture = image_texture
        #new_image.color = [1,1,1,self.bg_opacity]
        self.ids.screen.add_widget(new_image)

    def apply_alpha_channel(self, frame, alpha):
        b, g, r = cv2.split(frame)
        a = alpha.astype(np.uint8)
        rgba = [b,g,r,a]
        return cv2.merge(rgba,4)

    def show_frames(self):
        if not self.initialized:
            return
        self.ids.screen.clear_widgets()
        if self.n_frames < 1:
            return
        if self.moving_frame_slider or not self.onion_skin:
            self.show_frame_bgr(self.frames[self.current_frame-1])
            return
        sub_bg = self.subtract_bg and self.has_background_frame and not self.capturing_background
        current = self.current_frame
        low = max(current-self.before_frames, 1)
        high = min(current+self.after_frames, self.n_frames)
        maxdiff = max(abs(current - low),
                      abs(current - high))
        first = True
        n_bg = 0
        #print("show_frames")
        if sub_bg:
            self.show_frame_bgr(self.background_frame)
        for i in reversed(range(1,maxdiff+1)):
            for j in [1, -1]:
                index = current + j*(i)
                if (index < low) or (index > high):
                    continue
                n_bg += 1
                #print("add frame: {} ({})".format(index, i))
                frame = self.frames[index-1]

                if sub_bg:
                    fgmask = self.fgbg.apply(frame,None,0) # don't update bg model
                    fgmask = fgmask*(self.bg_opacity**i)
                    aframe = self.apply_alpha_channel(frame, fgmask)
                    self.show_frame_bgra(aframe)
                else:
                    if first:
                        opacity = 1.0
                    else:
                        opacity = self.bg_opacity
                    self.show_frame_bgr(frame, opacity)

                if first:
                    first = False

        # top frame
        if current >= 1:
            frame = self.frames[current-1]
            if sub_bg:
                fgmask = self.fgbg.apply(frame,None,0) # don't update bg model
                aframe = self.apply_alpha_channel(frame, fgmask)
                self.show_frame_bgra(aframe)
            else:
                if n_bg == 0:
                    opacity = 1.0
                else:
                    opacity = self.bg_opacity
                self.show_frame_bgr(frame, opacity)

    def capture_background(self):
        if not self.capturing_background:
            if self.live_capture:
                return
            self.capturing_background = True
            self.start_live_capture()
        else:
            self.stop_live_capture()
            self.capturing_background = False
            self.background_frame = self.frames[self.live_capture_index-1]
            self.n_frames -= 1
            self.frames.pop(self.live_capture_index-1)
            self.has_background_frame = True
            self.show_frames()

    def preview_capture(self):
        if not self.capturing_frame:
            if self.live_capture:
                return
            self.capturing_frame = True
            self.start_live_capture()
        else:
            self.stop_live_capture()
            self.capturing_frame = False

    def stop_live_capture(self):
        if self.live_capture:
            stop_capture(self.cap)
            self.live_capture = False

    def start_live_capture(self):
        if not self.live_capture:
            self.cap = start_capture(self.camera_number)
            frame = live_snapshot(self.cap)
            current = self.current_frame
            self.frames.insert(self.current_frame, frame)
            self.n_frames += 1
            if current != 0:
                self.ids.frame_slider.value += 1
            self.live_capture_index = self.ids.frame_slider.value
            self.show_frames()
            self.live_capture = True
            if self.cap:
                Clock.schedule_once(self.update_capture, 1.0 / 30.0)

    def update_capture(self, *args, **kw):
        if not self.cap:
            return
        if not self.live_capture:
            return
        frame = live_snapshot(self.cap)
        if frame is not None:
            self.frames[self.live_capture_index-1] = frame
            self.show_frames()
        if self.cap and self.live_capture:
            Clock.schedule_once(self.update_capture, 1.0 / 30.0)

    def capture(self):
        if self.live_capture:
            return
        frame = snapshot(self.camera_number)
        current = self.current_frame
        self.frames.insert(self.current_frame, frame)
        self.n_frames += 1
        if current != 0:
            self.ids.frame_slider.value += 1
        #self.show_frames()
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
        save_video(self.file_name, self.frames, self.fps)
        launch_video(self.file_name, self.frames)

    def delete_frame(self):
        if self.live_capture:
            return
        #print("delete frame")
        if self.n_frames < 1:
            return
        current = self.current_frame
        self.n_frames -= 1
        self.frames.pop(current-1)
        self.show_frames()
        
    def file_menu(self):
        print("file menu not implemented")
        
    def save(self):
        save_frames(self.file_name, self.frames, self.background_frame)

class TestApp(App):
    def build(self):
        root = Builder.load_string(kv)

        if len(sys.argv) > 1:
            root.file_name = sys.argv[1]
            root.frames, root.background_frame = load_frames(root.file_name)
            if root.frames is None:
                sys.exit(-1)
            root.n_frames = len(root.frames)
            if root.background_frame is not None:
                root.has_background_frame = True

        if root.frames:
            frame = root.frames[0]
        else:
            frame = snapshot(root.camera_number)
        frame_width = frame.shape[1]
        frame_height = frame.shape[0]
        print("frames are {}w x {}h".format(frame_width, frame_height))

        return root
    
TestApp().run()
