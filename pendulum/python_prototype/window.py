"""Creates and handles a pygame window"""

import pygame
import numpy as np

from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *

#from sread import Sensor
from model import Pendulum

BEAM = 200
SCALE = BEAM * 0.05

SCREEN_X = 2*BEAM + 40
SCREEN_Y = 2*BEAM + 40



class Window:
    def __init__(self):
        pygame.init()
        window_size = (SCREEN_X, SCREEN_Y)
        pygame.display.set_mode(window_size, flags=DOUBLEBUF | OPENGL)
        glOrtho(-SCREEN_X/2, SCREEN_X/2, -SCREEN_Y/2, SCREEN_Y/2, -1, 1)

    def check_quit(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 1
        return 0

    def draw_line(self, start_coords, end_coords, color=(0, 1, 0)):
        glBegin(GL_LINES)
        glColor3d(*color)
        glVertex2f(*start_coords)
        glVertex2f(*end_coords)
        glEnd()

    def draw_pendulum(self, angle, color=(0,1,0)):
        x_coord = BEAM * np.sin(angle)
        y_coord = BEAM * -np.cos(angle)
        self.draw_line((0, 0), (x_coord, y_coord), color)

    def draw_arc(self, centre, r, start, end, color=(1,0,0)):
        pi4 = np.pi/2
        conversion = 50
        start = int((start-pi4)*conversion)
        end = int((end-pi4)*conversion)
        if start <= end:
            points = range(start, end)
        else:
            points = range(end, start)

        glEnable(GL_POINT_SMOOTH)
        glPointSize(1)
        glBegin(GL_POINTS)
        glColor3d(*color)
        for i in points:
            coords = (centre[0] + r*np.cos(i/conversion),
                            centre[1] + r*np.sin(i/conversion))
            glVertex2f(*coords)
        glEnd()
            
    def draw_z(self, z_val, radius=20):
        if z_val >= 0:
            self.draw_arc((0, 0), radius, 0, z_val)
        else:
            self.draw_arc((0, 0), radius, z_val, 0, (0, 0, 1))

    def draw_height(self, height):
        start_coords = (-BEAM, -BEAM+ (height*2*BEAM))
        end_coords =  (BEAM, -BEAM+ (height*2*BEAM))
        self.draw_line(start_coords, end_coords, (1, 0, 0))

    def draw_dots(self, dots, color=(1, 1, 0)):
        glEnable(GL_POINT_SMOOTH)
        glPointSize(1)
        glBegin(GL_POINTS)
        glColor3d(*color)
        for dot in dots:
            glVertex2f(*dot)
        glEnd()

    def main(self):
        prev_z_vals = [0]
        x_y_trace = []
        #t_z_trace = []
        z_count = 0
        #clock = pygame.time.Clock()

        pendulum = Pendulum()

        while self.check_quit() == 0:

            # only refresh screen if there's new data
            if pendulum.update() == 0:

                x_val, y_val = pendulum.get_coords()
                x_val *= BEAM
                y_val *= BEAM

                x_ival, y_ival = pendulum.get_int_coords()
                x_ival *= BEAM
                y_ival *= BEAM

                #int_vals = [x_ival, y_ival]
                #mag_val = np.sqrt(x_val**2 + y_val**2)
                #z_val = data[3]/50
                #t_val = (data[0] - t_0)/10
                vals = [x_val, y_val]
                pred_height = pendulum.pred_height * SCALE
                torque = pendulum.get_torque()
                #t_z_vals = [t_val, pendulum.theta_ddot/10]
                x_y_trace.append(vals)
                #t_z_trace.append(t_z_vals)

                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                self.draw_z(pendulum.state.theta_dot/10)
                self.draw_z(torque/10, 40)
                self.draw_z(pendulum.state.theta_ddot/10, 60)
                #self.draw_z(pendulum.int_theta*180/np.pi, 80)
                #self.draw_dots(x_y_trace)
                self.draw_arc((0,0), BEAM, pendulum.prev_peak,
                              pendulum.state.theta, (1,1,0))
                #self.draw_dots(t_z_trace, (0,1,1))

                self.draw_pendulum(pendulum.state.theta)
                self.draw_pendulum(pendulum.int_theta, (1,0.7,0))

                self.draw_height(pred_height)



                z_check = float(pendulum.state.theta_dot-0.1) * float(prev_z_vals[0]+0.1)
                if z_check < 0:
                    z_count += 1
                    x_y_trace = []

                    #print(f"{z_count}: {data[3]} * {prev_z_vals[0]} = {z_check}")
                prev_z_vals = (prev_z_vals + [pendulum.state.theta_dot])[1:]
                
                pygame.display.flip()
        
        pendulum.write_to_csv()


if __name__ == '__main__':
    Window().main()
