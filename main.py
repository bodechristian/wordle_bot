import pickle

from collections import Counter
from util import *


# initialize stuff
nb_letters = 5
with open(f"{nb_letters}-letter-combinations.pkl", "rb") as f:
    all_words = pickle.load(f)
wordlist = all_words.copy()

frequency_table = {i: Counter() for i in range(nb_letters)}
for word in all_words:
    for i, letter in enumerate(word):
        frequency_table[i][letter] += 1

letters_correct = {}
letters_contained = defaultdict(list)
letters_incorrect = ""


# wait a bit and then click where the grid has been detected
time.sleep(1)
view = find_grid()
pyautogui.click(view["left"], view["top"])
time.sleep(1)

# do the 6 guesses
for nb_guess in range(6):
    print(f"Guess {nb_guess+1}:")
    wordlist = update_wordlist(wordlist, letters_correct, letters_contained, letters_incorrect)
    guess = solve(wordlist, all_words, frequency_table, letters_correct, letters_contained, letters_incorrect)
    print(f"Guessing {guess}")
    enter_guess(guess)
    letters_correct, letters_contained, letters_incorrect = update_data(nb_guess, guess, view,
                                                                        letters_correct, letters_contained, letters_incorrect)
    print()
