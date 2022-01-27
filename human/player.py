'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import pygame
from pygame.locals import *
import sys
import os
CARD_HEIGHT = 726 / 5
CARD_WIDTH = 500 /5
class GameCard(pygame.sprite.Sprite):
    def __init__(self, card, WIDTH, HEIGHT, POS):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA, 32)
        self.surf = self.surf.convert_alpha()
        #self.surf = pygame.Surface((WIDTH+10, 10+HEIGHT))

        """
        self.surf.fill((255,255,255))
        font = pygame.font.SysFont(None, 30)
        txt = font.render(card, True, (0,0,0))
        self.surf.blit(txt, (20,HEIGHT/2-10))
        """

        val = card[0]
        if val == 'T':
            val = '10'
        elif val == 'J':
            val = 'jack'
        elif val == 'Q':
            val = 'queen'
        elif val == 'K':
            val = 'king'
        elif val == 'A':
            val = 'ace'

        suits = {'c':'clubs', 's':'spades', 'h':'hearts','d':'diamonds'}
        if card == ' ':
            image_name = 'back.png'
        else:
            image_name = val + '_of_' + suits[card[1]] + '.png'
        image =pygame.image.load(os.path.join(os.getcwd(), './images/' + image_name))
        image=pygame.transform.scale(image, (WIDTH, HEIGHT))
        self.surf.blit(image, (0,0))
        self.rect = self.surf.get_rect(topleft = POS)

class PlayerInfo(pygame.sprite.Sprite):
    def __init__(self, stack_size, pip, tot_delta, big_blind, WIDTH, HEIGHT, POS):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA, 32)
        self.surf = self.surf.convert_alpha()
        #self.surf.fill((255,255,255))
        font = pygame.font.SysFont(None, 23)

        txt = font.render('Pip: ' + str(pip), True, (0,0,0))
        txt2 = font.render('Stack: ' + str(stack_size), True, (0,0,0))
        txt3 = font.render('Score: ' + str(tot_delta), True, (0,0,0))
        if big_blind:
            tmp = 'Big blind'
        else:
            tmp = 'Small blind'
        txt4 = font.render(tmp, True, (0,0,0))

        self.surf.blit(txt, (10,0))
        self.surf.blit(txt2, (10,30))
        self.surf.blit(txt3, (10,60))
        self.surf.blit(txt4, (10,90))
        self.rect = self.surf.get_rect(topleft = POS)

class GameInfo(pygame.sprite.Sprite):
    def __init__(self, pot, round_num, legal_actions, WIDTH, HEIGHT, POS):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, HEIGHT),pygame.SRCALPHA, 32)
        self.surf = self.surf.convert_alpha()
        #self.surf.fill((255,255,255))
        font = pygame.font.SysFont(None, 23)

        txt = font.render('Pot: ' + str(pot), True, (0,0,0))
        txt2 = font.render('Round #: ' + str(round_num), True, (0,0,0))
        txt4 = font.render('Legal Actions: ', True, (0,0,0))
        self.surf.blit(txt2, (10,0))
        self.surf.blit(txt, (10,30))
        self.surf.blit(txt4, (10,60))
        
        x = 90
        for i in legal_actions:
            txt3 = font.render(i, True, (0,0,0))
            self.surf.blit(txt3, (10, x))
            x+=30
            


        self.rect = self.surf.get_rect(topleft = POS)


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pygame.init()
        pygame.display.set_caption('Pokerbots')
        self.window = pygame.display.set_mode((800,600))

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        self.my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        self.round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        self.big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        if opp_cards == []:
            return
        game_blank_cards = []
        curpos = [10, 30]
        for i in opp_cards:
            self.all_sprites.add(GameCard(i, CARD_WIDTH+0.5, CARD_HEIGHT+0.5, tuple(curpos)))
            curpos[0] += CARD_WIDTH + 10 

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
            font = pygame.font.SysFont(None, 25)
            txt_surface = font.render('Press Return to continue', True, (0,0,0))
            self.window.fill((81,155,118))
            self.window.blit(txt_surface, (500, 500))

         
            for entity in self.all_sprites:
                self.window.blit(entity.surf, entity.rect)
         
            pygame.display.update()
        
        

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        legal_actions_text = []
        legal_actions_keys = []
        if CheckAction in legal_actions:
            legal_actions_keys.append('K')
            legal_actions_text.append('Check - K')
        if CallAction in legal_actions:
            legal_actions_keys.append('L')
            legal_actions_text.append('Call - L')
        if FoldAction in legal_actions:
            legal_actions_keys.append('F')
            legal_actions_text.append('Fold - F')
        if RaiseAction in legal_actions:
            legal_actions_keys.append('R')
            legal_actions_text.append('Raise - R' + str(min_raise) + ' to R' + str(max_raise))

        all_sprites = pygame.sprite.Group()
        #all_sprites.add(PlayerInfo(opp_stack, opp_pip, -self.my_bankroll)
            
        game_blank_cards = []
        curpos = [10, 30]
        for i in range(2):
            game_blank_cards.append(GameCard(' ', CARD_WIDTH+0.5, CARD_HEIGHT+0.5, tuple(curpos)))
            curpos[0] += CARD_WIDTH + 10 
        all_sprites.add(PlayerInfo(opp_stack, opp_pip, -self.my_bankroll, not self.big_blind, 100, 150, (curpos[0], curpos[1])))

        game_my_cards = []
        curpos = [10, 400]
        for i in my_cards:
            game_my_cards.append(GameCard(i, CARD_WIDTH, CARD_HEIGHT, tuple(curpos)))
            curpos[0] += CARD_WIDTH + 10 

        all_sprites.add(PlayerInfo(my_stack, my_pip, self.my_bankroll, self.big_blind,  100, 150, (curpos[0], curpos[1])))
        curpos = [10, 430/2]
        all_sprites.add(GameInfo(my_contribution + opp_contribution, self.round_num,legal_actions_text, 300, 550, (curpos[0] + 5*(CARD_WIDTH + 10), curpos[1])))
        game_board_cards = []
        for i in board_cards:
            game_board_cards.append(GameCard(i, CARD_WIDTH, CARD_HEIGHT, tuple(curpos)))
            curpos[0] += CARD_WIDTH + 10 

        
        
        for i in game_my_cards:
            all_sprites.add(i)

        for i in game_blank_cards:
            all_sprites.add(i)

        for i in game_board_cards:
            all_sprites.add(i)
        self.all_sprites = all_sprites
        text = ''
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if text[0] in legal_actions_keys:
                            
                            if text[0] == 'R':
                                amt = text[1:].strip()
                                if amt.isnumeric():
                                    amt = int(amt)
                                    if amt >= min_raise and amt <= max_raise:
                                        return RaiseAction(amt)
                            elif text[0] =='L':
                                return CallAction()
                            elif text[0] =='K':
                                return CheckAction()
                            elif text[0] == 'F':
                                return FoldAction()

                    elif event.key == pygame.K_BACKSPACE:
                        if text != '':
                            text = text[:-1]
                    else:
                        ch = event.unicode
                        if ch.isalnum():
                            if ch.isalpha():
                                ch = ch.upper()
                            text += ch
            font = pygame.font.SysFont(None, 25)
            txt_surface = font.render('Your action: ' + text, True, (0,0,0))
            self.window.fill((81,155,118))
            self.window.blit(txt_surface, (500, 500))

         
            for entity in all_sprites:
                self.window.blit(entity.surf, entity.rect)
         
            pygame.display.update()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
