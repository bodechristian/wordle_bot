import numpy as np

from util import *


def game(_all_words, screen_grab, style_strategy, style_frequency, solution="", debug=False):
    if not screen_grab and (solution == "" or len(solution) != 5):
        print("Error schmerror!!! Given solution is not a valid solution.")
        return None

    _wordlist = _all_words.copy()
    view = {}
    # either play it by screen grabbing the browser game
    # or simulating it, then it needs a solution word
    if screen_grab:
        # wait a bit and then detect grid and click where the grid has been detected
        time.sleep(2)
        view = find_grid()
        pyautogui.click(view["left"], view["top"])

    # (correct letters, letters contained, incorrect letters)
    letters_data = (defaultdict(list), defaultdict(list), "")

    needed_guesses = 0
    guesses = []
    # do the 6 guesses
    for nb_guess in range(6):
        if debug:
            print(f"Guess {nb_guess+1}:")
        _wordlist = update_wordlist(_wordlist, letters_data)
        guess = solve(_wordlist, _all_words, nb_guess, letters_data, strategy=style_strategy, frequency=style_frequency,
                      debug=debug)
        if guess is None:
            break
        guesses.append(guess)
        if debug:
            print(f"Guessing {guess}")
        if screen_grab:
            enter_guess(guess)
            solved, letters_data = update_data_screengrab(nb_guess, guess, view, letters_data, debug=debug)
        # no scren grab means its a simulation and it took a solution
        else:
            solved, letters_data = update_data_simul(guess, solution, letters_data)

        if solved:
            if debug:
                print("\n--------------")
                print("Correct!!!")
                print(f"The correct guess was {guess}")
                print()
            needed_guesses = nb_guess + 1
            break
        if nb_guess == 5:
            needed_guesses = 7

    return needed_guesses, guesses


def simulation(_strats, _freqs, _sols, debug=False):
    results = defaultdict(list)

    for i, solution in enumerate(_sols):
        print(f"{solution}:")
        _l = len(_sols)
        _ll = len(strategies) * len(frequencies)
        _cnt = 0
        for strat in strategies:
            for freq in frequencies:
                result, guesses = game(all_words, False, strat, freq, solution=solution, debug=debug)
                results[(strat, freq)].append(result)
                _cnt += 1
                print(f"Word {i}/{_l}.\tMethod {_cnt}/{_ll}\t{solution} --> {result} guesses ({strat}, {freq})\t" +
                      " --> ".join(guesses))
        print()

    eval_text(results)
    eval_graph(results)
    save_data(results, "results")


if __name__ == "__main__":
    # initialize stuff
    all_words = load_words("wordlelist")

    strategies = ["solve", "info", "yolo"]
    frequencies = ["slots", "words"]
    solutions = all_words.copy()

    simulation(strategies, frequencies, ["elder", "pause"])
    #game(all_words, False, strategies[0], frequencies[0], solution="pause", debug=True)
    """with open("results.pkl", "rb") as f:
        data = pickle.load(f)
    eval_graph(data)"""







