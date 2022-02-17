import pyautogui
import time
import cv2
import pickle
import csv

import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict, Counter
from PIL import Image
from mss import mss


def default_colour():
    return "error"


COLORS = {
    "wordle": defaultdict(default_colour, {
        (83, 141, 78): "green",
        (181, 159, 59): "yellow",
        (58, 58, 60): "gray",
    }),
    "squabble": defaultdict(default_colour, {
        (46, 216, 60): "green",
        (214, 190, 0): "yellow",
        (155, 93, 247): "gray",
    }),
}


def alt_tab():
    pyautogui.keyDown('alt')
    time.sleep(.2)
    pyautogui.press('tab')
    time.sleep(.2)
    pyautogui.keyUp('alt')


def get_freqs_slots(_words):
    freqs = {i: Counter() for i in range(5)}
    for word in _words:
        for i, letter in enumerate(word):
            freqs[i][letter] += 1
    """for i in range(5):
        print(f"Slot {i+1}:\n\t{freqs[i]}")"""
    return freqs


def get_freqs_words(_words):
    _freqs = Counter()
    for _word in _words:
        for _letter in set(_word):
            _freqs[_letter] += 1
    return _freqs


def calc_score_slots(_freqs, _word):
    _res = 0
    for i, letter in enumerate(_word):
        _res += _freqs[i][letter]
    return _res


def calc_score_words(_freqs, _word):
    _res = 0
    for _letter in _word:
        _res += _freqs[_letter]
    return _res


def guess_info(used_letters, _freqs, all_words, func_calc_score):
    max_score, max_word = 0, ""
    for word in all_words:
        # ignore words with already investigated letters or without 5 distinct letters
        if any([_letter in word for _letter in used_letters]) or len(set(word)) < 5:
            continue
        score = func_calc_score(_freqs, word)
        # save word if new max but
        if score >= max_score:
            max_score = score
            max_word = word
    return max_word


def guess_info_yolo(used_letters, _freqs, all_words, func_calc_score):
    min_score, min_word = float("inf"), ""
    for word in all_words:
        # ignore words with already investigated letters or without 5 distinct letters
        if any([_letter in word for _letter in used_letters]) or len(set(word)) < 5:
            continue
        score = func_calc_score(_freqs, word)
        # save word if new min but
        if score <= min_score:
            min_score = score
            min_word = word
    return min_word


def guess_solve(words, _freqs, func_calc_score, debug=False):
    max_score, max_word = 0, ""
    if debug:
        print(words)
    for word in words:
        score = func_calc_score(_freqs, word)
        # save word if new max
        if score >= max_score:
            max_score = score
            max_word = word
    return max_word


def solve_infoguesses(word_list, all_words, _freqs, _data, func_calc_score, yolo=False, debug=False):
    _correct, _contained, _incorrect = _data
    if debug:
        print(word_list)
    if len(word_list) == 1:
        return list(word_list)[0]
    if yolo:
        result = guess_info_yolo(list(_contained.keys())
                                 + list(_correct.keys())
                                 + list(_incorrect), _freqs, all_words, func_calc_score)
    else:
        result = guess_info(list(_contained.keys())
                            + list(_correct.keys())
                            + list(_incorrect), _freqs, all_words, func_calc_score)
    return result if result != "" else guess_solve(word_list, _freqs, func_calc_score, debug=debug)


def solve(word_list, all_words, nb_guess, _data, strategy="info", frequency="words", debug=False):
    if frequency == "words":
        _freqs = get_freqs_words(all_words)
        func_score = calc_score_words
    elif frequency == "slots":
        _freqs = get_freqs_slots(all_words)
        func_score = calc_score_slots
    else:
        print("invalid frequency parameter")
        return None

    if strategy == "info":
        return solve_infoguesses(word_list, all_words, _freqs, _data, func_score, debug=debug)
    elif strategy == "yolo":
        return solve_infoguesses(word_list, all_words, _freqs, _data, func_score, yolo=True, debug=debug)
    elif strategy == "solve":
        return guess_solve(word_list, _freqs, func_score, debug=debug)
    else:
        print(f"Invalid strategy. {strategy}")
        return None


def update_wordlist(_cur_wordlist, _data):
    _correct, _contained, _incorrect = _data
    new_wordlist = set()
    for word in _cur_wordlist:
        keep = True

        for letter, idxs in _correct.items():
            for idx in idxs:
                if not word[idx] == letter:
                    keep = False

        for letter, idxs in _contained.items():
            if letter not in word:
                keep = False
            for idx in idxs:
                if word[idx] == letter:
                    keep = False

        for letter in _incorrect:
            for i, el in enumerate(word):
                if el == letter and i not in _correct[letter]:
                    keep = False

        if keep:
            new_wordlist.add(word)
    return new_wordlist


def enter_guess(_str, platform="wordle"):
    # write guess and press enter, then wait for the websites animation
    for _letter in _str:
        pyautogui.press(_letter)
        time.sleep(0)
    pyautogui.press("enter")
    if platform == "wordle":
        time.sleep(3)
    elif platform == "squabble":
        time.sleep(0.5)


def update_data_simul(_guess, _sol, _data):
    _correct, _contained, _incorrect = _data

    for i, _letter in enumerate(_guess):
        # correct letter?
        if _letter == _sol[i]:
            _correct[_guess[i]].append(i)
        # letter contained?
        elif _letter in _sol:
            _contained[_guess[i]].append(i)
        # letter incorrect
        else:
            _incorrect += _letter

    return _guess == _sol, (_correct, _contained, _incorrect)


def update_data_screengrab(_nb_guess, _guess, _view, _data, debug=False, platform="wordle"):
    _correct, _contained, _incorrect = _data
    with mss() as sct:
        ss = sct.grab(_view)
        # colour correct
        img = Image.frombytes(
            'RGB',
            (ss.width, ss.height),
            ss.rgb,
        )
        cell_height, cell_width = _view["height"] / 6, _view["width"] / 5

        results = []
        for idx_letter in range(5):
            pxl = img.getpixel((int(idx_letter*cell_width+(1/4)*cell_width),
                                int(_nb_guess*cell_height+(1/4)*cell_height)))
            results.append(pxl)
        results_colours = list(map(lambda x: COLORS[platform][x], results))

        if debug:
            print(results_colours)

        # correct guess
        solved = False
        if all([_col == "green" for _col in results_colours]):
            solved = True

        for i, col in enumerate(results_colours):
            if col == "green":
                _correct[_guess[i]].append(i)
            elif col == "yellow":
                _contained[_guess[i]].append(i)
            elif col == "gray":
                _incorrect += _guess[i]

        return solved, (_correct, _contained, _incorrect)


def draw_reading_points(_grid_view):
    with mss() as sct:
        ss = sct.grab(_grid_view)
        ss = Image.frombytes('RGB', (ss.width, ss.height), ss.rgb, )
        img = pil2cv(ss)

        cell_height, cell_width = _grid_view["height"] / 6, _grid_view["width"] / 5
        for idx_letter in range(5):
            for j in range(6):
                ss.putpixel((int(idx_letter*cell_width+(1/4)*cell_width), int(j*cell_height+(1/4)*cell_height)),
                            (255, 105, 180))

        plt.imshow(ss)
        plt.show()


def pil2cv(img):
    img = np.array(img)
    img = img[:, :, ::-1].copy()
    return img


def find_grid(platform="wordle"):
    with mss() as sct:
        # can use sct.monitors[0] for all screens in 1 picture
        # then find the grid
        mon = sct.monitors[0]
        ss = sct.grab(mon)
        ss = Image.frombytes('RGB', (ss.width, ss.height), ss.rgb, )
        img = pil2cv(ss)

        template = cv2.imread(f"grid_{platform}.png")
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)

        grid_view = {"left": mon["left"] + max_loc[0], 'top': mon["top"] + max_loc[1], 'width': template.shape[1],
                     'height': template.shape[0]}
        return grid_view


def test():
    _view = find_grid()
    draw_reading_points(_view)


def load_words(_str):
    if _str == "pkl":
        with open(f"5-letter-combinations.pkl", "rb") as f:
            all_words = pickle.load(f)
    elif _str == "wordlelist":
        with open("wordlelist.csv", newline="") as f:
            csvreader = csv.reader(f, delimiter=",")
            all_words = list(csvreader)[0]
    return all_words


def save_data(_data, _name):
    with open(f"{_name}.pkl", "wb") as f:
        pickle.dump(_data, f)


def eval_text(_results):
    print()
    for key, val in _results.items():
        val = np.asarray(val)
        _misses = np.where(val == 7)[0]
        nb_misses = len(_misses)
        val = np.delete(val, _misses)
        avg = np.average(val)
        print(f"{key} guessed the solution in an average of {avg} guesses and {nb_misses} misses")


def eval_graph(_results):
    nb_cols = 2
    nb_rows = len(_results.keys()) // nb_cols

    fig, ax = plt.subplots(nb_rows, nb_cols, figsize=(9, 7), sharey="all")

    for i, (key, val) in enumerate(_results.items()):
        val = np.asarray(val)
        _misses = np.where(val == 7)
        nb_misses = len(_misses[0])
        val = np.delete(val, _misses)

        ax[i // nb_cols, i % nb_cols].set_title(", ".join(key) +
                                                f"\n{round(np.average(val), 2)} avg.\n{nb_misses} misses")
        ax[i // nb_cols, i % nb_cols].hist(val, bins=np.linspace(0.5, 6.5, 7), alpha=0.8, ec="black")

    plt.suptitle("Number of guesses needed for different strategies")
    plt.tight_layout()
    plt.savefig("temp")
    plt.show()


def eval_from_file(file="results.pkl"):
    with open(file, "rb") as f:
        data = pickle.load(f)
    eval_graph(data)


if __name__ == "__main__":
    # draw_reading_points()
    test()
