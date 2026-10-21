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


def main():
  modulus = 1000
  multiplier = 37
  increment = 1
  seed = 38
  count = 100
  alpha = 0.05

  print_line("=")
  print("ЗАДАНИЕ 2. Мультипликативный метод генерации псевдослучайных чисел")
  print_line("=")
  print("  Формула: x(i+1) = (a·x(i) + b) mod M;  u(i) = x(i) / M")
  print()
  print(f"  M = {modulus}")
  print(f"  a = {multiplier}")
  print(f"  b = {increment}")
  print(f"  x1 = {seed}   ← затравка (в выборку НЕ входит)")
  print(f"  N = {count}")
  print(f"  α = {alpha}")
  print()

  integer_sequence = generate_random_sequence(
    seed, multiplier, increment, modulus, count)

  print_line("=")
  print("ПОСЛЕДОВАТЕЛЬНОСТЬ ЦЕЛЫХ ЧИСЕЛ x_1 … x_N")
  print_line("=")
  print_sequence_table("", integer_sequence, is_float=False)

  float_sequence = [x / modulus for x in integer_sequence]

  print_line("=")
  print("НОРМИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ u_i = x_i / M ⊂ [0; 1)")
  print_line("=")
  print_sequence_table("", float_sequence, is_float=True)


if __name__ == "__main__":
  main()
