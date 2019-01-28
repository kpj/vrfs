import os
import sys
import mimetypes
import threading

import numpy as np

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    WindowProperties,
    AntialiasAttrib,
    CollideMask, CollisionTraverser,
    CollisionHandlerQueue,
    CollisionNode,
    GeomNode,
    CollisionRay
)

from entities import (
    ErrorEntity,
    DirectoryEntity,
    ImageEntity,
    TextEntity
)


class MyApp(ShowBase):
    def __init__(self, path):
        ShowBase.__init__(self)
        self.verbose = True

        self.setFrameRateMeter(True)
        #self.render.setAntialias(AntialiasAttrib.MAuto)

        self.setup_camera()
        self.setup_controls()
        self.setup_collisions()

        self.scene_node_history = []
        self.scene_node = None

        t = threading.Thread(
            target=self.load_directory, args=(path,))
        t.start()

    def setup_collisions(self):
        self.coll_traverser = CollisionTraverser()  # does actual work of collision detection
        self.coll_handler = CollisionHandlerQueue()  # records collisions that happened

        self.selector_ray = CollisionRay()  # is a CollisionSolid, which is a basic object of the collision system
        self.selector_ray.setFromLens(self.camNode, 0, 0)  # point straight away from camera

        selector_node = CollisionNode('mouseRay')  # encapsulates a CollisionSolid
        selector_node.addSolid(self.selector_ray)

        selector_nodepath = self.camera.attachNewNode(selector_node)
        self.coll_traverser.addCollider(selector_nodepath, self.coll_handler)

        # debug
        if self.verbose:
            self.coll_traverser.showCollisions(self.render)
            selector_nodepath.show()

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
        # keyboard
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

        self.accept('b', self.traverse_history)

        self.key_map = {
            'forward': False, 'backward': False,
            'right': False, 'left': False,
            'up': False, 'down': False
        }

        # mouse
        self.accept('mouse1', self.handle_mouse)

    def traverse_history(self):
        if len(self.scene_node_history) > 0:
            self.scene_node.detachNode()  # remove current scene...
            self.scene_node = self.scene_node_history.pop()
            self.scene_node.reparentTo(self.render)  # ...and activate old one
        else:
            print('History is empty')

    def handle_key(self, key, value):
        self.key_map[key] = value

    def handle_mouse(self):
        # check collisions
        self.coll_traverser.traverse(self.render)
        if self.coll_handler.getNumEntries() > 0:
            self.coll_handler.sortEntries()  # sort by distance
            pickedObj = self.coll_handler.getEntry(0).getIntoNodePath()

            pickedObj = pickedObj.findNetTag('canCollide')
            if not pickedObj.isEmpty():
                func = pickedObj.getPythonTag('callback')
                func()

    def load_directory(self, path):
        # save old scene
        if self.scene_node is not None:
            self.scene_node_history.append(self.scene_node)
            self.scene_node.detachNode()

        # create new scene under dummy node
        dummy = self.render.attachNewNode('dummy')

        # generate layout
        x = 0
        y = 0
        step = 3

        filenum = len(os.listdir(path))
        sidelen = int(np.ceil(np.sqrt(filenum)))
        idx_list = list(np.ndindex((sidelen, sidelen)))
        assert len(idx_list) >= filenum, f'{filenum} < {len(idx_list)}'

        for (i, j), entry in zip(idx_list, os.scandir(path)):
            print(f'Parsing "{entry.name}":', end=' ')
            x, y = i*step, j*step
            pos = (x, 0, y)

            if entry.is_dir():
                if not entry.name.startswith('.'):
                    e = DirectoryEntity(self, dummy, entry.path, pos)
                    e.build()
                print('directory')
                continue

            general_type, _ = mimetypes.guess_type(entry.path)
            if general_type is None:
                ErrorEntity(self, dummy, entry.path, pos).build()
                print('error')
                continue

            type_, subtype = general_type.split('/')
            print(type_, subtype)

            Entity = {
                'image': ImageEntity,
                'text': TextEntity
            }.get(type_, ErrorEntity)

            e = Entity(self, dummy, entry.path, pos)
            e.build()

        # self.render.ls()
        self.scene_node = dummy

    def controlCameraTask(self, task):
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()

        sens = .1
        self.camera.setH(x*sens)
        self.camera.setP(y*sens)

        speed = 10
        dt = globalClock.getDt()  # is magically available from panda3d
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

        if self.verbose:
            self.coll_traverser.traverse(self.render)

        return Task.cont


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <path to directory>')
        sys.exit(-1)

    app = MyApp(sys.argv[1])
    app.run()


if __name__ == '__main__':
    main()
