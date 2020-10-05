# BlackJack_Eval

Keyboard operations
------
The following keyboard options are available:
- 'h': hit
- 's': stand
- 'd': double
- 't': split
- 'q': toggle Q-learning (do in background)
- 'p': print remaining card counts to stdout in a comma seperated list
- 'a': toggle autoplay
- '1': save the AI knowledge about game states
- '2': load from file the saved AI knowledge about game states

Rules of Blackjack
-----

### Game’s procedure: 
1. The player and dealer are both given two cards, with one of the dealer’s card revealed to the player. 
2. The player can keep asking for new cards (hit) before going bust (player will lose). 
3. When the player stops taking cards (stand), the dealer takes over until termination. 

### Player’s actions: 
1. Hit: player takes a card from card deck
2. Stand: player stops taking cards, and dealer starts playing with its policy (see below)
3. Double: player doubles down on bet, but must stand after taking next card
4. Split: player splits one game of two cards with same rank into two games and two bets, then plays      
    seperately, (this project allows double after split)

**Goal of the player**: Get a bigger sum than the dealer’s sum, without going over 21 (bust). 

### Cards’ values:
- Ace counts as either 1 or 11 based on need. 
- Jack, Queen and King counts as 10. 
- Other cards count as their numerical values.

### Dealer’s policy:
1. If dealer has an Ace, it will count as 11 unless it makes dealer busts
2. Dealer always hits until the sum gets > 17 and <= 21 with Ace counted as 11 (if there is an Ace),
   or >= 17 without Ace counted as 11 (or without an Ace), where dealer will then stand. 
   (Note: This is often referred to as hit on soft-17 policy and will give the dealer more advantage than a 
   stand on soft-17 policy. This can be adjusted in game.py.)

### Game results:
1. If player has Blackjack, player WINS if dealer does not have a blackjack, otherwise player DRAWS
2. If player busts, player LOSES
3. If dealer busts, player WINS
4. If player and dealer has the same sum values, the player DRAWS
5. If neither busts, player WINS if player has a higher hand