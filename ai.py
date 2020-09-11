import copy
import random

from game import Game, states, BET, WIN_STATE, LOSE_STATE, DRAW_STATE, BLACKJACK_STATE, SIMPLE_STATE

HIT = 0
STAND = 1
DOUBLE = 2
DISCOUNT = 0.97 #This is the gamma value for all value calculations
FAST_LEARN = False

class Agent:
    def __init__(self):
        # For Q-learning values
        self.Q_values = {}   # Dictionary storing the Q-Learning value of each state and action
        self.N_Q = {}        # Dictionary: Store the number of samples of each state

        self.double_values = {}

        self.hitQ = 0
        self.standQ = 0
        self.doubleQ = 0
        self.hitQ = 0
        self.standQ = 0

        # Initialization of the values
        for s in states:
            self.Q_values[s] = [0,0] # First element is the Q value of "Hit", second element is the Q value of "Stand"
            self.N_Q[s] = 0
            self.double_values[s] = 70

        if SIMPLE_STATE:
            for s in states:
                self.double_values[s] = self.calculate_double_value(s)
        
        # NOTE: see the comment of `init_cards()` method in `game.py` for description of game state       
        self.simulator = Game()

    # NOTE: do not modify
    # This is the policy for MC and TD learning. 
    @staticmethod
    def default_policy(state):
        user_sum = state[0]
        user_A_active = state[1]
        actual_user_sum = user_sum + user_A_active * 10
        if actual_user_sum < 14:
            return 0
        else:
            return 1

    # NOTE: do not modify
    # This is the fixed learning rate for TD and Q learning. 
    @staticmethod
    def alpha(n):
        return 10.0/(9 + n)

    @staticmethod
    def epsilon(n):
        return 10/(9 + n)
    
    def Q_run(self, num_simulation, tester=False):
        # Simulate all possible starting card counts
        # for n in range(2**10):
        #     bits = []
        #     for i in range(10):
        #         bits.append(n >> (9-i) & 0x1)

        #Perform num_simulation rounds of simulations in each cycle of the overall game loop
        for simulation in range(num_simulation):

            # self.simulator.new_decks()
            self.simulator.reset()
            # for i in range(10):
            #     if bits[i] == 0:
            #         self.simulator.remove_rank(i + 1)

            # # Skip if this is not a possible game state
            # if not self.simulator.cards_sufficient():
            #     continue

            # TODO: Remove the following dummy update and implement Q-learning
            # Note: Do not reset the simulator again in the rest of this simulation
            # Hint: You need a loop that takes one step simulation each time, until state is "None" which indicates termination
            state = self.simulator.state
            reward = self.simulator.check_reward()
            while True:
                epsilon = self.epsilon(self.N_Q[state])
                action = self.pick_action(state, epsilon)
                n_state, n_reward = self.simulator.simulate_one_step(action)
                self.N_Q[state] += 1
                if n_state == None:
                    self.Q_values[state][action] += (reward - self.Q_values[state][action]) * self.alpha(self.N_Q[state])
                    break
                else:
                    sample = reward + DISCOUNT * max(self.Q_values[n_state])
                    self.Q_values[state][action] += (sample - self.Q_values[state][action]) * self.alpha(self.N_Q[state])
                reward = n_reward
                state = n_state

            
            if FAST_LEARN and simulation % (num_simulation / 10) == 0:
                print(simulation * 100 / num_simulation, "%")

    def pick_action(self, s, epsilon):
        if random.random() < epsilon:
            # Make random choice (explore)
            return random.randint(0,1)
        else:
            # Make rational choice (exploit)
            if self.Q_values[s][HIT] > self.Q_values[s][STAND]:
                return HIT
            return STAND

    def autoplay_decision(self, state, can_double):
        return self.ai_decision(state, can_double)

    def ai_decision(self, state, can_double):
        self.doubleQ = -100
        if can_double:
            if SIMPLE_STATE:
                self.doubleQ = self.double_values[state]
            else:
                self.doubleQ = self.calculate_double_value(state)
        self.hitQ, self.standQ = self.Q_values[state][HIT], self.Q_values[state][STAND]
        if self.hitQ > self.standQ and self.hitQ > self.doubleQ:
            return HIT
        if self.standQ > self.hitQ and self.standQ > self.doubleQ:
            return STAND
        if self.doubleQ > self.hitQ and self.doubleQ > self.standQ:
            return DOUBLE
        return self.simple_decision(state[0])
    
    def random_decision(self):
        if random.random() < 0.5:
            return HIT
        return STAND
    
    def simple_decision(self, sum):
        if sum < 17:
            return HIT
        return STAND

    def print_decision_value(self):
        print("HIT: ", self.hitQ)
        print("STAND: ", self.standQ)
        print("DOUBLE: ", self.doubleQ)

    # Inaccuacy: Consider 21 a win, but can still be a push
    def calculate_double_value(self, state):
        if state == WIN_STATE or state == LOSE_STATE or state == DRAW_STATE or state == BLACKJACK_STATE:
            return 0

        # If double value for the state is previously calculated and saved
        if self.double_values[state] != 70:
            return self.double_values[state]

        sum = 0
        count = 0

        if SIMPLE_STATE:
            new_state = (state[0] + 1, 1, *(state[2:]))
            if new_state[0] == 21 or (new_state[0] == 11 and new_state[1] == 1):
                sum += BET * 2
            # stand value of the next state
            else:
                sum += self.Q_values[new_state][STAND] * 2

            for i in range(2, 14):
                i = min(10, i)
                new_state = (state[0] + i, *(state[1:]))
                if new_state[0] == 21 or (new_state[0] == 11 and new_state[1] == 1):
                    sum += BET * 2
                elif new_state in states:
                    sum += self.Q_values[new_state][STAND] * 2
                # busted
                else:
                    sum -= BET * 2

            return sum / 13

        # Iterate through each possible next card value
        # Ace
        if state[4] == 1:
            new_state = (state[0] + 1, 1, *(state[2:]))
            # 21 considered win
            if new_state[0] == 21 or (new_state[0] == 11 and new_state[1] == 1):
                sum += BET * 2
            # stand value of the next state
            else:
                sum += self.Q_values[new_state][STAND] * 2
            count += 1
            

        # 2-9
        for i in range(5, len(state) - 1):
            if state[i] == 1:
                new_state = (state[0] + i-3, *(state[1:]))
                if new_state[0] == 21 or (new_state[0] == 11 and new_state[1] == 1):
                    sum += BET * 2
                elif new_state in states:
                    sum += self.Q_values[new_state][STAND] * 2
                # busted
                else:
                    sum -= BET * 2
                count += 1
            
        
        # 10-valued cards
        if state[13] == 1:
            for x in range(4):
                new_state = (state[0] + 10, *(state[1:]))
                if new_state[0] == 21 or (new_state[0] == 11 and new_state[1] == 1):
                    sum += BET * 2
                elif new_state in states:
                    sum += self.Q_values[new_state][STAND] * 2
                else:
                    sum -= BET * 2
                count += 1

        if count == 0:
            return 0

        self.double_values[state] = sum / count
        return self.double_values[state]

    def save(self, filename):
        with open(filename, "w") as file:
            # for table in [self.MC_values, self.TD_values, self.Q_values, self.S_MC, self.N_MC, self.N_TD, self.N_Q]:
            for table in [self.Q_values, self.N_Q]:
                for key in table:
                    key_str = str(key).replace(" ", "")
                    entry_str = str(table[key]).replace(" ", "")
                    file.write(f"{key_str} {entry_str}\n")
                file.write("\n")

        # with open(filename, "w") as file:
        #     # file.write("[State] [Hit value, Stand value]\n")
        #     for key in self.Q_values:
        #         key_str = str(key).replace(" ", "")
        #         entry_str = str(self.Q_values[key]).replace(" ", "")
        #         file.write(f"{key_str} {entry_str}\n")
            
        #     file.write("\n")
        #     # file.write("[State] [Number of visit]\n")
        #     for key in self.N_Q:
        #         key_str = str(key).replace(" ", "")
        #         entry_str = str(self.N_Q[key]).replace(" ", "")
        #         file.write(f"{key_str} {entry_str}\n")

    def load(self, filename):
        with open(filename) as file:
            text = file.read()
            Q_values_text, NQ_text, _  = text.split("\n\n")
            
            def extract_key(key_str):
                return tuple([int(x) for x in key_str[1:-1].split(",")])
            
            for table, text in zip(
                [self.Q_values, self.N_Q], 
                [Q_values_text, NQ_text]
            ):
                for line in text.split("\n"):
                    key_str, entry_str = line.split(" ")
                    key = extract_key(key_str)
                    table[key] = eval(entry_str)
     
        if SIMPLE_STATE:
            for s in states:
                self.double_values[s] = 70
                self.double_values[s] = self.calculate_double_value(s)

    @staticmethod
    def tester_print(i, n, name):
        print(f"\r  {name} {i + 1}/{n}", end="")
        if i == n - 1:
            print()