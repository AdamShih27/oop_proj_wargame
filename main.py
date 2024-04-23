#! /usr/bin/python3
import pygame
import time

from resources.engine import Engine
from resources.country import Country
from resources.weapons import Weapons

from collections import Counter

pygame.init()

from settings import *

window_size = SIZE
window = pygame.display.set_mode(window_size, DEFAULT_FLAG)

pygame.display.set_caption(TITLE)
pygame.display.set_icon(
    pygame.image.load(ICON_PATH).convert_alpha()
)

from visualizer.weapons import ActiveWeapons
from visualizer.countries import Countries
from visualizer.explosions import Explosions
from visualizer.lasers import Lasers
from visualizer.particles import Particles
from visualizer.shake import Shake
from visualizer.text_rect import TextRect

class Game:
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

        self.shake_enabled = True

        self.countries = Countries(self.game.countries.countries, window_size)

    def start(self):
        global window_size

        self.turn_label = TextRect(TITLE_FONT, f"Round {self.game.turn}", GUI_COLOR)
        self.turn_label.rect.topleft = (10, 10)

        quit_game = lambda event: \
            (event.type == pygame.QUIT) or \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            
        toggle_fullscreen = lambda event: \
            (event.type == pygame.KEYDOWN and event.key == pygame.K_F11)
        
        while True:
            for event in pygame.event.get():
                if quit_game(event):
                    return None
                elif toggle_fullscreen(event):
                    self.fullscreen = not self.fullscreen
                    pygame.display.toggle_fullscreen()
                elif event.type == pygame.VIDEORESIZE:
                    window_size = event.size
                    pygame.display.set_mode(event.size, 
                                            (DEFAULT_FLAG | pygame.FULLSCREEN) if self.fullscreen else DEFAULT_FLAG)
                    self.countries.resize(event.size)

            self.window.fill(BACKGROUND_COLOR)

            self.explosions.draw(self.window)
            self.turn_label.draw(self.window)
            self.countries.draw(self.window)
            self.lasers.draw(self.window)
            self.active_weapons.draw(self.window)
            self.particles.draw(self.window, FPS)
            
            time_now = time.time()
            
            if time_now - self.timer > TURN_LENGTH:
                if not self.game.is_finished():
                    self.game.do_turn()
                    self.game.print_events()
                    self.animate_turn()
                    self.turn_label.text = f"Round {self.game.turn}"
                elif self.end_game is None:
                    self.end_game = time.time() + 3
                
                self.timer = time_now

            if self.shake_enabled and self.shake.is_active():
                self.shake.animate(self.window)

            pygame.display.update()
            self.clock.tick(FPS)

            if self.end_game and self.end_game < time.time():
                break

        if self.game.countries.get_alive_count():
            alive = self.game.countries.get_survivor()
            print(f"{alive} is the last one standing.")
        else:
            alive = "No one"
            print("There were no survivors.")
        
        print()
        return alive

    def animate_turn(self):
        for event in self.game.events["Player"]:
            if event["Type"] == "Attack" and event["Success"]:
                start = self.countries.get_pos(event["Source"])
                end_pos = self.countries.get_pos(event["Target"])

                if event["Weapon"] == Weapons.LASER:
                    self.lasers.add(start, end_pos, TURN_LENGTH)
                else:
                    self.active_weapons.add(start, end_pos, event, TURN_LENGTH)

        for event in self.game.events["Death"]:
            end_pos = self.countries.get_pos(event["Target"])
            self.particles.add(end_pos)

        for event in self.game.events["Hit"]:
            if event["Weapon"] == Weapons.NUKE:
                self.shake.start(40)

            pos = self.countries.get_pos(event["Target"])
            self.explosions.add(pos, event["Weapon"])

def show_results(final):
    size = sum(final.values())
    print(f'{"Bot": <15} | {"Wins": <4} | {"Perc"}')
    for bot, wins in final.most_common():
        perc = f'{round(100 * wins / size)}%'
        print(f'{bot: <15} | {wins: <4} | {perc}')

if __name__ == '__main__':
    # Print error messages if not in batch mode
    Country.verbose = False
    
    results = Counter()

    for i in range(4):
        print(f'Game {i + 1}')
        print()
        
        survivor = Game(window).start()
        
        if survivor is None:
            break
        
        results[survivor] += 1
        
    show_results(results)

    pygame.quit()
