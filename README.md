# BlackJack_Eval

On the screen it shows the values and number of visits corresponding to the current state of the game. Note that the learning is happening in the background and it is not related to the state that you see in the screen. When you manually play with the buttons, you are just manually sampling various states of the game and can see how their current values are (they keep changing when you are running the learning algorithms). 


Keyboard operations
------
The following keyboard options are available:
- 'h': hit
- 's': stand
- 'd': double
- 'q': toggle Q-learning
- 'a': toggle autoplay
- '1': save the AI state (not the game state)
- '2': load from saved AI state

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
1. If player and dealer has the same sum values, the player DRAWS
2. If player busts, player LOSES
3. If dealer busts, player WINS
4. If neither busts, the player WINS if player has a sum bigger than dealer.

### Custom rules: