import csv

FILE = "words_guesses"


def txt2csv():
    with open(f"{FILE}.csv", "w", newline="") as f_out:
        writer = csv.writer(f_out)
        with open(f"{FILE}.txt", "r", newline="\r\n") as f_in:
            writer.writerow([line.strip() for line in f_in.readlines()])


if __name__ == "__main__":
    txt2csv()
