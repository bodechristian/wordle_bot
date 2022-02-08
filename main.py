import pickle

from collections import Counter
from util import *


# initialize stuff
nb_letters = 5
all_words = load_words("wordlelist")
wordlist = all_words.copy()

frequency_table = get_freqs(all_words)

letters_correct = defaultdict(list)
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
    guess = solve(wordlist, all_words, frequency_table, nb_guess, letters_correct, letters_contained, letters_incorrect)
    print(f"Guessing {guess}")
    enter_guess(guess)
    solved, letters_correct, letters_contained, letters_incorrect = update_data(nb_guess, guess, view,
                                                                        letters_correct, letters_contained, letters_incorrect)
    if solved:
        print("\n--------------")
        print("Correct!!!")
        print(f"The correct guess was {guess}")
        break
    print()
