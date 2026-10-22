import math
import random

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

def sample_mean(data):
  return sum(data) / len(data)


def sample_variance(data):
  n = len(data)
  m = sample_mean(data)
  return sum((x - m) ** 2 for x in data) / (n - 1)

def sturges_k(n):
  return int(round(1 + 3.3221 * math.log10(n)))


def build_intervals(x_min, x_max, k):
  h = (x_max - x_min) / k
  intervals = []
  for i in range(k):
    a = x_min + i * h
    b = x_min + (i + 1) * h
    if i == k - 1:
      b = x_max
    intervals.append((a, b))
  return intervals


def count_frequencies(data, intervals):
  freqs = []
  last = len(intervals) - 1
  for i, (a, b) in enumerate(intervals):
    if i == last:
      cnt = sum(1 for v in data if a <= v <= b)
    else:
      cnt = sum(1 for v in data if a <= v < b)
    freqs.append(cnt)
  return freqs
