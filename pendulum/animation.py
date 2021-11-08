import pygame
import time
from sread import Sensor
from model import Pendulum
pygame.init()

scr_x = 800
scr_y = 600

gameDisplay = pygame.display.set_mode((scr_x, scr_y))
pygame.display.set_caption("This is a test")

sensor = Sensor()
pendulum = Pendulum()
#clock = pygame.time.Clock() # Messes up the serial
crashed = False
data = sensor.update()

prev_time = data[0]
start_x = data[1]
start_y = data[2]

sig_x = data[1]
sig_y = data[2]
min_z = max_z = data[3]

while not crashed:
    gameDisplay.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

    data = sensor.update()

    if data is not None:
        pos_x = int(scr_x/2 + data[1]/2)%scr_x
        pos_y = int(scr_y/2 + data[2]/2)%scr_y
        z_bar = int(scr_y/2 + data[3]/20)%scr_y

        if data[3] > max_z:
            max_z = data[3]
        elif data[3] < min_z:
            min_z = data[3]
        pygame.draw.rect(gameDisplay, (0, 255, 0), [pos_x,
                                                    pos_y,
                                                    10,
                                                    10])
        pygame.draw.rect(gameDisplay, (255, 0, 0), [0,
                                                    0,
                                                    data[0]%scr_x,
                                                    10])
        pygame.draw.rect(gameDisplay, (255, 0, 0), [0,
                                                    10,
                                                    10,
                                                    z_bar])
        prev_time = data[0]

    else:
        pygame.draw.rect(gameDisplay, (0, 0, 255), [scr_x/2,
                                                    scr_y/2,
                                                    50,
                                                    50])
    #print(data)
    pygame.display.update()

    
    #clock.tick(50)

print(f"Min: {min_z}, Max: {max_z}")
pygame.quit()
quit()
