#! /usr/bin/python3
import pygame
import time

from resources.engine import Engine
from resources.country import Country
from resources.weapons import Weapons

# try:
#     from visualizer.optimize_dirty_rects import optimize_dirty_rects
# except ImportError:
#     optimize_dirty_rects = None

pygame.init()
DEFAULT_FLAG = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
SIZE = (800, 600)
window = pygame.display.set_mode(SIZE, DEFAULT_FLAG)

from visualizer.weapons import ActiveWeapons
from visualizer.countries import Countries
from visualizer.explosions import Explosions
from visualizer.lasers import Lasers
from visualizer.particles import Particles
from visualizer.shake import Shake
from visualizer.text_rect import TextRect


BLACK = pygame.Color(0, 0, 0)

GUI_COLOUR = pygame.Color(0, 180, 180)

nuclearIcon = pygame.image.load("images/nuclear.png").convert_alpha()
pygame.display.set_icon(nuclearIcon)

TITLE_FONT = pygame.font.Font("fonts/FROSTBITE-Narrow Bold.ttf", 24)


class Game:
    # BATCH = True
    # frame = 0
    FPS = 60
    TURN_LENGTH = 0.2

    def __init__(self, window: pygame.Surface):
        self.end_game = None
        self.fullscreen = False
        self.window = window

        self.game = Engine()
        self.clock = pygame.time.Clock()
        self.active_weapons = ActiveWeapons()
        self.explosions = Explosions()
        self.lasers = Lasers()
        self.particles = Particles()
        self.shake = Shake()
        self.timer = time.time()

        # self.show_explosions = True
        self.shake_enabled = True
        # self.dirty_rect_enabled = False

        # self.old_dirty_rects = []

        self.countries = Countries(self.game.countries.countries, SIZE)

    def start(self):
        global SIZE

        running = True
        self.turn_label = TextRect(TITLE_FONT, f"Round {self.game.turn}", GUI_COLOUR)
        self.turn_label.rect.topleft = (10, 10)

        quit_game = lambda event: \
            (event.type == pygame.QUIT) or \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            
        toggle_fullscreen = lambda event: \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_F11)
        
        while running:
            for event in pygame.event.get():
                if quit_game(event):
                    running = False
                    pygame.quit()
                    return 1
                
                elif toggle_fullscreen(event):
                    self.fullscreen = not self.fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.VIDEORESIZE:
                    SIZE = event.size
                    pygame.display.set_mode(event.size, 
                                            (DEFAULT_FLAG | pygame.FULLSCREEN) if self.fullscreen else DEFAULT_FLAG)
                    self.countries.resize(event.size)

            self.window.fill(BLACK)

            self.explosions.draw(self.window)
            self.turn_label.draw(self.window)
            self.countries.draw(self.window)
            self.lasers.draw(self.window)
            self.active_weapons.draw(self.window)
            self.particles.draw(self.window, self.FPS)

            if time.time() - self.timer > self.TURN_LENGTH * self.game.turn:
                if not self.game.is_finished():
                    self.game.do_turn()
                    self.game.print_events()
                    self.animate_turn()
                    self.turn_label.text = f"Round {self.game.turn}"

                elif not self.end_game:
                    self.end_game = time.time()

                    # if self.BATCH:
                    self.end_game += 3

            if self.shake_enabled and self.shake.is_active():
                self.shake.animate(self.window)

            pygame.display.update()
            self.clock.tick(self.FPS)

            if self.end_game and self.end_game < time.time():
                break

        if self.game.countries.get_alive_count():
            alive = self.game.countries.get_survivor()
            print(f"{alive} is the last one standing.")
        else:
            print("There were no survivors.")

        # if self.BATCH:
        return 0
        # else:
        #     return self._finish_game()

    def animate_turn(self):
        for event in self.game.events["Player"]:
            if event["Type"] == "Attack" and event["Success"]:
                start = self.countries.get_pos(event["Source"])
                end_pos = self.countries.get_pos(event["Target"])

                if event["Weapon"] == Weapons.LASER:
                    self.lasers.add(start, end_pos, self.TURN_LENGTH)
                else:
                    self.active_weapons.add(start, end_pos, event, self.TURN_LENGTH)

        for event in self.game.events["Death"]:
            end_pos = self.countries.get_pos(event["Target"])
            self.particles.add(end_pos)

        for event in self.game.events["Hit"]:
            if event["Weapon"] == Weapons.NUKE:
                self.shake.start(40)

            pos = self.countries.get_pos(event["Target"])
            self.explosions.add(pos, event["Weapon"])

    # def screenshot(self):
    #     path = os.path.join("screenshots", str(Game.frame) + '.png')
    #     os.makedirs(os.path.dirname(path), exist_ok=True)
    #     pygame.image.save(self.window, path)
    #     Game.frame += 1

    # @staticmethod
    # def press_f11(event):
    #     return 

    # @staticmethod
    # def quit_game(event):
    #     return 

    # def toggle_fullscreen(self):
    #     self.fullscreen = not self.fullscreen

    #     if self.fullscreen:
    #         flag = DEFAULT_FLAG | pygame.FULLSCREEN

    #     pygame.display.set_mode(SIZE, flag)


if __name__ == "__main__":
    # Print error messages if not in batch mode
    Country.verbose = False

    while True:
        game = Game(window)
        player_quit = game.start()

        if player_quit:
            break

    pygame.quit()
