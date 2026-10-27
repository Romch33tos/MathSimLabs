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

# =========================================================
# ОБЩИЕ СТАТИСТИЧЕСКИЕ ФУНКЦИИ
# =========================================================

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

def laplace_phi(z):
  return 0.5 * math.erf(z / math.sqrt(2.0))


def normal_cdf(x, mean, sigma):
  return 0.5 + laplace_phi((x - mean) / sigma)


def chi2_critical(alpha, df):
  z_table = {0.10: 1.2816, 0.05: 1.6449, 0.025: 1.9600,
             0.01: 2.3263, 0.005: 2.5758, 0.001: 3.0902}
  z = z_table.get(alpha, 1.6449)
  term = 1 - 2.0 / (9 * df) + z * math.sqrt(2.0 / (9 * df))
  return df * term ** 3

def merge_small(intervals, emp, theo, min_freq=5):
  """Объединяет малочисленные интервалы с соседними."""
  intervals = list(intervals)
  emp = list(emp)
  theo = list(theo)
  changed = True
  while changed and len(intervals) > 2:
    changed = False
    for i in range(len(intervals)):
      if emp[i] < min_freq or theo[i] < min_freq:
        if i == 0:
          j = 1
        elif i == len(intervals) - 1:
          j = i - 1
        else:
          if emp[i - 1] + theo[i - 1] <= emp[i + 1] + theo[i + 1]:
            j = i - 1
          else:
            j = i + 1
        a = min(intervals[i][0], intervals[j][0])
        b = max(intervals[i][1], intervals[j][1])
        new_i = (a, b)
        new_e = emp[i] + emp[j]
        new_t = theo[i] + theo[j]
        for idx in sorted([i, j], reverse=True):
          intervals.pop(idx)
          emp.pop(idx)
          theo.pop(idx)
        pos = min(i, j)
        intervals.insert(pos, new_i)
        emp.insert(pos, new_e)
        theo.insert(pos, new_t)
        changed = True
        break
  return intervals, emp, theo


def print_freq_table(intervals, mids, emp, theo):
  """Печатает таблицу частот с вкладами в хи-квадрат."""
  sep = ("  +" + "-" * 4 + "+" + "-" * 22 + "+" + "-" * 14 + "+" +
         "-" * 8 + "+" + "-" * 12 + "+" + "-" * 20 + "+")
  print(sep)
  print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
    "№", "Интервал", "Середина x_i", "n_i", "n_i'", "(n_i−n_i')²/n_i'"))
  print(sep)
  s = len(intervals)
  chi2_obs = 0.0
  for i in range(s):
    bracket = "]" if i == s - 1 else ")"
    interval_str = f"[{fmt(intervals[i][0])}; {fmt(intervals[i][1])}{bracket}"
    term = ((emp[i] - theo[i]) ** 2 / theo[i]) if theo[i] > 0 else 0.0
    chi2_obs += term
    print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
      i + 1, interval_str, fmt(mids[i], 6), emp[i],
      fmt(theo[i], 4), fmt(term, 4)))
  print(sep)
  print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
    "Σ", "", "", sum(emp), fmt(sum(theo), 4), fmt(chi2_obs, 4)))
  print(sep)
  print()
  return chi2_obs
