import math

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

def generate_random_sequence(seed, multiplier, increment, modulus, count):
  sequence = []
  current = seed
  for _ in range(count):
    current = (multiplier * current + increment) % modulus
    sequence.append(current)
  return sequence

def print_sequence_table(title, seq, is_float=False):
  if title:
    print(title)
  columns = 5
  sep = "  +" + "-" * 8 + "+" + ("-" * 10 + "+") * columns
  print(sep)
  header = "  |{:^8}|".format("i")
  for j in range(columns):
    header += "{:^10}|".format(f"x{j + 1}")
  print(header)
  print(sep)
  rows = (len(seq) + columns - 1) // columns
  for row in range(rows):
    line = "  |{:^8}|".format(row * columns + 1)
    for col in range(columns):
      idx = row * columns + col
      if idx < len(seq):
        if is_float:
          line += "{:^10}|".format(fmt(seq[idx], 4))
        else:
          line += "{:^10}|".format(seq[idx])
      else:
        line += "{:^10}|".format("")
    print(line)
  print(sep)
  print()

def sturges_interval_length(x_max, x_min, n):
  return (x_max - x_min) / (1 + 3.3221 * math.log10(n))


def build_intervals(x_min, x_max, h):
  num_intervals = int(math.ceil((x_max - x_min) / h))
  intervals = []
  start = x_min
  for i in range(num_intervals):
    end = start + h
    if i == num_intervals - 1:
      end = x_max
    intervals.append((start, end))
    start = end
  return intervals


def count_frequencies(data, intervals):
  frequencies = []
  last = len(intervals) - 1
  for i, (start, end) in enumerate(intervals):
    if i == last:
      count = sum(1 for v in data if start <= v <= end)
    else:
      count = sum(1 for v in data if start <= v < end)
    frequencies.append(count)
  return frequencies
