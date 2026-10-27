import math
import random


# =========================================================
# ФОРМАТИРОВАНИЕ И ПЕЧАТЬ (стиль как в образце)
# =========================================================

def fmt(value, digits=4):
  if value == 0:
    return "0"
  s = f"{value:.{digits}f}"
  s = s.rstrip("0").rstrip(".")
  if s == "-0":
    s = "0"
  return s


def print_line(char="-", length=78):
  print(char * length)


def print_header(title):
  print_line("=")
  print(title)
  print_line("=")


def print_subheader(title):
  print_line("-")
  print(title)
  print_line("-")


def print_sequence_table(title, seq, is_float=True):
  """Печатает последовательность в таблицу 5 столбцов по 20 строк."""
  if title:
    print(title)
  columns = 5
  sep = "  +" + "-" * 8 + "+" + ("-" * 12 + "+") * columns
  print(sep)
  header = "  |{:^8}|".format("i")
  for j in range(columns):
    header += "{:^12}|".format(f"x({j + 1})")
  print(header)
  print(sep)
  rows = (len(seq) + columns - 1) // columns
  for row in range(rows):
    line = "  |{:^8}|".format(row * columns + 1)
    for col in range(columns):
      idx = row * columns + col
      if idx < len(seq):
        if is_float:
          line += "{:^12}|".format(fmt(seq[idx], 4))
        else:
          line += "{:^12}|".format(seq[idx])
      else:
        line += "{:^12}|".format("")
    print(line)
  print(sep)
  print()
