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
import pandas as pd

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
        strengths = pd.read_csv("hole_strengths.csv")
        self.strengths = dict(zip(strengths.Holes, strengths.Strengths))
        self.average_continue_cost = 2 
        self.continue_cost_count = 1
        
        self.preflop_num_raises = 0
        self.preflop_num_calls = 0
        self.preflop_num_folds = 0
        
        self.bluff_probability = 0.1
        
        # 0.3 - 0.45 - 
        # 0.45 - 0.6
        # 0.6 - 0.75
        # 0.75 - 0.9

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
        self.is_big_blind = big_blind

        self.round_num = round_num
        self.bluffing = False
        pass
    
    def do_monte_carlo(self, hole, num_iterations, street, board=None, known=None):
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
        if street < 3:
            card_1, card_2 = hole

            rank_1, suit_1 = card_1 
            rank_2, suit_2 = card_2 
            
            if suit_1 == suit_2:
                if rank_1 + rank_2 + "s" in self.strengths:
                    return self.strengths[rank_1 + rank_2 + "s"]
                else:
                    return self.strengths[rank_2 + rank_1 + "s"]
            else:
                if rank_1 + rank_2 + "o" in self.strengths:
                    return self.strengths[rank_1 + rank_2 + "o"]
                else:
                    return self.strengths[rank_2 + rank_1 + "o"]

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
        # print("delta", my_delta)
        if street == 0 and my_delta > 0:
            # print("Folded")
            self.preflop_num_folds += 1
            
        if self.bluffing:
            if my_delta > 0:
                print("Yess")
            else:
                print("Noo")

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

        exploit_excess_folding = 0 
        _MONTE_CARLO_ITERS = 100
        strength = self.do_monte_carlo(my_cards, _MONTE_CARLO_ITERS, street, board_cards, self.known_cards)
        
        if street < 3:
            # if strength > 0.7 and not self.is_big_blind:
            #     raise_amount = int(my_pip + continue_cost + (strength-0.1) * (pot_total + continue_cost))
            #     # raise_amount = 80
            # else:
            #     raise_amount = int(my_pip + continue_cost + 0.4 * (pot_total + continue_cost))
            
            if (strength < 0.4 and (not self.is_big_blind or continue_cost > 3)):
                if random.random() < self.bluff_probability:
                    self.bluffing = True
                    strength = 0.7
                else:
                    return FoldAction()
            raise_amount = int(my_pip + continue_cost + (strength * 0.8 - 0.1) * (pot_total + continue_cost))

            # opp_continue_cost = raise_amount - continue_cost - my_pip
            
            # opp_pot_odds = opp_continue_cost / (pot_total + raise_amount - my_pip + opp_continue_cost)
            
            # perc_hands_less_than_pot_odds = sum([6 if k[2] == 'o' and k[0] == k[1] else 12 if k[2] == 'o' else 4 for k, v in self.strengths.items() if v < opp_pot_odds]) / 1326
            # print(opp_pot_odds, perc_hands_less_than_pot_odds)
            
            # perc_fold = self.preflop_num_folds / self.round_num
            # print(perc_fold)
            # if self.round_num > 200 and perc_fold < 0.2:
            #     print(1)
            #     exploit_excess_folding = perc_fold / 3

        else:
            if self.bluffing:
                if strength < 0.6:
                    strength = 0.7
                else:
                    print("got better")
            raise_amount = int(my_pip + continue_cost + strength * (pot_total + continue_cost))


        
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


        if continue_cost > 0: 
            # self.average_continue_cost = (self.average_continue_cost * self.continue_cost_count + continue_cost) / (self.continue_cost_count + 1)
            # self.continue_cost_count += 1

            _SCARY = 0
            if continue_cost > 5:
                _SCARY = 0.1
            if continue_cost > 10: 
                _SCARY = .2
            if continue_cost > 20:
                _SCARY = 0.35
                
            # print(self.average_continue_cost, continue_cost)

            strength = max(0, strength - _SCARY)
            pot_odds = continue_cost/(pot_total + continue_cost)

            if strength >= pot_odds: # nonnegative EV decision
                if strength > 0.5 and random.random() < strength + exploit_excess_folding: 
                    my_action = temp_action
                else: 
                    my_action = CallAction()
            
            else: #negative EV
                bluff_probability = -0.2
                if random.random() < bluff_probability:
                    my_action = temp_action
                else:
                    my_action = FoldAction()
                
                
        else: # continue cost is 0  
            if random.random() < strength: 
                my_action = temp_action
            else: 
                my_action = CheckAction()
            

        return my_action


if __name__ == '__main__':
    run_bot(Player(), parse_args())
