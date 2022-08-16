import copy
import re
import numpy as np
import pandas as pd
import random
from collections import Counter, defaultdict
from random import randint

# Official Wordle game allows users to guess from 12966 valid words
with open('guesses.txt') as file:
    possible_guesses = file.readlines()
possible_guess_list = [guess.upper()[:5] for guess in possible_guesses]

# Official Wordle game has only 2309 actual possible solutions
with open('solutions.txt') as file:
    possible_solutions = file.readlines()
possible_solution_list = [solution.upper()[:5] for solution in possible_solutions]

# Use DataFrame to indepently list letters 1-5 for each possible solution
solutions_arr = np.array([list(word) for word in possible_solution_list])
solutions_df = pd.DataFrame(data=solutions_arr, columns=[f'Letter_{i+1}' for i in range(5)])
solutions_df['Word'] = possible_solution_list

# Create Game class to hold Wordle game logic
class Game:
    def __init__(self, solutions_all_df):
        # Possible letters in a word
        self.letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        # Store correct letters placed in the wrong location
        self.misplaced_letters = Counter()
        # Possible solutions
        self.possible_solutions_df = solutions_all_df.copy(deep=True)
        # Dictionary of possible solutions in a game as we learn more about the word
        self.letters_dict = defaultdict(str)
        for i in range(5):
            self.letters_dict[i+1] = None
        # Dictionary of letters counts at each index as learn more about the word
        self.count_letters_dict = defaultdict(str)
        for i in range(5):
            self.count_letters_dict[i+1] = Counter(solutions_all_df[f'Letter_{i+1}'])

    # Given a set of 26 letters, add up the their frequency at each index
    # Repeat this for all 5 letters in a word to obtain a word frequency score
    def calculate_frequency(self, letters):
        letters = re.sub('^A-Z', '', letters.upper())
        assert len(letters) == 5, 'Word must be 5 letters long'
        frequency = 0
        for num, letter in enumerate(list(letters.upper())):
            frequency += self.count_letters_dict[num+1][letter]
        return frequency

    # In a game state, return a DataFrame of possible 5 letter solutions
    # Results are ordered from highest to lowest frequency scores
    def guess(self):
        # Reset all letter counts
        for i in range(5):
            self.count_letters_dict[i+1] = Counter(self.possible_solutions_df[f'Letter_{i+1}'])
        # Vectorize calculate_frequency to speed up runtime
        vect_calculate_frequency = np.vectorize(self.calculate_frequency)
        # Calculate frequency of each word
        self.possible_solutions_df['Frequency'] = vect_calculate_frequency(self.possible_solutions_df['Word'])
        # Sort words from highest to lowest frequency
        self.possible_solutions_df = self.possible_solutions_df.sort_values(by='Frequency', ascending=False)
        return self.possible_solutions_df

    # Filters through DataFrame of possible solutions
    # Returns true if a word has at least all the misplaced letters
    def check_misplaced(self, word):
        word = re.sub(r'[^A-Z]', '', word.upper())
        assert len(word) == 5, 'Word must be 5 letters long'
        word_list = list(word)

        # Create array of indices that remain unsolved
        unsolved = [key for key, value in self.letters_dict.items() if value is None]
        # Filter word list to only include unsolved positions
        word_list_unsolved = [word_list[i-1] for i in unsolved]
        lettercounts_dict = Counter(word_list_unsolved)

        # Compare to dictionary of misplaced letters
        valid = True
        for key, value in self.misplaced_letters.items():
            if lettercounts_dict[key] < value:
                valid = False
        return valid

    # Takes in 5 letter guess and outputs a list of results for each letter
    # White square if incorrect, yellow square if misplaced, green square if correct
    def update(self, guess, results):
        guess = re.sub(r'[^A-Z]', '', guess.upper())
        assert len(guess) == 5, 'Guess must be 5 letters long'
        assert len(results) == 5, 'Results list must contain 5 items'
        assert all([color in ["⬜", "🟨", "🟩"] for color in results]), 'Results list can only contain white, yellow, green squares'

        # Convert guess into list
        guess_list = list(guess.upper())
        # Create DataFrame of guess results
        guess_results_df = pd.DataFrame(data=list(zip(guess_list, results)), columns=['Letter', 'Result'], index=np.arange(1,6))

        # Avoid iterating through letters that are already solved
        solved = [key for key, value in self.letters_dict.items() if value is not None]

        # Update correct answers
        correct_answers_df = guess_results_df.query('Result=="🟩"')
        if correct_answers_df.shape[0] > 0:
            for index, row in correct_answers_df.iterrows():
                if index in solved:
                    pass
                else:
                    correct_letter = row['Letter']
                    self.letters_dict[index] = correct_letter
                    if correct_letter in self.misplaced_letters.keys():
                        self.misplaced_letters[correct_letter] -= 1
                    self.possible_solutions_df = self.possible_solutions_df.query(f'Letter_{index}=="{correct_letter}"')

        # Add misplaced letters to answers list if it's a new letter
        misplaced_answers_df = guess_results_df.query('Result=="🟨"')
        if misplaced_answers_df.shape[0] > 0:
            for index, row in misplaced_answers_df.iterrows():
                misplaced_letter = row['Letter']
                self.possible_solutions_df = self.possible_solutions_df.query(f'Letter_{index}!="{misplaced_letter}"')
            guess_misplaced_letters = misplaced_answers_df['Letter'].values
            guess_misplaced_letters_dict = Counter(guess_misplaced_letters)
            for key, value in guess_misplaced_letters_dict.items():
                self.misplaced_letters[key] = value
            vect_check_misplaced = np.vectorize(self.check_misplaced)
            self.possible_solutions_df['Valid'] = vect_check_misplaced(self.possible_solutions_df['Word'])
            self.possible_solutions_df = self.possible_solutions_df.query('Valid == True')
            self.possible_solutions_df = self.possible_solutions_df.drop('Valid', axis=1)

        # Remove wrong letters from the list to guess from
        wrong_answers_df = guess_results_df.query('Result=="⬜"')
        if wrong_answers_df.shape[0] > 0:
            # Avoid double counts
            for letter in wrong_answers_df['Letter'].unique():
                if self.misplaced_letters[letter] == 0:
                    self.letters.remove(letter)

        # Remove from list of possible solutions all rows where for letters to be
        # guessed, they're not included in the list of possible letters
        to_solve = [key for key, value in self.letters_dict.items() if value is None]
        for index in to_solve:
            index_letters = self.possible_solutions_df[f'Letter_{index}']
            index_in_possibleletters = [letter in self.letters for letter in index_letters]
            self.possible_solutions_df = self.possible_solutions_df[index_in_possibleletters].copy(deep=True)

# Carry out one round of Wordle Challenger
def game_play(target, possible_words_df):
    assert len(target) == 5, "Target must be 5 letters long"
    assert all(possible_words_df.columns == ['Letter_1', 'Letter_2', 'Letter_3', 'Letter_4', 'Letter_5', 'Word'])

    NewGame = Game(possible_words_df)
    target_letters = list(target)

    for turn in range(6):
        # Starting guess = word with highest frequency score for all letters
        guess = NewGame.guess().iloc[0]["Word"]
        guess_letters = list(guess)

        # Dictionary of turn results at each index
        results_dict = defaultdict(str)
        for i in range(5):
            results_dict[i] = None

        # Assign correct letters with a green square
        for index, letter in enumerate(guess_letters):
            if letter == target_letters[index]:
                results_dict[index] = "🟩"

        # If remaining letters appear in the target word, assign a yellow square
        # Else assign a white square
        remaining_positions = [key for key, value in results_dict.items() if value is None]
        # Guess is correct
        if len(remaining_positions) == 0:
            results = "['🟩', '🟩', '🟩', '🟩', '🟩']"
        else:
            remaining_guess_letters = [[guess_letters[i], i] for i in remaining_positions]
            remaining_target_letters = [target_letters[i] for i in remaining_positions]
            target_lettercount_dict = Counter(remaining_target_letters)

            # Check if remaining guess letters appear in the target word
            for [letter, position] in remaining_guess_letters:
                if target_lettercount_dict[letter] > 0:
                    target_lettercount_dict[letter] -= 1
                    results_dict[position] = "🟨"
                else:
                    results_dict[position] = "⬜"
            
            results = list(results_dict.values())
    
        print(f'Turn {turn+1}')
        print(guess)
        print(f'{results}')
        if results == "['🟩', '🟩', '🟩', '🟩', '🟩']":
            print(f'Game won in {turn + 1} turns!')
            return
        if turn == 5:
            print(f'Unsolved :( The word was {target}.')
            return

        NewGame.update(guess, results)
                
rand = randint(0, len(possible_solution_list) - 1)
target = possible_solution_list[rand]
game_play(target, solutions_df)

# ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']