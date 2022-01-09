'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import eval7
import random

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
        pass

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
        #### PARAMETERS ####
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round

        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game

        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS

        my_cards = round_state.hands[active]  # your cards

        big_blind = bool(active)  # True if you are the big blind
        
        #### LOGIC ####
        self.known_cards = []

        pass
    
    def do_monte_carlo(self, hole, num_iterations, board=None, known=None):
        """
        Runs a Monte Carlo simulation on the current hand

        Arguments:
        hand: the current cards in the hand
        num_iterations: the number of Monte Carlo iterations to perform
        board: the current cards in the board
        known: the cards that are known not to be in the deck (possibly due to knowledge from swapping)
        
        Returns: 
        The probability of winning
        """
        if board is None:
            board = []
        if known is None:
            known = []
            
        deck = eval7.Deck()
        
        hole_cards = {eval7.Card(card) for card in hole}
        board_cards = {eval7.Card(card) for card in board}
        known_cards = {eval7.Card(card) for card in known}
        
        for card in hole_cards | board_cards | known_cards:
            deck.cards.remove(card)
            

        score = 0

        for _ in range(num_iterations):
            deck.shuffle()

            revealed_count = len(board)

            drawn = deck.peek(2 + (5 - revealed_count))
            
            opp_hole = drawn[:2]
            unrevealed_board = drawn[2:]
            
            total_board = list(board_cards) + unrevealed_board
            
            hand = list(hole_cards) + total_board
            opp_hand = opp_hole + total_board
            
            our_value = eval7.evaluate(hand)
            opp_value = eval7.evaluate(opp_hand)
            
            if our_value > opp_value:
                score += 2
            elif our_value == opp_value:
                score += 1

        return score / (2 * num_iterations)

        
        

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
        #### PARAMETERS ####
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round

        previous_state = terminal_state.previous_state  # RoundState before payoffs

        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended

        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        
        #### LOGIC ####

        pass

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
        #### PARAMETERS ####
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
        
        pot_total = my_contribution + opp_contribution

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        #### LOGIC ####
        
        if street < 3:
            self.original_hand = my_cards
            self.known_cards = []
        if street == 3 or street == 4:
            for card in self.original_hand:
                if card not in my_cards:
                    self.known_cards.append(card)
                    
            self.original_hand = my_cards

        
        if street < 3:
            raise_amount = int(my_pip + continue_cost + 0.4 * (pot_total + continue_cost))
        else:
            raise_amount = int(my_pip + continue_cost + 0.75 * (pot_total + continue_cost))
        
        if RaiseAction in legal_actions:
            raise_amount = max([min_raise, raise_amount])
            raise_amount = min([max_raise, raise_amount])

        if (RaiseAction in legal_actions and (raise_amount <= my_stack)):
            temp_action = RaiseAction(raise_amount)
        elif (CallAction in legal_actions and (continue_cost <= my_stack)):
            temp_action = CallAction()
        elif CheckAction in legal_actions:
            temp_action = CheckAction()
        else:
            temp_action = FoldAction()

        _MONTE_CARLO_ITERS = 100
        strength = self.do_monte_carlo(my_cards, _MONTE_CARLO_ITERS, board_cards, self.known_cards)

        if continue_cost > 0: 
            _SCARY = 0
            if continue_cost > 6:
                _SCARY = 0.1
            if continue_cost > 15: 
                _SCARY = .2
            if continue_cost > 50: 
                _SCARY = 0.35

            strength = max(0, strength - _SCARY)
            pot_odds = continue_cost/(pot_total + continue_cost)

            if strength >= pot_odds: # nonnegative EV decision
                if strength > 0.5 and random.random() < strength: 
                    my_action = temp_action
                else: 
                    my_action = CallAction()
            
            else: #negative EV
                my_action = FoldAction()
                
        else: # continue cost is 0  
            if random.random() < strength: 
                my_action = temp_action
            else: 
                my_action = CheckAction()
            

        return my_action


if __name__ == '__main__':
    run_bot(Player(), parse_args())
