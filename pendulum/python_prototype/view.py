#from mcv import Model, Controller#, Observables

import pygame
import numpy as np

from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
RADIUS = 200

SCREEN_X = 2*RADIUS + 40
SCREEN_Y = 2*RADIUS + 40
class View:
    def __init__(self):
        self._controller
        self._model

        pygame.init()
        window_size = (SCREEN_X, SCREEN_Y)
        pygame.display.set_mode(
            window_size,
            flags=DOUBLEBUF | OPENGL
            )
        glOrtho(
            -SCREEN_X/2, SCREEN_X/2,
            -SCREEN_Y/2, SCREEN_Y/2, -1, 1
        )
    
    def setModel(self, model: Model):
        self._model = model
    
    def setController(self, controller: Controller):
        self._controller = controller
    
    def _check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._controller.setIsRunning(False)
                None
        return None

    def _drawPendulum(self, theta: float) -> None:
        pass

    def _drawPredHeight(self, predHeight: float) -> None:
        pass

    def notify(self) -> None:
        modelState = self._model.getState()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._drawPendulum(modelState.theta)
        self._drawPredHeight(modelState.predHeight)

        pygame.display.flip()
