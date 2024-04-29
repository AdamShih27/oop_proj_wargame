#! /usr/bin/python3
import pygame
import time

class Game:
    def __init__(self, window: pygame.Surface):
        self.end_game = None
        self.fullscreen = False
        self.window = window

        self.game = Engine()
        self.clock = pygame.time.Clock()
        self.shake = Shake()
        self.timer = time.time()
        
        self.all_sprites = pygame.sprite.Group()

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

            self.turn_label.draw(self.window)
            self.countries.draw(self.window)
            self.all_sprites.update(self.window)
            
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
                    # self.lasers.add(start, end_pos, TURN_LENGTH)
                    self.all_sprites.add(LaserSprite(start, end_pos, TURN_LENGTH))
                else:
                    # self.active_weapons.add(start, end_pos, event, TURN_LENGTH)
                    self.all_sprites.add(ActiveWeaponSprite(start, end_pos, event, TURN_LENGTH))

        for event in self.game.events["Death"]:
            end_pos = self.countries.get_pos(event["Target"])
            # self.particles.add(end_pos)
            self.all_sprites.add(ParticleSprite(end_pos) for _ in range(100))

        for event in self.game.events["Hit"]:
            if event["Weapon"] == Weapons.NUKE:
                self.shake.start(40)

            pos = self.countries.get_pos(event["Target"])
            # self.explosions.add(pos, event["Weapon"])
            self.all_sprites.add(ExplosionSprite(pos, event["Weapon"]))

def show_results(final):
    size = sum(final.values())
    print(f'{"Bot": <15} | {"Wins": <4} | {"Perc"}')
    for bot, wins in final.most_common():
        perc = f'{round(100 * wins / size)}%'
        print(f'{bot: <15} | {wins: <4} | {perc}')

# check if the script is being run directly (i.e. python main.py) and not imported
if __name__ == '__main__': 
    from resources.engine import Engine
    from resources.country import Country
    from resources.weapons import Weapons

    from collections import Counter

    pygame.init()

    from settings import *

    global window_size
    window_size = SIZE
    window = pygame.display.set_mode(window_size, DEFAULT_FLAG)

    pygame.display.set_caption(TITLE)
    pygame.display.set_icon(
        pygame.image.load(ICON_PATH).convert_alpha()
    )

    from visualizer.countries import Countries
    from visualizer.shake import Shake
    from visualizer.text_rect import TextRect

    from visualizer.weapons import ActiveWeaponSprite
    from visualizer.explosions import ExplosionSprite
    from visualizer.lasers import LaserSprite
    from visualizer.particles import ParticleSprite

    # Print error messages if not in batch mode
    Country.verbose = False
    
    results = Counter()

    for i in range(NUM_ROUNDS):
        print(f'Game {i + 1}')
        print()
        
        survivor = Game(window).start()
        
        if survivor is None:
            break
        
        results[survivor] += 1
        
    show_results(results)

    pygame.quit()
