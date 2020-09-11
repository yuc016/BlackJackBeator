Assignment 3: Blackjack
=========
DO NOT FORK THIS REPO
----
Implement Monte Carlo policy evaluation, Temporal Difference policy evaluation, and Q-Learning for Blackjack. The base game engine uses code from [here](https://github.com/ServePeak/Blackjack-Python/blob/master/blackjack.py). 

Authors: Zhizhen Qin, Rishikesh Vaishnav, Sicun Gao

Due date
-----
May-10 5pm. 

The Game
-----
The game more or less follows the standard Blackjack rules. Read the **Blackjack Rules** section below and game engine code to see minor simplification. Again, you do not need to really understand the rules of the game to do the learning right.

The Hit and Stand buttons are for playing the game manually. The MC, TD, and QL bottons start/pause the corresponding learning processes. 

On the screen it shows the values and number of visits corresponding to the current state of the game. Note that the learning is happening in the background and it is not related to the state that you see in the screen. When you manually play with the Hit and Stand buttons, you are just manually sampling various states of the game and can see how their current values are (they keep changing when you are running the learning algorithms). 

Right now the MC, TD, and Q learning code is doing dummy updates that you are supposed to replace. But you can see how the numbers relate to the updates. In particular, keep in mind that in each game loop many rounds of simulation and learning are being run (see Line 80-91 in `main.py`), and that is why the numbers grow quickly. After implementing the right methods, you will observe that these values will stablize after a while (i.e. converge). 

The AutoPlay button at the end will automatically play the game with the learned Q values. When you haven't implemented Q learning, its default action is always HIT. Take a look at the winning rate to see how your Q-learning improves the decisions and that is an indicator of whether your Q-learning is correct (when it is working, the winning rate should be around 41%). 

Keyboard operations
------
The following keyboard options are available:
- 'h': hit
- 's': stand
- 'm': toggle MC learning
- 't': toggle TD learning
- 'q': toggle Q-learning
- 'a': toggle autoplay
- '1': save the AI state (not the game state)
- '2': load from saved AI state

Submission
----
You only need to submit the `ai.py` file on Gradescope for grading. 

If you have changed other files, make sure that your implementation works properly with the given `main.py` and `game.py`, and `test.py` which we will use for grading. The grading metrics are the same as previous PAs, (if your code fails the tests in `test.py` it will not get more than the Half grade).

Tasks
-----
Implement the following algorithms. In all of them, the discount factor is 0.95 as given in Line 8 of `ai.py`. When the player wins, give reward +1, and when loses, the reward is -1. (See **Blackjack Rules** below for details).

Check comments in the code for hints. 

- Monte Carlo Policy Evaluation 

Evaluate the policy "Hit (ask for a new card) if sum of cards is below 14, and Stand (switch to dealer) otherwise" using the Monte Carlo method. Namely, learn the values for each state under the policy. 

- Temporal-Difference Policy Evaluation

Evaluate the policy "Hit (ask for a new card) if sum of cards is below 14, and Stand (switch to dealer) otherwise" using the Temporal-Difference method. 

- Q-Learning

Implement the Q-learning algorithm. Use epsilon=0.4 in the epsilon-strategy in your final submission, but you are encouraged to check the behavior difference for various choices of epsilon. After learning, AutoPlay will follow the Q-learning values to make decisions. 

Testing
-----

We provide three testers: `-t 1` for the first 3-step deterministic tests, `-t 2` for 1k-step divergence test, and `-t 3` for 1-million-step convergence test. 

You can also give the options for MC-only (`-a 1`), TD-only (`-a 1`), Q-Learning-only (`-a 1`), and all together (`-a 0` and this is the default). Note that the 3-step deterministic tester (`-t 1`) is not provided for Q-learning. 

Examples:

`python main.py -t 1 -a 1` to run the deterministic tester for MC algorithm. 
`python main.py -t 2 -a 3` to run the divergence tester for Q-Learning algorithm.
`python main.py -t 3` to run the convergence tester for all algorithms.

### 3-Step Deterministic Tests

The agent is trained for only three steps, with three predified different seeds. After each step, the values of states are compared with the reference solution.

Passing this test depends heavily on how `random` is called, and you are advised to follow the comments in `MC_run` and `TD_run` to use this test. But it is possible that your implementation uses the random numbers differently and the result is different from the test values -- do not freak out. These deterministic tests will not be part of grading; they are just to help you with debugging. 

### 100-k-Step Divergence Tests

The agent is loaded with state valued trained to convergence (with 1 million steps), and the states further trained with 1k steps. After this, the new states values are compared with the old state values. If the values become much different, you know something is wrong as the values should not diverge after convergence.

Note: The convergence of MC/TD/Q-learning should not depend on any specific random seed within the given error margin.

### 1-Million-Step Divergence Tester

The agent is trained with 1 million steps, and compared to pre-trained state values (that are also traiend with 1 million steps). In particular, the given data is trained using epsilon=0.4 in the epsilon-greedy strategy for picking actions. If you use a much smaller epsilon it may give different values (think about why that matters). 

Note: The convergence of MC/TD/Q-learning should not depend on any specific random seed within the given error margin.


Rules of Blackjack
-----

**Goal of the player**: Get a bigger sum than the dealer’s sum, without going over 21 (bust). 

### Cards’ values:
- Ace counts as either 1 or 11 based on need. 
- Jack, Queen and King counts as 10. 
- Other cards count as their numerical values.

### Terms:
- Bust: the sum of cards is greater than 21.

### Game’s procedure: 
1. The player and dealer are both given two cards, with one of the dealer’s card revealed to the player. 
2. The player can keep asking for new cards before going bust. 
3. When the player stands, the dealer takes over until termination. 

### Player’s actions: 
1. Hit: player takes a card from card deck
2. Stand: player stops taking cards, and dealer plays with its policy (see below)

### Dealer’s policy:
1. Dealer starts taking cards until the sum get greater than or equal to 17, or greater than or equal to the player’s sum
2. If dealer has A’s in its hand, then the A only counts as 1 when otherwise the dealer bursts. See below for examples
    1. If dealer has {“Ace”, 6}. then the ace counts as 11 and dealer stops taking cards since the sum equals 17.
    2. If dealer has {8, 6, “Ace”}, then the ace counts as 1 (since counting A as 11 would make the dealer burst), and dealer keeps taking cards since the sum equals 15.

### Termination conditions:
1. Player stands
2. Player gets over 21 (bust)
3. Player gets exactly 21

### Game results:
1. If player and dealer has the same sum values, the player LOSES
2. If player busts, player LOSES
3. If dealer busts, player WINS
4. If neither busts, the player WINS if player has a sum bigger than dealer. That means if player and dealer has the same sum value, player LOSES

### Custom rules:
For simplifying the simulation and modeling, the game engine uses rules slightly different than the normal ones. Do not be disturbed by them; your algorithms work regardless of the rules. 

1. Cards are drawn with replacement, so assume that you are playing with infinitely many decks of cards and the drawn cards do not affect the probability of the next cards. 
2. When user has 5 cards without busting, it is NOT considered as WIN in our game engine. 
3. We don’t have DRAW state. If after stand, user and dealer has the same sum values, the player LOSEs.
4. If player gets 21 at the first hand, player WINs if dealer doesn’t have 21; otherwise player LOSEs. 
5. If player gets 21 after a hit, the player automatically stands, meaning dealer starts to play, and check results afterwards.
6. We don’t differentiate between Blackjack (A + 10) and 21, meaning if user and player both has a sum of 21 when the scores are checked, the player is considered as LOSE.


# BlackJack_Eval
