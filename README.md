## Wordle Challenger:
This Wordle challenger mimics the popular Wordle game (developed by Josh Wardle) but adds a competitive twist. Challenge (and maybe even improve) your Wordle skills by competing against the computer! 

-----------------------------------------------------

## How a User Plays:
To play the game, run `python3 wordle-challenger.py` or `python wordle-challenger.py`

![Screen Shot 2022-08-16 at 3 49 54 AM](https://user-images.githubusercontent.com/68519543/184826739-e669c75e-a95d-4259-aacc-0e9fd5ed73d8.png)

Similar to the official Wordle game, there are 2309 actual solutions the game draws from, but users can guess from a list of 12966 valid 5-letter words to eliminate more incorrect words.

The game starts by asking a user for an input guess (which must be a valid 5-letter word) and returns the accuracy of each letter compared to the target solution just like Wordle (white is incorrect, yellow is misplaced, and green is correct). The computer also makes a guess but its words are hidden during the game to maintain fair play.

The user's objective is not only to guess the word within 6 turns but also ***guess in less turns than the computer***, otherwise they lose (as shown above). If the user guesses in less turns than the computer, they win. If both the user and computer use the same number of guesses, they tie. In the rare occasion the computer also fails to guess the word, both players lose.

When the game ends, the computer's guesses are revealed to help users improve their own Wordle skills. 

-----------------------------------------------------

## How the Computer Plays:
The computer plays by trying to eliminate as many wrong solutions as possible with each guess. It does this by calculating the frequency of each letter (A-Z) at each position (1-5) throughout the words in the official solution list. For example, A appears as the first letter 141 times while E appears as the first letter only 72 times. By adding up the frequencies for all 5 letters for every word, the computer's algorithm then chooses the word with the largest frequency to make its guess.

As more information about the target word is revealed through the Wordle colors, the algorithm adjusts the solution list it draws from: it deletes words that include incorrect letters, are missing correct and misplaced letters, and have correct letters in the wrong position.

Using this strategy, the computer tends to correctly guess most words in 3-4 guesses.

Note that the computer's algorithm still has room for optimization. As Jonathan Olson suggests (see references), utilizing the list of 12966 valid 5-letter words instead of just the solutions list as well as adopting a tree structure can help the computer narrow down words even faster. 

-----------------------------------------------------

## References:
https://notfunatparties.substack.com/p/wordle-solver#footnote-1

https://medium.com/codex/building-a-wordle-solver-with-python-77e3c2388d63

https://jonathanolson.net/experiments/optimal-wordle-solutions
