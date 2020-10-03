import pygame
from pygame.locals import *
import sys, copy, random, argparse, os

from game import Game, cards, HIT, STAND, DOUBLE, SPLIT, WIN_STATE, LOSE_STATE, DRAW_STATE, BLACKJACK_STATE
from ai import Agent

from test import *

# -- Configurations --
AI_FILE = "saved"
LOAD = True                  # Load saved AI knowedge from file
FAST_LEARN = True           # Do Q-Learning and store to file
LEARN_ITERATIONS = 50000000  # Number of Q-Learning iterations
FAST_SIM = True              # Simulate games
SIM_ITERATIONS = 1000000    # Number of simulations to run
GAMES_PER_STAT_TRACK = 200
# -- Configurations --

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,139)
GREEN = (0x44,0xff,0x44)
RED = (0xff, 0x44, 0x44)

PADDING = 5

GAME_OVER_TEXT_POS = (240, 20)

OPS_BTN_Y = 430
OPS_TXT_Y = OPS_BTN_Y + 3

OPS_INSTR_X = 10
OPS_INSTR_Y = 460

OPS_BTN_HEIGHT = 23

USR_CARD_HEIGHT = 275

class GameRunner:
    def __init__(self):
        self.game = Game()
        self.agent = Agent()
        self.parallel_games = []

        if LOAD:
            print("Loading..")
            self.agent.load(AI_FILE)
        
        if FAST_LEARN:
            print(f"Learning {LEARN_ITERATIONS} times..")
            self.agent.Q_run(LEARN_ITERATIONS)
            self.agent.save(AI_FILE)

        self.autoQL = False
        self.autoPlay = False

        self.action = HIT

        card_path = 'resources/cards/'
        self.card_imgs = {}
        for (rank, suit) in cards:
            self.card_imgs[(rank, suit)] = pygame.image.load(os.path.join(card_path, f"{rank}_{suit}.png"))
        self.cBack = pygame.image.load('resources/cardback.png')

        self.init_display()
        self.render_board()
        

    def init_display(self):
        #Initialize Game
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Blackjack')
        self.font = pygame.font.SysFont("arial", 15)
        
        self.hitTxt = self.font.render('[H]it', 1, BLACK)
        self.standTxt = self.font.render('[S]tand', 1, BLACK)
        self.doubleTxt = self.font.render('[D]ouble', 1, BLACK)
        self.splitTxt = self.font.render('Spli[t]', 1, BLACK)
        self.splitHandTxt = self.font.render('Split: 0', 1, BLACK)

        modes = ["off", "on"]
        self.QLTxt = [self.font.render('[Q]L - ' + mode, 1, BLUE) for mode in modes]
        self.playTxt = [self.font.render('[A]uto Play - ' + mode, 1, BLUE) for mode in modes]
        self.gameoverTxt = [self.font.render('End of Round. You WON!', 1, RED), self.font.render('End of Round. You LOST!', 1, RED), self.font.render('End of Round. BLACKJACK!', 1, RED), self.font.render('End of Round. DRAW!', 1, RED)]

        self.ops_instr = self.font.render('Click on the button or type the initial character of the operation to play or toggle modes', 1, BLACK)
        self.save_instr = self.font.render('Press 1 to save AI state', 1, BLACK)
        self.load_instr = self.font.render('Press 2 to load from AI\'s saved state', 1, BLACK)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0xa0, 0xa0, 0xa0))
        self.hitB = pygame.draw.rect(self.background, WHITE, (10, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.standB = pygame.draw.rect(self.background, WHITE, (95, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.doubleB = pygame.draw.rect(self.background, WHITE, (180, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.splitB = pygame.draw.rect(self.background, WHITE, (265, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))


    def loop(self):
        if FAST_SIM:
            print("Simulating...")
            i = 0
            last_checked_profit = 0
            results_100_games_file = open("results.txt", "w")

            while i < SIM_ITERATIONS:
                if self.game.game_over() or self.game.stand:
                        self.game.update_stats()
                        self.game.reset()
                        i += 1
                        if i % (SIM_ITERATIONS / 10) == 0:
                            print("[ ", i * 100 / SIM_ITERATIONS, "%]")
                        if self.game.gameNum % GAMES_PER_STAT_TRACK == 0 and self.game.gameNum != 0:
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
            display_changed = False

            # Our state information does not take into account of number of cards
            if self.autoQL:
                #Q-Learning
                #For each state, compute the Q value of the action "Hit" and "Stand"
                self.agent.Q_run(5)
            
            if self.autoPlay:
                if self.game.game_over():
                    display_changed = True
                    self.game.update_stats()
                    if len(self.parallel_games) != 0:
                        self.parallel_games[0].sync(self.game)
                        self.game = self.parallel_games[0]
                        self.parallel_games.pop(0)
                    else:
                        self.game.reset()

                else:
                    # if self.game.dealCards[0][0] == "ace" or self.game.dealCards[1][0] == "ace":
                    #     self.autoPlay = False
                    #     continue
                    decision = self.agent.autoplay_decision(copy.deepcopy(self.game.state), self.game.can_double(), self.game.can_split())
                    if decision == HIT:
                        self.game.act_hit()
                    elif decision == STAND:
                        self.game.act_stand()
                    elif decision == DOUBLE:
                        self.game.act_double()
                    elif decision == SPLIT:
                        self.split_games()
                
            self.handle_user_action()
            self.render_board()
    
    def split_games(self):
        self.game.act_split()
        self.parallel_games.append(copy.deepcopy(self.game))
        self.game.act_hit()
        self.parallel_games[len(self.parallel_games)-1].act_hit()
        if self.game.userCards[0][0] == "ace":
            self.game.act_stand()
            self.parallel_games[len(self.parallel_games)-1].act_stand()
            
    def check_act_QL(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.QLB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_q
        return clicked or pressed
    
    def check_act_autoplay(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.playB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_a
        return clicked or pressed

    def check_act_hit(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.hitB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_h

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_stand(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.standB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_s

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_double(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.doubleB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_d

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_act_split(self, event):
        clicked = event.type == MOUSEBUTTONDOWN and self.splitB.collidepoint(pygame.mouse.get_pos())
        pressed = event.type == KEYDOWN and event.key == K_t

        return not self.game.game_over() and not self.autoPlay and (clicked or pressed)

    def check_reset(self, event):
        clicked = event.type == MOUSEBUTTONDOWN
        pressed = event.type == KEYDOWN

        return self.game.game_over() and not self.autoPlay and (clicked or pressed)
    
    def handle_user_action(self):
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
                
            elif self.check_act_stand(event):
                self.game.act_stand()

            elif self.check_act_double(event):
                if self.game.can_double():
                    self.game.act_double()

            elif self.check_act_split(event):
                if self.game.can_split():
                    self.split_games()

            elif self.check_reset(event):
                self.game.update_stats()
                if len(self.parallel_games) != 0:
                    last_index = len(self.parallel_games) - 1
                    self.parallel_games[last_index].sync(self.game)
                    self.game = self.parallel_games[last_index]
                    self.parallel_games.pop()
                else:
                    self.game.reset()
            
            if event.type == KEYDOWN:
                if event.key == K_x:
                    pygame.quit()
                    sys.exit()
                if event.key == K_1:
                    self.agent.save("saved")
                elif event.key == K_2:
                    self.agent.load("saved")
                if event.key == K_p:
                    self.game.print_counts()
                if event.key == K_v:
                    self.agent.print_decision_value()
    
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
        winTxt = self.font.render('Wins: {}'.format(self.game.winNum), 1, WHITE)
        loseTxt = self.font.render('Losses: {}'.format(self.game.loseNum), 1, WHITE)
        drawTxt = self.font.render('Draws: {}'.format(self.game.drawNum), 1, WHITE)
        blackjackTxt = self.font.render('BlackJacks: {}'.format(self.game.blackjackNum), 1, WHITE)
        profitTxt = self.font.render('Profit: {}'.format(self.game.profit), 1, WHITE)
        amountTxt = self.font.render('Amount played: {}'.format(self.game.amountPlayed), 1, WHITE)
        maxLossTxt = self.font.render('Max loss: {}'.format(self.game.maxLoss), 1, WHITE)
        maxWinTxt = self.font.render('Max win: {}'.format(self.game.maxProfit), 1, WHITE)

        if self.game.gameNum == 0:
            win_rate = 0
            draw_rate = 0
            lose_rate = 0
            blackjack_rate = 0
        else:
            blackjack_rate = self.game.blackjackNum / self.game.gameNum
            win_rate = self.game.winNum / self.game.gameNum
            draw_rate = self.game.drawNum / self.game.gameNum
            lose_rate = self.game.loseNum / self.game.gameNum
        blackjack_rate_txt = self.font.render('Blackjack rate: {:.2f}%'.format(blackjack_rate * 100), 1, WHITE)
        win_rate_txt = self.font.render('Win rate: {:.2f}%'.format(win_rate * 100), 1, WHITE)
        draw_rate_txt = self.font.render('Draw rate: {:.2f}%'.format(draw_rate * 100), 1, WHITE)
        lose_rate_txt = self.font.render('Loss rate: {:.2f}%'.format(lose_rate * 100), 1, WHITE)
            
        button_colors = [RED, GREEN]
        self.QLB = pygame.draw.rect(self.background, button_colors[self.autoQL], (350, OPS_BTN_Y, 75, OPS_BTN_HEIGHT))
        self.playB = pygame.draw.rect(self.background, button_colors[self.autoPlay], (435, OPS_BTN_Y, 115, OPS_BTN_HEIGHT))


        state_info = self.font.render('State (user_sum, user_has_Ace, dealer_first) ={}'.format(self.game.state), 1, BLACK)

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
        self.screen.blit(self.hitTxt, (37, OPS_TXT_Y))
        self.screen.blit(self.standTxt, (113, OPS_TXT_Y))
        self.screen.blit(self.doubleTxt, (190, OPS_TXT_Y))
        self.screen.blit(self.splitTxt, (270, OPS_TXT_Y))
        self.screen.blit(self.QLTxt[self.autoQL], (359, OPS_TXT_Y))
        self.screen.blit(self.playTxt[self.autoPlay], (444, OPS_TXT_Y))
        self.screen.blit(self.ops_instr, (OPS_INSTR_X, OPS_INSTR_Y))

        for width, color in [(0, WHITE), (2, BLACK)]:
            pygame.draw.rect(self.screen, color,
                (10, 170, 600, 95), width)
        self.screen.blit(state_info, (20, 180))
        self.screen.blit(QV, (20, 220))
        self.screen.blit(STRATEGY, (20, 240))

        self.screen.blit(self.splitHandTxt, (350, 300))
        self.screen.blit(winTxt, (500, 10))
        self.screen.blit(blackjackTxt, (500, 30))
        self.screen.blit(drawTxt, (500, 50))
        self.screen.blit(loseTxt, (500, 70))
        self.screen.blit(profitTxt, (500, 90))
        self.screen.blit(amountTxt, (500, 110))
        self.screen.blit(maxLossTxt, (500, 130))
        self.screen.blit(maxWinTxt, (500, 150))
        self.screen.blit(blackjack_rate_txt, (350, 40))
        self.screen.blit(win_rate_txt, (350, 65))
        self.screen.blit(draw_rate_txt, (350, 90))
        self.screen.blit(lose_rate_txt, (350, 115))

        self.screen.blit(self.save_instr, (350, 380))
        self.screen.blit(self.load_instr, (350, 400))

        for i, card in enumerate(self.game.userCards):
            x = 10 + i * 20
            self.screen.blit(self.card_imgs[card], (x, USR_CARD_HEIGHT))
        
        if self.game.game_over() or self.game.stand:
            if self.game.state == WIN_STATE:
                result_txt = self.gameoverTxt[0]
            elif self.game.state == BLACKJACK_STATE:
                result_txt = self.gameoverTxt[2]
            elif self.game.state == DRAW_STATE:
                result_txt = self.gameoverTxt[3]
            else:
                result_txt = self.gameoverTxt[1]
            self.draw_label_hl(self.screen, GAME_OVER_TEXT_POS, result_txt)
            self.screen.blit(result_txt, GAME_OVER_TEXT_POS)
            for i, card in enumerate(self.game.dealCards):
                x = 10 + i * 20
                self.screen.blit(self.card_imgs[card], (x, 10))
        else:
            self.screen.blit(self.card_imgs[self.game.dealCards[0]], (10, 10))
            self.screen.blit(self.cBack, (30, 10))

        pygame.display.update()


ROTATIONS = {pygame.K_UP: 0, pygame.K_DOWN: 2, pygame.K_LEFT: 1, pygame.K_RIGHT: 3}
game = GameRunner()
game.loop()