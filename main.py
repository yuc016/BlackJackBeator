import pygame
from pygame.locals import *
import sys, copy, random, argparse, os

from constants import *
from game import Game
from ai import Agent
from constants import *

class GameRunner:
    def __init__(self):
        self.game = Game()
        self.agent = Agent(SMART_BET)
        self.splitted_games = []

        if LOAD_AI:
            print("Loading AI knowledge..")
            self.agent.load(AI_FILE)
        
        if FAST_LEARN:
            print(f"Learning {LEARN_ITERATIONS} times..")
            self.agent.Q_run(LEARN_ITERATIONS, True)

        self.autoQL = False
        self.autoPlay = False
        self.action = HIT
        self.split_hand = 0

        card_path = 'resources/cards/'
        self.card_imgs = {}
        for rank in RANKS:
            for suit in SUITS:
                self.card_imgs[(rank, suit)] = pygame.image.load(os.path.join(card_path, f"{rank}_{suit}.png"))
        self.card_back_img = pygame.image.load('resources/cardback.png')

        self.init_display()
        self.render_board()


    def init_display(self):
        #Initialize Game
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption('Blackjack')
        self.font = pygame.font.SysFont("arial", 15)
        
        self.hit_txt = self.font.render('[H]it', 1, BLACK)
        self.stand_txt = self.font.render('[S]tand', 1, BLACK)
        self.double_txt = self.font.render('[D]ouble', 1, BLACK)
        self.split_txt = self.font.render('Spli[t]', 1, BLACK)
        self.split_hand_txt = self.font.render('Split: ' + str(self.split_hand), 1, BLACK)

        modes = ["OFF", "ON"]
        self.QL_txt = [self.font.render('[Q]L - ' + mode, 1, BLUE) for mode in modes]
        self.autoplay_txt = [self.font.render('[A]uto Play - ' + mode, 1, BLUE) for mode in modes]
        self.gameover_txt = [self.font.render('You WON!', 1, RED), self.font.render('You LOST!', 1, RED), self.font.render('You WON!\nBLACKJACK!', 1, RED), self.font.render('DRAW!', 1, RED)]

        self.ops_instr = self.font.render('Click on the button or press corresponding key to play', 1, BLACK)
        self.save_instr = self.font.render('Press 1 to save AI state', 1, BLACK)
        self.load_instr = self.font.render('Press 2 to load AI state', 1, BLACK)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0xa0, 0xa0, 0xa0))
        self.hit_btn = pygame.draw.rect(self.background, WHITE, (10, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.stand_btn = pygame.draw.rect(self.background, WHITE, (95, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.double_btn = pygame.draw.rect(self.background, WHITE, (180, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.split_btn = pygame.draw.rect(self.background, WHITE, (265, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))


    def loop(self):
        if FAST_SIM:
            print(f"Simulating {SIM_ITERATIONS} times..")
            i = 0
            last_checked_profit = 0
            results_100_games_file = open("results.txt", "w")

            while i < SIM_ITERATIONS:
                if self.game.is_game_over() or self.game.stand:
                    self.game.update_stats()
                    self.next_game()

                    i += 1
                    if i % (SIM_ITERATIONS / 10) == 0:
                        print("[ ", i * 100 / SIM_ITERATIONS, "%]")
                    if self.game.num_games % GAMES_PER_STAT_TRACK == 0 and self.game.num_games != 0:
                        results_100_games_file.write(str(self.game.profit - last_checked_profit))
                        results_100_games_file.write("\n")
                        last_checked_profit = self.game.profit
                else:
                    decision = self.agent.autoplay_decision(self.game.state, self.game.can_double(), self.game.can_split())
                    if decision == HIT:
                        self.game.act_hit()
                    elif decision == STAND:
                        self.game.act_stand()
                    elif decision == DOUBLE:
                        self.game.act_double()
                    elif decision == SPLIT:
                        self.split_games()

            results_100_games_file.close()
            self.render_board()

        while True:
            update_display = False

            # State information does not take into account of number of cards
            if self.autoQL:
                # Q-Learning
                update_display = True
                self.agent.Q_run(5)
            
            if self.autoPlay:
                update_display = True
                if self.game.is_game_over():
                    self.game.update_stats()
                    self.next_game()
                else:
                    decision = self.agent.autoplay_decision(copy.deepcopy(self.game.state), self.game.can_double(), self.game.can_split())
                    if decision == HIT:
                        self.game.act_hit()
                    elif decision == STAND:
                        self.game.act_stand()
                    elif decision == DOUBLE:
                        self.game.act_double()
                    elif decision == SPLIT:
                        self.split_games()
        
            if self.handle_user_action() or update_display:
                self.render_board()
    
    def split_games(self):
        self.split_hand = 1
        self.game.act_split()
        self.splitted_games.append(copy.deepcopy(self.game))
        self.game.act_hit()
        self.splitted_games[-1].act_hit()
        if self.game.player_cards[0][0] == ACE and ACE_SPLIT_DEAL_ONE_CARD:
            self.game.act_stand()
            self.splitted_games[len(self.splitted_games)-1].act_stand()

    def next_game(self):
        # Check if there is a split game
        if len(self.splitted_games) != 0:
            self.next_split_hand()
        else:
            self.split_hand = 0
            self.game.reset_game()
            self.game.bet = self.agent.calculate_bet_amount(self.game.true_count)

    def next_split_hand(self):
        self.split_hand += 1
        self.splitted_games[-1].sync(self.game)
        self.game = self.splitted_games[-1]
        self.splitted_games.pop()

    def check_act_QL(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.QL_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_q
        return clicked or pressed
    
    def check_act_autoplay(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.autoplay_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_a
        return clicked or pressed

    def check_act_hit(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.hit_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_h

        return not self.game.is_game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_stand(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.stand_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_s

        return not self.game.is_game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_double(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.double_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_d

        return not self.game.is_game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_split(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.split_btn.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_t

        return not self.game.is_game_over() and not self.autoPlay and (clicked or pressed)

    def check_reset(self, event):
        clicked = event.type == MOUSEBUTTONDOWN
        pressed = event.type == KEYDOWN

        return self.game.is_game_over() and not self.autoPlay and (clicked or pressed)
    
    # Return whether to change display
    def handle_user_action(self):
        update_display = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif self.check_act_QL(event):
                self.autoQL = not self.autoQL
            elif self.check_act_autoplay(event):
                self.autoPlay = not self.autoPlay
            elif self.check_act_hit(event):
                self.game.act_hit()
                update_display = True
            elif self.check_act_stand(event):
                self.game.act_stand()
                update_display = True
            elif self.check_act_double(event):
                if self.game.can_double():
                    self.game.act_double()
                    update_display = True
            elif self.check_act_split(event):
                if self.game.can_split():
                    self.split_games()
                    update_display = True
            elif self.check_reset(event):
                self.game.update_stats()
                self.next_game()
                update_display = True
            if event.type == KEYDOWN:
                if event.key == K_x:
                    pygame.quit()
                    sys.exit()
                if event.key == K_1:
                    self.agent.save(AI_FILE)
                elif event.key == K_2:
                    self.agent.load(AI_FILE)
                    update_display = True
                if event.key == K_p:
                    self.game.print_counts()
                if event.key == K_v:
                    self.agent.print_decision_value()
            
            return update_display
    
    @staticmethod
    def draw_label_hl(surface, pos, label, padding=PADDING, bg=WHITE, wd=2, border=True):
        specs = [(bg, 0)]
        if border:
            specs += [(BLACK, wd)]
        for color, width in specs:
            x = pos[0] - padding
            y = pos[1] - padding
            w = label.get_width() + padding * 2
            h = label.get_height() + padding * 2
            pygame.draw.rect(surface, color, (x, y, w, h), width)

    def render_board(self):
        curr_true_count_txt = self.font.render('True count: {}'.format(self.game.true_count), 1, WHITE)
        curr_bet_txt = self.font.render('Bet: {}'.format(self.game.bet), 1, WHITE)

        # Game Stats
        if self.game.num_games == 0:
            win_rate = 0
            draw_rate = 0
            lose_rate = 0
            blackjack_rate = 0
        else:
            blackjack_rate = self.game.num_blackjacks / self.game.num_games
            win_rate = self.game.num_wins / self.game.num_games
            draw_rate = self.game.num_draws / self.game.num_games
            lose_rate = self.game.num_losses / self.game.num_games

        num_games_txt = self.font.render('Number of games: {}'.format(self.game.num_games), 1, WHITE)
        blackjack_rate_txt = self.font.render('Blackjack rate: {:.2f}%'.format(blackjack_rate * 100), 1, WHITE)
        win_rate_txt = self.font.render('Win rate: {:.2f}%'.format(win_rate * 100), 1, WHITE)
        draw_rate_txt = self.font.render('Draw rate: {:.2f}%'.format(draw_rate * 100), 1, WHITE)
        lose_rate_txt = self.font.render('Loss rate: {:.2f}%'.format(lose_rate * 100), 1, WHITE)
            
        # Bank Stats
        amount_played_txt = self.font.render('Amount played: {}'.format(self.game.amount_played), 1, WHITE)
        max_profit_txt = self.font.render('Max win: {}'.format(self.game.max_profit), 1, WHITE)
        max_loss_txt = self.font.render('Max loss: {}'.format(self.game.max_loss), 1, WHITE)
        max_loss_streak_txt = self.font.render('Max continuous loss: {}'.format(self.game.max_loss_streak), 1, WHITE)
        max_win_streak_txt = self.font.render('Max continuous win: {}'.format(self.game.max_win_streak), 1, WHITE)
        profit_txt = self.font.render('Profit: {}'.format(self.game.profit), 1, WHITE)

        self.split_hand_txt = self.font.render('Split: ' + str(self.split_hand), 1, BLACK)

        button_colors = [RED, GREEN]
        self.QL_btn = pygame.draw.rect(self.background, button_colors[self.autoQL], (350, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.autoplay_btn = pygame.draw.rect(self.background, button_colors[self.autoPlay], (435, OPS_BTN_Y, 115, OPS_BTN_HEIGHT))


        state_info = self.font.render('State (player_sum, player_has_Ace, dealer_first) ={}'.format(self.game.state), 1, BLACK)

        QV = self.font.render('Current stats\'s Q values ([Hit, Stand], #samples): ([{:f},{:f}], {})'.format(
            self.agent.Q_values[self.game.state][0],
            self.agent.Q_values[self.game.state][1],
            self.agent.N_Q[self.game.state],
        ) , 1, BLACK)

        d = self.agent.autoplay_decision(self.game.state, self.game.can_double(), self.game.can_split())
        
        if d == HIT:
            self.action = "HIT"
        elif d == STAND:
            self.action = "STAND"
        elif d == DOUBLE:
            self.action = "DOUBLE"
        elif d == SPLIT:
            self.action = "SPLIT"
        

        STRATEGY = self.font.render('Recommended action: {}'.format(
            self.action,
        ) , 1, BLACK)
        
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.hit_txt, (37, OPS_TXT_Y))
        self.screen.blit(self.stand_txt, (113, OPS_TXT_Y))
        self.screen.blit(self.double_txt, (190, OPS_TXT_Y))
        self.screen.blit(self.split_txt, (270, OPS_TXT_Y))
        self.screen.blit(self.QL_txt[self.autoQL], (359, OPS_TXT_Y))
        self.screen.blit(self.autoplay_txt[self.autoPlay], (444, OPS_TXT_Y))
        self.screen.blit(self.ops_instr, (OPS_INSTR_X, OPS_INSTR_Y))

        for width, color in [(0, WHITE), (2, BLACK)]:
            pygame.draw.rect(self.screen, color,
                (10, 170, 600, 95), width)
        self.screen.blit(state_info, (20, 180))
        self.screen.blit(QV, (20, 220))
        self.screen.blit(STRATEGY, (20, 240))

        self.screen.blit(curr_bet_txt, (200, 10))
        self.screen.blit(curr_true_count_txt, (200, 30))

        self.screen.blit(num_games_txt, (350, 10))
        self.screen.blit(blackjack_rate_txt, (350, 30))
        self.screen.blit(win_rate_txt, (350, 50))
        self.screen.blit(draw_rate_txt, (350, 70))
        self.screen.blit(lose_rate_txt, (350, 90))

        self.screen.blit(amount_played_txt, (500, 10))
        self.screen.blit(max_profit_txt, (500, 30))
        self.screen.blit(max_loss_txt, (500, 50))
        self.screen.blit(max_loss_streak_txt, (500, 70))
        self.screen.blit(max_win_streak_txt, (500, 90))
        self.screen.blit(profit_txt, (500, 110))

        self.screen.blit(self.split_hand_txt, (350, 300))
        self.screen.blit(self.save_instr, (350, 380))
        self.screen.blit(self.load_instr, (350, 400))

        for i, card in enumerate(self.game.player_cards):
            x = 10 + i * 20
            self.screen.blit(self.card_imgs[card], (x, USR_CARD_HEIGHT))
        
        if self.game.is_game_over() or self.game.stand:
            if self.game.state == STATE_WIN:
                result_txt = self.gameover_txt[0]
            elif self.game.state == STATE_BLACKJACK:
                result_txt = self.gameover_txt[2]
            elif self.game.state == STATE_DRAW:
                result_txt = self.gameover_txt[3]
            else:
                result_txt = self.gameover_txt[1]
            self.draw_label_hl(self.screen, GAME_OVER_TEXT_POS, result_txt)
            self.screen.blit(result_txt, GAME_OVER_TEXT_POS)
            for i, card in enumerate(self.game.dealer_cards):
                x = 10 + i * 20
                self.screen.blit(self.card_imgs[card], (x, 10))
        else:
            self.screen.blit(self.card_imgs[self.game.dealer_cards[0]], (10, 10))
            self.screen.blit(self.card_back_img, (30, 10))

        pygame.display.update()


ROTATIONS = {pygame.K_UP: 0, pygame.K_DOWN: 2, pygame.K_LEFT: 1, pygame.K_RIGHT: 3}
game = GameRunner()
game.loop()