import os
import sys
import mimetypes
import threading

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties

from entities import (
    ErrorEntity,
    DiretoryEntity,
    ImageEntity,
    TextEntity
)


class MyApp(ShowBase):
    def __init__(self, path):
        ShowBase.__init__(self)

        self.setFrameRateMeter(True)

        self.setup_camera()
        self.setup_controls()

        t = threading.Thread(
            target=self.load_directory, args=(path,))
        t.start()

    def setup_camera(self):
        self.disableMouse()

        props = WindowProperties()
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

        self.camera.setPos(2, -20, 3)

        self.taskMgr.add(self.controlCameraTask, 'controlCameraTask')
        # self.oobe()

    def setup_controls(self):
        self.accept('escape', sys.exit)

        self.accept('w', self.handle_key, ['forward', True])
        self.accept('w-up', self.handle_key, ['forward', False])

        self.accept('s', self.handle_key, ['backward', True])
        self.accept('s-up', self.handle_key, ['backward', False])

        self.accept('a', self.handle_key, ['left', True])
        self.accept('a-up', self.handle_key, ['left', False])

        self.accept('d', self.handle_key, ['right', True])
        self.accept('d-up', self.handle_key, ['right', False])

        self.accept('space', self.handle_key, ['up', True])
        self.accept('space-up', self.handle_key, ['up', False])

        self.accept('shift', self.handle_key, ['down', True])
        self.accept('shift-up', self.handle_key, ['down', False])

        self.key_map = {
            'forward': False, 'backward': False,
            'right': False, 'left': False,
            'up': False, 'down': False
        }

    def handle_key(self, key, value):
        self.key_map[key] = value

    def load_directory(self, path):
        x = 0
        y = 0

        for entry in os.scandir(path):
            if entry.is_dir():
                DiretoryEntity(entry.path, self.render, (x, 0, y)).build()
                continue

            general_type, _ = mimetypes.guess_type(entry.path)
            if general_type is None:
                ErrorEntity(entry.path, self.render, (x, 0, y)).build()
                continue

            type_, subtype = general_type.split('/')

            Entity = {
                'image': ImageEntity,
                'text': TextEntity
            }.get(type_, ErrorEntity)

            try:
                Entity(entry.path, self.render, (x, 0, y)).build()
            except:
                ErrorEntity(entry.path, self.render, (x, 0, y)).build()

            x += 3
            if x > 6:
                x = 0
                y += 3

    def controlCameraTask(self, task):
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        sens = .1
        self.camera.setH(x*sens)
        self.camera.setP(y*sens)

        speed = .5
        dt = 1  # self.globalClock.getDt()
        if self.key_map['forward']:
            self.camera.setPos(self.camera, 0, speed*dt, 0)
        if self.key_map['backward']:
            self.camera.setPos(self.camera, 0, -speed*dt, 0)
        if self.key_map['left']:
            self.camera.setPos(self.camera, -speed*dt/2, 0, 0)
        if self.key_map['right']:
            self.camera.setPos(self.camera, speed*dt/2, 0, 0)
        if self.key_map['up']:
            self.camera.setPos(self.camera, 0, 0, speed*dt/2)
        if self.key_map['down']:
            self.camera.setPos(self.camera, 0, 0, -speed*dt/2)

        # print(self.camera.getPos(), x, y)
        return Task.cont


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <path to directory>')
        sys.exit(-1)

    app = MyApp(sys.argv[1])
    app.run()


if __name__ == '__main__':
    main()
