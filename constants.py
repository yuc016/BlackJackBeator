#### Configurable constants ####

## Display ##
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,139)
GREEN = (0x20,0xff,0x20)
RED = (0xff, 0x20, 0x20)

PADDING = 5
WINDOW_SIZE_WIDTH = 1100
WINDOW_SIZE_HEIGHT = 800
WINDOW_SIZE = (WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)
GENERAL_GAP = WINDOW_SIZE_WIDTH // 70
SMALL_GAP = GENERAL_GAP // 2

AI_INFO_BOX_WIDTH = WINDOW_SIZE_WIDTH * 0.6
AI_INFO_BOX_HEIGHT = WINDOW_SIZE_HEIGHT // 6
AI_INFO_BOX_X = WINDOW_SIZE_WIDTH - AI_INFO_BOX_WIDTH - GENERAL_GAP
AI_INFO_BOX_Y = WINDOW_SIZE_HEIGHT // 3
SAVE_INSTR_X = AI_INFO_BOX_X
SAVE_INSTR_Y = AI_INFO_BOX_Y + AI_INFO_BOX_HEIGHT + GENERAL_GAP
LOAD_INSTR_X = SAVE_INSTR_X

OPS_BTN_Y = WINDOW_SIZE_HEIGHT // 4 * 3
OPS_BTN_WIDTH = WINDOW_SIZE_WIDTH // 7
OPS_BTN_HEIGHT = WINDOW_SIZE_HEIGHT // 24
OPS_BTN_GAP = GENERAL_GAP
HIT_BTN_X = OPS_BTN_GAP
STAND_BTN_X = HIT_BTN_X + (OPS_BTN_GAP + OPS_BTN_WIDTH) * 1
DOUBLE_BTN_X = HIT_BTN_X + (OPS_BTN_GAP + OPS_BTN_WIDTH) * 2
SPLIT_BTN_X = HIT_BTN_X + (OPS_BTN_GAP + OPS_BTN_WIDTH) * 3
QL_BTN_X = HIT_BTN_X + (OPS_BTN_GAP + OPS_BTN_WIDTH) * 4
AUTO_PLAY_BTN_X = HIT_BTN_X + (OPS_BTN_GAP + OPS_BTN_WIDTH) * 5
OPS_INSTR_X = OPS_BTN_GAP
OPS_INSTR_Y = OPS_BTN_Y + OPS_BTN_HEIGHT + OPS_BTN_GAP

CARD_WIDTH = WINDOW_SIZE_WIDTH // 8
CARD_HEIGHT = WINDOW_SIZE_HEIGHT // 4
DEALER_CARD_START_X = WINDOW_SIZE_WIDTH // 80
DEALER_CARD_OFFSET = WINDOW_SIZE_WIDTH // 40
DEALER_CARD_Y = WINDOW_SIZE_HEIGHT // 60
PLAYER_CARD_START_X = WINDOW_SIZE_WIDTH // 80
PLAYER_CARD_OFFSET = WINDOW_SIZE_WIDTH // 40
PLAYER_CARD_Y = DEALER_CARD_Y + CARD_HEIGHT + GENERAL_GAP

GAME_OVER_TEXT_X = PLAYER_CARD_START_X
GAME_OVER_TEXT_Y = PLAYER_CARD_Y + CARD_HEIGHT + GENERAL_GAP

## Program behavior ##
AI_FILE = "saved"
LOAD_AI = True             # Load saved AI knowedge from file
FAST_LEARN = False           # Do Q-Learning and store to file
LEARN_ITERATIONS = 10000    # Number of Q-Learning iterations
FAST_SIM = False             # Simulate games
SIM_ITERATIONS = 100000      # Number of simulations to run

## Statistics ## 
GAMES_PER_STAT_TRACK = 200

## AI behavior ##
DEFAULT_BET = 25
SMART_BET = True            # Bet with card counting technique
USE_SIMPLE_STATES = True    # Considers player sum, whether player has ace and dealer upcard
DISCOUNT = 0.9              # For calculating values of future state

## Game rules ##
NUM_DECK = 4                # Number of decks of cards
HIT_SOFT_17 = False         # Whether dealer will hit on soft 17 (sum of 17 with ace counted as 11)
ALLOW_SPLIT = True
ALLOW_DOUBLE = True
DOUBLE_WITH_2_CARDS_ONLY = True
ACE_SPLIT_DEAL_ONE_CARD = True
BLACKJACK_PAYRATE = 1.5


#### Code constants ####

## Action ##
HIT = 0
STAND = 1
DOUBLE = 2
SPLIT = 3

## Cards ##
ACE = "Ace"
JACK = "Jack"
Queen = "Queen"
KING = "King"
RANKS = [
    ACE,
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    JACK,
    Queen,
    KING,
]
SUITS = [
    "Clubs",
    "Spades",
    "Diamonds",
    "Hearts",
]
SMALL_CARD_VALUE = 6
BIG_CARD_VALUE = 10

## Game states ##
STATE_WIN = (0,0,1)
STATE_LOSE = (0,0,0)
STATE_PUSH = (1,0,1)
STATE_BLACKJACK = (11,1,11)

STATES = [STATE_WIN, STATE_LOSE, STATE_PUSH, STATE_BLACKJACK]

# Non-special states (player's sum, player has Ace, dealer's upcard)
for player_sum in range(2,21):
    for player_has_Ace in range(0,2):
        for dealer_upcard in range(1,11):
            if USE_SIMPLE_STATES:
                STATES.append((player_sum, player_has_Ace, dealer_upcard))
            else:
                # For each possible combination of each rank being available
                for n in range(2**10):
                    s = (player_sum, player_has_Ace, dealer_upcard,
                        n >> 9 & 0x1,
                        n >> 8 & 0x1,
                        n >> 7 & 0x1,
                        n >> 6 & 0x1,
                        n >> 5 & 0x1,
                        n >> 4 & 0x1,
                        n >> 3 & 0x1,
                        n >> 2 & 0x1,
                        n >> 1 & 0x1,
                        n & 0x1)
                    STATES.append(s)
