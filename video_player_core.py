
from pyglet.gl import *
import pyglet
from pyglet.window import key
import cv2
import sys

def draw_rect(x, y, width, height):
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()


class Control(pyglet.event.EventDispatcher):
    x = y = 0
    width = height = 10

    def __init__(self, parent):
        super(Control, self).__init__()
        self.parent = parent

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and
                self.y < y < self.y + self.height)

    def capture_events(self):
        self.parent.push_handlers(self)

    def release_events(self):
        self.parent.remove_handlers(self)


class Button(Control):
    charged = False

    def draw(self):
        if self.charged:
            glColor3f(0, 1, 0)
        draw_rect(self.x, self.y, self.width, self.height)
        glColor3f(1, 1, 1)
        self.draw_label()

    def on_mouse_press(self, x, y, button, modifiers):
        self.capture_events()
        self.charged = True

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.charged = self.hit_test(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        if self.hit_test(x, y):
            self.dispatch_event('on_press')
        self.charged = False


Button.register_event_type('on_press')


class TextButton(Button):
    def __init__(self, *args, **kwargs):
        super(TextButton, self).__init__(*args, **kwargs)
        self._text = pyglet.text.Label('', anchor_x='center', anchor_y='center')

    def draw_label(self):
        self._text.x = self.x + self.width / 2
        self._text.y = self.y + self.height / 2
        self._text.draw()

    def set_text(self, text):
        self._text.text = text

    text = property(lambda self: self._text.text,
                    set_text)


class Slider(Control):
    THUMB_WIDTH = 6
    THUMB_HEIGHT = 10
    GROOVE_HEIGHT = 2

    def draw(self):
        center_y = self.y + self.height / 2
        draw_rect(self.x, center_y - self.GROOVE_HEIGHT / 2,
                  self.width, self.GROOVE_HEIGHT)
        pos = self.x + self.value * self.width / (self.max - self.min)
        draw_rect(pos - self.THUMB_WIDTH / 2, center_y - self.THUMB_HEIGHT / 2,
                  self.THUMB_WIDTH, self.THUMB_HEIGHT)

    def coordinate_to_value(self, x):
        return float(x - self.x) / self.width * (self.max - self.min) + self.min

    def on_mouse_press(self, x, y, button, modifiers):
        value = self.coordinate_to_value(x)
        self.capture_events()
        self.dispatch_event('on_begin_scroll')
        self.dispatch_event('on_change', value)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        value = min(max(self.coordinate_to_value(x), self.min), self.max)
        self.dispatch_event('on_change', value)

    def on_mouse_release(self, x, y, button, modifiers):
        self.release_events()
        self.dispatch_event('on_end_scroll')


Slider.register_event_type('on_begin_scroll')
Slider.register_event_type('on_end_scroll')
Slider.register_event_type('on_change')


class PlayerWindow(pyglet.window.Window):
    GUI_WIDTH = 400
    GUI_HEIGHT = 40
    GUI_PADDING = 4
    GUI_BUTTON_HEIGHT = 16

    def __init__(self, player):
        super(PlayerWindow, self).__init__(caption='Homemade Media Player',
                                           visible=False,
                                           resizable=True)
        self.player = player
        self.player.push_handlers(self)
        # self.player.eos_action = self.player.EOS_PAUSE

        self.slider = Slider(self)
        self.slider.x = self.GUI_PADDING
        self.slider.y = self.GUI_PADDING * 2 + self.GUI_BUTTON_HEIGHT
        self.slider.on_begin_scroll = lambda: player.pause()
        self.slider.on_end_scroll = lambda: player.play()
        self.slider.on_change = lambda value: player.seek(value)

        self.play_pause_button = TextButton(self)
        self.play_pause_button.x = self.GUI_PADDING
        self.play_pause_button.y = self.GUI_PADDING
        self.play_pause_button.height = self.GUI_BUTTON_HEIGHT
        self.play_pause_button.width = 45
        self.play_pause_button.on_press = self.on_play_pause

        win = self
        self.window_button = TextButton(self)
        self.window_button.x = self.play_pause_button.x + \
                               self.play_pause_button.width + self.GUI_PADDING
        self.window_button.y = self.GUI_PADDING
        self.window_button.height = self.GUI_BUTTON_HEIGHT
        self.window_button.width = 90
        self.window_button.text = 'Window'
        self.window_button.on_press = lambda: win.set_fullscreen(False)

        self.controls = [
            self.slider,
            self.play_pause_button,
            self.window_button,
        ]

        x = self.window_button.x + self.window_button.width + self.GUI_PADDING
        i = 0
        for screen in self.display.get_screens():
            screen_button = TextButton(self)
            screen_button.x = x
            screen_button.y = self.GUI_PADDING
            screen_button.height = self.GUI_BUTTON_HEIGHT
            screen_button.width = 120
            screen_button.text = 'Full Screen %d' % (i + 1)
            screen_button.on_press = \
                (lambda s: lambda: win.set_fullscreen(True, screen=s))(screen)
            self.controls.append(screen_button)
            i += 1
            x += screen_button.width + self.GUI_PADDING

    def on_eos(self):
        self.gui_update_state()

    def gui_update_source(self):
        if self.player.source:
            source = self.player.source
            self.slider.min = 0.
            self.slider.max = source.duration
        self.gui_update_state()

    def gui_update_state(self):
        if self.player.playing:
            self.play_pause_button.text = 'Pause'
        else:
            self.play_pause_button.text = 'Play'

    def get_video_size(self):
        if not self.player.source or not self.player.source.video_format:
            return 0, 0
        video_format = self.player.source.video_format
        width = video_format.width
        height = video_format.height
        if video_format.sample_aspect > 1:
            width *= video_format.sample_aspect
        elif video_format.sample_aspect < 1:
            height /= video_format.sample_aspect
        return width, height

    def set_default_video_size(self):
        '''Make the window size just big enough to show the current
        video and the GUI.'''
        width = self.GUI_WIDTH
        height = self.GUI_HEIGHT
        video_width, video_height = self.get_video_size()
        width = max(width, video_width)
        height += video_height
        self.set_size(int(width), int(height))

    def on_resize(self, width, height):
        '''Position and size video image.'''
        super(PlayerWindow, self).on_resize(width, height)

        self.slider.width = width - self.GUI_PADDING * 2

        height -= self.GUI_HEIGHT
        if height <= 0:
            return

        video_width, video_height = self.get_video_size()
        if video_width == 0 or video_height == 0:
            return

        display_aspect = width / float(height)
        video_aspect = video_width / float(video_height)
        if video_aspect > display_aspect:
            self.video_width = width
            self.video_height = width / video_aspect
        else:
            self.video_height = height
            self.video_width = height * video_aspect
        self.video_x = (width - self.video_width) / 2
        self.video_y = (height - self.video_height) / 2 + self.GUI_HEIGHT

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:
            if control.hit_test(x, y):
                control.on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.on_play_pause()
        elif symbol == key.ESCAPE:
            self.dispatch_event('on_close')

    def on_close(self):
        self.player.pause()
        self.close()

    def on_play_pause(self):

        if self.player.playing:
            self.player.pause()
        else:
            if self.player.time >= self.player.source.duration:
                self.player.seek(0)
            self.player.play()
        self.gui_update_state()

    def on_draw(self):
        self.clear()
        # print(self.player.time, self.player.source.duration)
        if self.player.time >= self.player.source.duration - 1:
            sys.exit()
        else:
            pass
        # Video
        if self.player.source and self.player.source.video_format:
            self.player.get_texture().blit(self.video_x,
                                           self.video_y,
                                           width=self.video_width,
                                           height=self.video_height)

        # GUI
        self.slider.value = self.player.time
        for control in self.controls:
            control.draw()

def MAIN(filename):
    vc = cv2.VideoCapture(filename)
    size = (int(vc.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    vc.release()
    player = pyglet.media.Player()
    window = PlayerWindow(player)

    source = pyglet.media.load(filename)
    player.queue(source)

    window.gui_update_source()
    window.set_default_video_size()

    window.set_size(size[0], size[1])
    window.set_visible(True)

    window.gui_update_state()
    player.play()

    pyglet.app.run()


if __name__ == '__main__':
    filename = 'bad_apple.flv'
    MAIN(filename)