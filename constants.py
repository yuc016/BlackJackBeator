#### Configurable constants ####

## Display ##
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,139)
GREEN = (0x44,0xff,0x44)
RED = (0xff, 0x44, 0x44)
PADDING = 5
WINDOW_SIZE = (800, 600)
GAME_OVER_TEXT_POS = (150, 300)
OPS_BTN_Y = 430
OPS_TXT_Y = OPS_BTN_Y + 3
OPS_INSTR_X = 10
OPS_INSTR_Y = 460
OPS_BTN_HEIGHT = 23
USR_CARD_HEIGHT = 275

## Program behavior ##
AI_FILE = "saved"
LOAD_AI = True             # Load saved AI knowedge from file
FAST_LEARN = True           # Do Q-Learning and store to file
LEARN_ITERATIONS = 100    # Number of Q-Learning iterations
FAST_SIM = True             # Simulate games
SIM_ITERATIONS = 1000      # Number of simulations to run

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
STATE_DRAW = (1,0,1)
STATE_BLACKJACK = (1,1,1)

STATES = [STATE_WIN, STATE_LOSE, STATE_DRAW, STATE_BLACKJACK]

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
