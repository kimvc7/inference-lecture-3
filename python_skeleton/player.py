'''
Simple example pokerbot, written in Python.
'''
import eval7
from numpy.random import geometric
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot


class Player(Bot):
    '''
    A pokerbot.
    '''

    def permute_values(self):
        '''
        Selects a value permutation for the whole game according the prior distribution.
        '''
        orig_perm = list(range(13))[::-1]
        prop_perm = []
        seed = geometric(p=0.25, size=13) - 1
        for s in seed:
            pop_i = len(orig_perm) - 1 - (s % len(orig_perm))
            prop_perm.append(orig_perm.pop(pop_i))
        return prop_perm

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        values = list('23456789TJQKA')
        suits = list('cdhs')
        self.proposal_perms = []
        for j in range(1000):
            # proposal_perm is a list with entries from 0 to 12
            proposal_perm = self.permute_values()
            perm_dict = {}
            for i, v in enumerate(values):
                for s in suits:
                    card = v + s
                    permuted_i = proposal_perm[i]
                    permuted_v = values[permuted_i]
                    permuted_card = eval7.Card(permuted_v + s)
                    perm_dict[card] = permuted_card
            # we've gone through the whole deck
            self.proposal_perms.append(perm_dict)

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
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        board_cards = previous_state.deck[:street]
        if opp_cards != []:  # we have a showdown
            new_perms = []
            for proposal_perm in self.proposal_perms:  # check if valid
                my_perm_cards = [proposal_perm[c] for c in my_cards]
                opp_perm_cards = [proposal_perm[c] for c in opp_cards]
                board_perm_cards = [proposal_perm[c] for c in board_cards]
                my_cards_available = my_perm_cards + board_perm_cards
                opp_cards_available = opp_perm_cards + board_perm_cards
                my_strength = eval7.evaluate(my_cards_available)
                opp_strength = eval7.evaluate(opp_cards_available)
                # consistent with my win
                if my_strength > opp_strength and my_delta > 0:
                   new_perms.append(proposal_perm)
                # consistent with opp win
                if my_strength < opp_strength and my_delta < 0:
                   new_perms.append(proposal_perm)
                # consistent with a tie
                if my_strength == opp_strength and my_delta == 0:
                   new_perms.append(proposal_perm)
            if len(new_perms) >= 10:
                self.proposal_perms = new_perms
        if game_state.round_num == NUM_ROUNDS:
            print(game_state.game_clock)

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
        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
