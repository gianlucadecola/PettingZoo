from numpy.lib.shape_base import tile
from pettingzoo import AECEnv
from pettingzoo.utils.agent_selector import agent_selector
from gym import spaces
import rlcard
import random
from rlcard.utils.utils import print_card
import numpy as np
from pettingzoo.utils import wrappers
from .rlcard_base import RLCardBase
import os


def get_image(path):
    import pygame
    from os import path as os_path
    cwd = os_path.dirname(__file__)
    image = pygame.image.load(cwd + '/' + path)
    return image


def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human', 'rgb_array'], "name": "texas_holdem_v3"}

    def __init__(self):
        super().__init__("limit-holdem", 2, (72,))

    def render(self, mode='human'):

        def calculate_width(self, screen_width, i):
            return int(((screen_width / ((np.ceil(len(self.possible_agents) / 2) + 1) * np.ceil((i + 1) / 2)))))

        def calculate_offset(hand, j, tile_size):
            return int((len(hand) * (tile_size / 2)) - ((j) * tile_size))

        def calculate_height(screen_height, divisor, multiplier, tile_size, offset):
            return int(multiplier * screen_height / divisor + tile_size * offset)

        screen_width = 1600
        screen_height = 1000

        if mode == "human":
            import pygame

            if self.screen is None:
                pygame.init()
                self.screen = pygame.display.set_mode((screen_width, screen_height))

            pygame.event.get()
            # Setup dimensions for card size and setup for colors
            tile_size = screen_width / 10

            bg_color = (31, 153, 131)
            white = (255, 255, 255)
            self.screen.fill(bg_color)
            font = pygame.font.Font('freesansbold.ttf', 36)

            # Load and blit all images for each card in each player's hand
            for i, player in enumerate(self.possible_agents):
                state = self.env.game.get_state(self._name_to_int(player))
                for j, card in enumerate(state['hand']):
                    # Load specified card
                    card_img = get_image(os.path.join('img', card + '.png'))
                    card_img = pygame.transform.scale(card_img, (int(tile_size * (142 / 197)), int(tile_size)))
                    # Players with even id go above public cards
                    if i % 2 == 0:
                        self.screen.blit(card_img, ((calculate_width(self, screen_width, i) - calculate_offset(state['hand'], j, tile_size)), calculate_height(screen_height, 4, 1, tile_size, -1)))
                    # Players with odd id go below public cards
                    else:
                        self.screen.blit(card_img, ((calculate_width(self, screen_width, i) - calculate_offset(state['hand'], j, tile_size)), calculate_height(screen_height, 4, 3, tile_size, 0)))

                # Load and blit text for player name
                text = font.render(player, True, white)
                textRect = text.get_rect()
                if i % 2 == 0:
                    textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 1, tile_size, -(5 / 4)))
                else:
                    textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 3, tile_size, -(1 / 4)))
                self.screen.blit(text, textRect)

                # Load and blit number of poker chips for each player
                text = font.render('Chips: ' + str(state['my_chips']), True, white)
                textRect = text.get_rect()
                if i % 2 == 0:
                    textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 1, tile_size, (1 / 4)))
                else:
                    textRect.center = (calculate_width(self, screen_width, i), calculate_height(screen_height, 4, 3, tile_size, (5 / 4)))
                self.screen.blit(text, textRect)

            # Load and blit public cards
            for i, card in enumerate(state['public_cards']):
                card_img = get_image(os.path.join('img', card + '.png'))
                card_img = pygame.transform.scale(card_img, (int(tile_size * (142 / 197)), int(tile_size)))
                self.screen.blit(card_img, ((((screen_width / 2) - calculate_offset(state['public_cards'], i, tile_size)), calculate_height(screen_height, 2, 1, tile_size, -(1 / 2)))))

            pygame.display.update()

        observation = np.array(pygame.surfarray.pixels3d(self.screen))

        return np.transpose(observation, axes=(1, 0, 2)) if mode == "rgb_array" else None
