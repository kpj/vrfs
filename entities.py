import os
import threading
from abc import ABC, abstractmethod

from panda3d.core import TextNode, CollisionBox, CollisionNode
from direct.gui.OnscreenImage import OnscreenImage


class BaseEntity(ABC):
    def __init__(self, base, ref_node, fname, pos):
        self.base = base

        self.fname = fname
        self.ref_node = ref_node
        self.pos = pos

    @abstractmethod
    def assemble(self):
        pass

    def build(self):
        self.assemble()
        self.setup_collision_handling()

    def on_click(self):
        """This should be overridden."""
        pass

    def setup_collision_handling(self):
        node = CollisionNode('entity collision node')
        box = CollisionBox(self.pos, 1, .2, 1)
        node.addSolid(box)

        nodepath = self.ref_node.attachNewNode(node)
        nodepath.setTag('canCollide', '1')
        nodepath.setPythonTag('callback', self.on_click)

        if self.base.verbose:
            nodepath.show()


class ErrorEntity(BaseEntity):
    def assemble(self):
        error = TextNode('error')

        error.setText('error')
        error.setTextColor(0, 0, 0, 1)
        error.setAlign(TextNode.A_center)

        error.setCardColor(1, 0, 0, 1)
        error.setCardAsMargin(0, 0, 0, 0)
        error.setCardDecal(True)

        textNodePath = self.ref_node.attachNewNode(error)
        textNodePath.setTwoSided(True)
        textNodePath.setScale(0.5)
        textNodePath.setPos(self.pos[0], self.pos[1], self.pos[2])


class DirectoryEntity(BaseEntity):
    def assemble(self):
        folder = TextNode('Directory')

        base = os.path.basename(self.fname) or os.path.basename(self.fname[:-1])
        folder.setText(f'folder:\n"{base}"')
        folder.setTextColor(1, 1, 1, 1)

        textNodePath = self.ref_node.attachNewNode(folder)
        textNodePath.setTwoSided(True)
        textNodePath.setScale(.5)
        textNodePath.setPos(self.pos[0]-1, self.pos[1], self.pos[2])

    def on_click(self):
        print(f'Traversing into: "{self.fname}"')
        t = threading.Thread(
            target=self.base.load_directory,
            args=(self.fname,))
        t.start()


class ImageEntity(BaseEntity):
    def assemble(self):
        image = OnscreenImage(
            image=self.fname, pos=self.pos,
            parent=self.ref_node)
        image.setTwoSided(True)


class TextEntity(BaseEntity):
    def assemble(self):
        text = TextNode('text')

        text.setWordwrap(20.0)
        text.setTextColor(0, 0, 0, 1)

        text.setFrameColor(.8, .8, .8, 1)
        text.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
        text.setFrameLineWidth(3)

        text.setCardColor(1, 1, 1, 1)
        text.setCardAsMargin(0, 0, 0, 0)
        text.setCardDecal(True)

        textNodePath = self.ref_node.attachNewNode(text)
        textNodePath.setTwoSided(True)
        textNodePath.setScale(0.1)
        textNodePath.setPos(self.pos[0]-1, self.pos[1], self.pos[2]+1)  # TODO: why +-1?

        try:
            with open(self.fname) as fd:
                text.setText(fd.read(400))
        except UnicodeDecodeError:
            with open(self.fname, 'rb') as fd:
                text.setText(str(fd.read(400)))
