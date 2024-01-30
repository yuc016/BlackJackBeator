# BlackJackBeator

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
1. The player and dealer are both dealt two cards, with one of the dealer’s card revealed to the player.
2. The player can keep asking for 1 more card (hit) before going bust (values of cards over 21).
3. When the player stops taking cards (stand), the dealer takes over playing by its policy until termination (see below).

### Player’s actions: 
1. Hit: player takes a card from card deck
2. Stand: player stops taking cards, and dealer starts playing
3. Double: player doubles down on bet and takes only 1 more card
4. Split: player splits a game of two same ranked cards into two games and two original bets, then plays seperately. Double is available after split.

**Goal of the player**: Get a bigger valued hand than the dealer without going bust (over 21). 

### Cards’ values:
- Ace counts as either 1 or 11, always pick the favorable option.
- Jack, Queen and King counts as 10. 
- Other cards count as their numerical values.

### Dealer’s policy:
1. If dealer has an Ace, it will count as 11 unless it makes dealer busts
2. Dealer always hits until card values goes over 16 or bust, with the exception that
   if dealer has Ace counted as 11 and has sum of 17 (e.g. Ace-6 combination), then dealer hits. 
   (Note: This is often referred to as hit on soft-17 policy and will give the dealer more advantage than a 
   stand on soft-17 policy. This can be adjusted in game.py.)

### Game results:
1. If player has Blackjack, player WINS if dealer does not have a blackjack, otherwise it's PUSH
2. If dealer has Blackjack, player LOSES if player does not have a blackjack
2. If player busts, player LOSES
3. If dealer busts, player WINS
4. If player and dealer have the same values, it's PUSH
5. If neither busts, player WINS if player has a higher value