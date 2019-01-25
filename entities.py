from abc import ABC, abstractmethod

from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage


class BaseEntity(ABC):
    def __init__(
        self,
        fname, render,
        pos
    ):
        self.fname = fname
        self.render = render
        self.pos = pos

    @abstractmethod
    def build(self):
        pass


class ErrorEntity(BaseEntity):
    def build(self):
        error = TextNode('error')

        error.setText('error')
        error.setTextColor(0, 0, 0, 1)

        error.setCardColor(1, 0, 0, 1)
        error.setCardAsMargin(0, 0, 0, 0)
        error.setCardDecal(True)

        textNodePath = self.render.attachNewNode(error)
        textNodePath.setTwoSided(True)
        textNodePath.setScale(0.5)
        textNodePath.setPos(self.pos[0], self.pos[1], self.pos[2])


class ImageEntity(BaseEntity):
    def build(self):
        image = OnscreenImage(
            image=self.fname, pos=self.pos,
            parent=self.render)
        image.setTwoSided(True)


class TextEntity(BaseEntity):
    def build(self):
        text = TextNode('text')

        text.setWordwrap(20.0)
        text.setTextColor(0, 0, 0, 1)

        text.setFrameColor(.8, .8, .8, 1)
        text.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)
        text.setFrameLineWidth(3)

        text.setCardColor(1, 1, 1, 1)
        text.setCardAsMargin(0, 0, 0, 0)
        text.setCardDecal(True)

        textNodePath = self.render.attachNewNode(text)
        textNodePath.setTwoSided(True)
        textNodePath.setScale(0.1)
        textNodePath.setPos(self.pos[0]-1, self.pos[1], self.pos[2]+1)

        with open(self.fname) as fd:
            text.setText(fd.read(400))
