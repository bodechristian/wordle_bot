import pyautogui
import time
import cv2

import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict
from PIL import Image
from mss import mss


def default_colour():
    return "error"


COLORS = defaultdict(default_colour, {
    (83, 141, 78): "green",
    (181, 159, 59): "yellow",
    (58, 58, 60): "gray",
})


def alt_tab():
    pyautogui.keyDown('alt')
    time.sleep(.2)
    pyautogui.press('tab')
    time.sleep(.2)
    pyautogui.keyUp('alt')


def calc_score(_freqs, _word):
    _res = 0
    for i, letter in enumerate(_word):
        _res += _freqs[i][letter]
    return _res


def guess_info(used_letters, _freqs, all_words):
    """
    go over list and calculate letter-frequency per slot
    calculate score for each word
    return word with max score - but ignore words with letters already used or double letters
    @param: iterable of possible words
    @param: iterable of letters that are contained/correct in the target word
    """
    max_score, max_word = 0, ""
    for word in all_words:
        # ignore words with already investigated letters or without 5 distinct letters
        if any([_letter in word for _letter in used_letters]) or len(set(word)) < 5:
            continue
        score = calc_score(_freqs, word)
        # save word if new max but
        if score >= max_score:
            max_score = score
            max_word = word
    return max_word


def guess_solve(words, _freqs):
    """
    go over list and calculate letter-frequency per slot
    calculate score for each word
    return word with max score
    @param: iterable of possible words
    """
    max_score, max_word = 0, ""
    print(words)
    for word in words:
        score = calc_score(_freqs, word)
        # save word if new max
        if score >= max_score:
            max_score = score
            max_word = word
    return max_word


def update_wordlist(_cur_wordlist, _correct, _contained, _incorrect):
    new_wordlist = set()

    for word in _cur_wordlist:
        keep = True

        for letter, idx in _correct.items():
            if not word[idx] == letter:
                keep = False

        for letter, idxs in _contained.items():
            if not letter in word:
                keep = False
            for idx in idxs:
                if word[idx] == letter:
                    keep = False

        for letter in _incorrect:
            if letter in word:
                keep = False

        if keep:
            new_wordlist.add(word)
    return new_wordlist


def solve(word_list, all_words, _freqs, _correct, _contained, _incorrect):
    result = guess_info(list(_contained.keys())
                        + list(_correct.keys())
                        + list(_incorrect), _freqs, all_words)
    return result if result != "" else guess_solve(word_list, _freqs)


def enter_guess(_str):
    # write guess and press enter, then wait for the websites animation
    for _letter in _str:
        pyautogui.press(_letter)
        time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(3)


def update_data(_nb_guess, _guess, _view, _correct, _contained, _incorrect):
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
            pxl = img.getpixel((int(idx_letter*cell_width), int(_nb_guess*cell_height)))
            results.append(pxl)
        results_colours = list(map(lambda x: COLORS[x], results))
        print(results_colours)

        for i, col in enumerate(results_colours):
            if col == "green":
                _correct[_guess[i]] = i
            elif col == "yellow":
                _contained[_guess[i]].append(i)
            elif col == "gray":
                _incorrect += _guess[i]

        return _correct, _contained, _incorrect


def draw_reading_points():
    with mss() as sct:
        mon = sct.monitors[1]
        grid_view = {"left": mon["left"] + 765, 'top': 335, 'width': 340, 'height': 410}
        ss = sct.grab(grid_view)
        ss = Image.frombytes('RGB', (ss.width, ss.height), ss.rgb, )
        img = pil2cv(ss)

        cell_height, cell_width = grid_view["height"] / 6, grid_view["width"] / 5
        for idx_letter in range(5):
            for j in range(6):
                ss.putpixel((int(idx_letter*cell_width), int(j*cell_height)), (255, 105, 180))
        plt.imshow(ss)
        plt.show()

        cv2.imwrite("grid.png", img)
        plt.imshow(img)
        plt.show()


def pil2cv(img):
    img = np.array(img)
    img = img[:, :, ::-1].copy()
    return img


def find_grid():
    with mss() as sct:
        # can use sct.monitors[0] for all screens in 1 picture
        # then find the grid
        mon = sct.monitors[0]
        ss = sct.grab(mon)
        ss = Image.frombytes('RGB', (ss.width, ss.height), ss.rgb, )
        img = pil2cv(ss)

        template = cv2.imread("grid.png")
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)

        grid_view = {"left": mon["left"] + max_loc[0], 'top': mon["top"] + max_loc[1], 'width': 340, 'height': 420}
        return grid_view


def test():
    while True:
        print(pyautogui.position())


if __name__ == "__main__":
    # draw_reading_points()
    test()
