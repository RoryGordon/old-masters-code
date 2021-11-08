from __future__ import division
import pygame
import numpy
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from OpenGL.arrays import vbo

class Text:
    def __init__(self):
        self.img = pygame.font.Font(None, 50).render("Testing", True, (255, 255, 255))
        w, h = self.img.get_size()
        self.texture = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        data = pygame.image.tostring(self.img, "RGBA", 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    def set_text(self, text_string, color = (255,255,255)):
        self.img = pygame.font.Font(None, 50).render(text_string, True, color)
        w, h = self.img.get_size()
        #glBindTexture(GL_TEXTURE_2D, self.texture)
        data = pygame.image.tostring(self.img, "RGBA", 1)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    def draw_text(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #glTranslate(-1, -1, 0)
        glScale(2 / 600, 2 / 400, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glBegin(GL_QUADS)
        x0, y0 = 10, 10
        w, h = self.img.get_size()
        for dx, dy in [(0, 0), (0, 1), (1, 1), (1, 0)]:
            glVertex(x0 + dx * w, y0 + dy * h, 0)
            glTexCoord(dy, 1 - dx)
        glEnd()