import copy
import random
from constants import *

class Game:
    def __init__(self):
        self.num_games = 0
        self.num_wins = 0
        self.num_losses = 0
        self.num_pushes = 0
        self.num_blackjacks = 0

        self.amount_played = 0
        self.profit = 0
        self.max_profit = 0
        self.max_loss = 0
        self.max_lose_streak = 0
        self.curr_lose_streak = 0
        self.max_win_streak = 0
        self.curr_win_streak = 0

        self.bet = 0
        self.playing_cards = []
        self.card_counts = [0] * 10
        self.true_count = 0

        self.doubledown = False
        self.stand = False

        self.player_sum = 0
        self.player_cards = []
        self.dealer_sum = 0
        self.dealer_cards = []
        self.player_has_ace = False
        self.dealer_has_ace = False
        self.dealer_upcard_value = 0

        self.state = None
        self.reset_game()

    def reset_game(self):
        self.player_cards = []
        self.dealer_cards = []
        self.stand = False
        self.doubledown = False
        self.bet = DEFAULT_BET
        self.init_cards()

    def init_cards(self):
        if not self.cards_sufficient():
            self.get_new_decks()

        self.player_has_ace = False
        self.dealer_has_ace = False

        card_1, is_ace = self.deal_card(self.player_cards)
        self.player_has_ace = is_ace or self.player_has_ace

        card_2, is_ace = self.deal_card(self.dealer_cards)
        self.dealer_has_ace = is_ace or self.dealer_has_ace

        card_3, is_ace = self.deal_card(self.player_cards)
        self.player_has_ace = is_ace or self.player_has_ace

        card_4, is_ace = self.deal_card(self.dealer_cards)
        self.dealer_has_ace = is_ace or self.dealer_has_ace

        self.player_sum = self.get_card_value(card_1) + self.get_card_value(card_3)
        self.dealer_sum = self.get_card_value(card_2) + self.get_card_value(card_4)
        self.dealer_upcard_value = self.get_card_value(card_2)

        self.state = self.make_state()

    def cards_sufficient(self):
        # One 6th of trailing cards will not be played
        return len(self.playing_cards) > NUM_DECK * 52 // 6

    def get_card_value(self, card):
        rank, _ = card
        if rank == ACE:
            return 1
        elif rank in [JACK, Queen, KING]:
            return 10
        return int(rank)
    
    def calculate_hand(self, cards_sum, has_ace):
        A_active = False
        if has_ace > 0 and cards_sum + 10 <= 21:
            A_active = True
        actual_sum = cards_sum + A_active * 10
        return actual_sum
    
    # Generate new decks of playing cards
    def get_new_decks(self):
        self.playing_cards = []
        for rank in RANKS:
            for suit in SUITS:
                for n in range(NUM_DECK):
                    self.playing_cards.append((rank, suit))
        
        for i in range(9):
            self.card_counts[i] = 4 * NUM_DECK  # 4 cards for per deck per rank
        self.card_counts[9] = 16 * NUM_DECK     # 16 cards for 10's value
        self.true_count = 0

    def deal_card(self, cards_list):
        card = random.choice(self.playing_cards)
        self.playing_cards.remove(card)
        self.update_card_count(card)
        cards_list.append(card)

        is_ace = False
        if card[0] == ACE:
            is_ace = True

        return card, is_ace

    def update_card_count(self, card_removed):
        card_value = self.get_card_value(card_removed)
        self.card_counts[card_value - 1] -= 1
        
        if card_value >= BIG_CARD_VALUE or card_removed[0] == ACE:
            self.true_count -= 1
        elif card_value <= SMALL_CARD_VALUE:
            self.true_count += 1
    
    def is_game_over(self):
        return self.stand or self.state == STATE_WIN or self.state == STATE_LOSE or self.state == STATE_PUSH or self.state == STATE_BLACKJACK

    def make_state(self):
        # Calculate actual hands after counting A as 11 as needed
        actual_player_sum = self.calculate_hand(self.player_sum, self.player_has_ace)
        actual_dealer_sum = self.calculate_hand(self.dealer_sum, self.dealer_has_ace)

        dealer_bj = len(self.dealer_cards) == 2 and actual_dealer_sum == 21
        player_bj = len(self.player_cards) == 2 and actual_player_sum == 21

        # Dealer blackjack
        if dealer_bj:
            if player_bj:
                return STATE_PUSH
            else:
                return STATE_LOSE
        
        # Player blackjack
        if player_bj:
            return STATE_BLACKJACK

        # if actual_player_sum == 21:
        #     # Call a stand for player to allow dealer play, and don't make state again
        #     self.act_stand(False)

        #     # Recalculate dealer sum after dealer played
        #     actual_dealer_sum = self.calculate_hand(self.dealer_sum, self.dealer_has_ace)

        #     if actual_dealer_sum != 21:
        #         return STATE_WIN
        #     else:
        #         # DEBUG
        #         # print(self.dealer_cards)
        #         # print(self.player_cards)
        #         # print(self.doubledown)
        #         # print()
        #         return STATE_PUSH
        
        # Player busts
        if actual_player_sum > 21:
            return STATE_LOSE
        
        # Player stands
        if self.stand:
            if actual_dealer_sum > 21 or actual_player_sum > actual_dealer_sum:
                return STATE_WIN
            elif actual_dealer_sum == actual_player_sum:
                return STATE_PUSH
            return STATE_LOSE

        # Game not over

        if USE_SIMPLE_STATES:
            return (self.player_sum, self.player_has_ace, self.dealer_upcard_value)

        card_value_available = [0] * 10
        for i in range(10):
            if self.card_counts[i] > 0:
                card_value_available[i] = 1
        return (self.player_sum, self.player_has_ace, self.dealer_upcard_value, *card_value_available)
        
    def act_hit(self):
        # Give player a card
        card, is_ace = self.deal_card(self.player_cards)
        self.player_has_ace = is_ace or self.player_has_ace
        self.player_sum += self.get_card_value(card)
        
        # Make state based on the updated player cards
        self.state = self.make_state()

    def act_stand(self, make_state=True):
        while True:
            actual_dealer_sum = self.calculate_hand(self.dealer_sum, self.dealer_has_ace)

            if actual_dealer_sum >= 17:
                # Break unless dealer gets a soft 17 and follows hit on soft 17 policy 
                if not (HIT_SOFT_17 and actual_dealer_sum == 17 and actual_dealer_sum != self.dealer_sum):
                    break
            card, is_ace = self.deal_card(self.dealer_cards)
            self.dealer_has_ace = is_ace or self.dealer_has_ace
            self.dealer_sum += self.get_card_value(card)
    
        # Make state based on the updated cards
        self.stand = True
        if make_state:
            self.state = self.make_state()

    def act_double(self):
        if self.can_double():
            self.bet *= 2
            self.doubledown = True
            self.act_hit()
            if not self.is_game_over():
                self.act_stand()

    def act_split(self):
        if self.can_split():
            self.player_sum = self.get_card_value(self.player_cards[0])
            self.player_cards.pop()
            self.state = self.make_state()

    def can_double(self):
        return ALLOW_DOUBLE and not self.doubledown and (not DOUBLE_WITH_2_CARDS_ONLY or len(self.player_cards) == 2)
    
    def can_split(self):
        return ALLOW_SPLIT and len(self.player_cards) == 2 and self.player_cards[0][0] == self.player_cards[1][0]
    
    def check_reward(self):
        if not self.is_game_over():
            return 0
        if self.state == STATE_BLACKJACK:
            return BLACKJACK_PAYRATE
        if self.state == STATE_WIN:
            return 1
        if self.state == STATE_PUSH:
            return 0
        return -1

    def update_stats(self):
        self.num_games += 1
        self.amount_played += self.bet

        profit_delta = 0
        if self.state == STATE_WIN:
            self.num_wins += 1
            profit_delta = self.bet
        elif self.state == STATE_BLACKJACK:
            self.num_blackjacks += 1
            profit_delta = BLACKJACK_PAYRATE * self.bet
        elif self.state == STATE_PUSH:
            self.num_pushes += 1
        elif self.state == STATE_LOSE:
            self.num_losses += 1
            profit_delta = -self.bet

        self.profit += profit_delta
        
        if self.profit > self.max_profit:
            self.max_profit = self.profit
        if self.profit < self.max_loss:
            self.max_loss = self.profit
        
        self.curr_lose_streak = min(self.curr_lose_streak + profit_delta, 0)
        if self.curr_lose_streak < self.max_lose_streak:
            self.max_lose_streak = self.curr_lose_streak

        self.curr_win_streak = max(self.curr_win_streak + profit_delta, 0)
        if self.curr_win_streak > self.max_win_streak:
            self.max_win_streak = self.curr_win_streak
    
    def simulate_one_step(self, action):
        # If the current state is already terminal, return None
        if self.is_game_over():
            return None, self.check_reward()
        
        # Perform action based on the parameter
        if action == HIT:
            self.act_hit()
        elif action == STAND:
            self.act_stand()

        return self.state, self.check_reward()

    def print_counts(self):
        print(self.card_counts)
        print(self.true_count)

    def sync(self, game):
        self.num_losses = game.num_losses
        self.num_pushes = game.num_pushes
        self.num_wins = game.num_wins
        self.num_blackjacks = game.num_blackjacks
        self.num_games = game.num_games
        self.max_loss = game.max_loss
        self.max_profit = game.max_profit
        self.max_lose_streak = game.max_lose_streak
        self.max_win_streak = game.max_win_streak
        self.curr_lose_streak = game.curr_lose_streak
        self.curr_win_streak = game.curr_win_streak
        self.profit = game.profit
        self.amount_played = game.amount_played

        self.playing_cards = game.playing_cards
        self.card_counts = game.card_counts
        self.true_count = game.true_count

        self.dealer_cards = game.dealer_cards
        self.dealer_sum = game.dealer_sum
        self.dealer_has_ace = game.dealer_has_ace
