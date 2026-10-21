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


def chi2_critical(alpha, degrees_of_freedom):
  z_table = {0.10: 1.2816, 0.05: 1.6449, 0.025: 1.9600,
             0.01: 2.3263, 0.005: 2.5758, 0.001: 3.0902}
  z = z_table.get(alpha, 1.6449)
  term = 1 - 2.0 / (9 * degrees_of_freedom) + \
         z * math.sqrt(2.0 / (9 * degrees_of_freedom))
  return degrees_of_freedom * term ** 3


def chi_square_test(data, alpha=0.05):
  n = len(data)
  print_header("КРИТЕРИЙ χ² ПИРСОНА (проверка равномерности распределения)")

  print_subheader("ШАГ 1. Оценки параметров равномерного распределения")

  x_bar = sum(data) / n
  variance = sum((x - x_bar) ** 2 for x in data) / n
  sigma = math.sqrt(variance)
  sqrt3 = math.sqrt(3)
  a_est = x_bar - sqrt3 * sigma
  b_est = x_bar + sqrt3 * sigma

  print(f"  N = {n}")
  print(f"  x̄ = (1/N)·Σx_i = {fmt(x_bar, 6)}")
  print(f"  D = (1/N)·Σ(x_i − x̄)² = {fmt(variance, 6)}")
  print(f"  σ = √D = {fmt(sigma, 6)}")
  print(f"  √3 = {fmt(sqrt3, 6)}")
  print()
  print("  a* = x̄ − √3·σ = "
        f"{fmt(x_bar, 6)} − {fmt(sqrt3, 6)}·{fmt(sigma, 6)} = {fmt(a_est, 6)}")
  print("  b* = x̄ + √3·σ = "
        f"{fmt(x_bar, 6)} + {fmt(sqrt3, 6)}·{fmt(sigma, 6)} = {fmt(b_est, 6)}")
  print()
  x_min = min(data)
  x_max = max(data)
  print(f"  X_min = {fmt(x_min, 6)}")
  print(f"  X_max = {fmt(x_max, 6)}")
  print(f"  Число значений < a*: {sum(1 for v in data if v < a_est)}")
  print(f"  Число значений > b*: {sum(1 for v in data if v > b_est)}")
  print()

  print_subheader("ШАГ 2. Разбиение на интервалы (формула Стерджерса)")

  h = sturges_interval_length(x_max, x_min, n)
  intervals = build_intervals(x_min, x_max, h)
  s = len(intervals)
  frequencies = count_frequencies(data, intervals)

  print("  h = (X_max − X_min) / (1 + 3.3221·lg N)")
  print(f"    lg({n}) = {fmt(math.log10(n), 6)}")
  print(f"    1 + 3.3221·lg(N) = {fmt(1 + 3.3221 * math.log10(n), 6)}")
  print(f"    h = ({fmt(x_max, 6)} − {fmt(x_min, 6)}) / "
        f"{fmt(1 + 3.3221 * math.log10(n), 6)} = {fmt(h, 6)}")
  print(f"  Число интервалов s = {s}")
  print(f"  Проверка: Σn_i = {sum(frequencies)} (= N = {n})")
  print()

  print_subheader("ШАГ 3. Эмпирические и теоретические частоты (метод середин)")

  mids = [(st + en) / 2.0 for (st, en) in intervals]
  theoretical = []
  theoretical.append(n * (mids[0] - a_est) / (b_est - a_est))
  for i in range(1, s - 1):
    theoretical.append(n * h / (b_est - a_est))
  theoretical.append(n * (b_est - mids[s - 2]) / (b_est - a_est))

  print("  Середины интервалов x_i:")
  for i, m in enumerate(mids):
    print(f"    x_{i + 1} = {fmt(m, 6)}")
  print()
  print("  Формулы (методичка, стр. 3):")
  print("    n1'  = N·(x1 − a*)/(b* − a*)")
  print("    ni'  = N·h/(b* − a*)        для i = 2..s−1")
  print("    ns'  = N·(b* − x_(s−1))/(b* − a*)")
  print()

  sep = ("  +" + "-" * 4 + "+" + "-" * 20 + "+" + "-" * 12 + "+" +
         "-" * 8 + "+" + "-" * 12 + "+" + "-" * 20 + "+")
  print(sep)
  print("  |{:^4}|{:^20}|{:^12}|{:^8}|{:^12}|{:^20}|".format(
    "№", "Интервал", "Середина x_i", "n_i", "n_i'", "(n_i−n_i')²/n_i'"))
  print(sep)
  chi2_obs = 0.0
  for i in range(s):
    diff = frequencies[i] - theoretical[i]
    term = (diff ** 2) / theoretical[i] if theoretical[i] > 0 else 0.0
    chi2_obs += term
    bracket = "]" if i == s - 1 else ")"
    interval_str = f"[{fmt(intervals[i][0])}; {fmt(intervals[i][1])}{bracket}"
    print("  |{:^4}|{:^20}|{:^12}|{:^8}|{:^12}|{:^20}|".format(
      i + 1, interval_str, fmt(mids[i], 6), frequencies[i],
      fmt(theoretical[i], 4), fmt(term, 4)))
  print(sep)
  print("  |{:^4}|{:^20}|{:^12}|{:^8}|{:^12}|{:^20}|".format(
    "Σ", "", "", sum(frequencies), fmt(sum(theoretical), 4), fmt(chi2_obs, 4)))
  print(sep)
  print()

  print("  Малочисленных интервалов (n_i < 5) "
        f"{'НЕТ' if all(f >= 5 for f in frequencies) else 'ЕСТЬ'}: "
        f"мин. n_i = {min(frequencies)}")
  print()

  print_subheader("ШАГ 4. Критическое значение χ²")

  df = s - 3
  if df < 1:
    df = 1
  chi2_cr = chi2_critical(alpha, df)
  print(f"  k = s − 3 = {s} − 3 = {df}")
  print(f"  α = {alpha}")
  print(f"  χ²_кр(α; k) = {fmt(chi2_cr, 4)}")
  print()

  print_subheader("ШАГ 5. Проверка гипотезы")
  print(f"  χ²_набл = {fmt(chi2_obs, 4)}")
  print(f"  χ²_кр   = {fmt(chi2_cr, 4)}")
  print()
  if chi2_obs < chi2_cr:
    print("  χ²_набл < χ²_кр  →  гипотеза о равномерном распределении")
    print("  НЕ отвергается.")
  else:
    print("  χ²_набл > χ²_кр  →  гипотеза о равномерном распределении")
    print("  ОТВЕРГАЕТСЯ.")
  print()
  print_line("=")
  print()


SERIES_CRITICAL_TABLE = {
  20: {0.99: (5, 15), 0.975: (6, 14), 0.95: (7, 13), 0.05: (7, 13), 0.025: (6, 14), 0.01: (5, 15)},
  21: {0.99: (5, 16), 0.975: (6, 15), 0.95: (7, 14), 0.05: (8, 15), 0.025: (7, 16), 0.01: (6, 17)},
  22: {0.99: (6, 17), 0.975: (7, 16), 0.95: (8, 15), 0.05: (8, 15), 0.025: (7, 16), 0.01: (6, 17)},
  23: {0.99: (6, 18), 0.975: (7, 17), 0.95: (8, 16), 0.05: (8, 16), 0.025: (7, 17), 0.01: (6, 18)},
  24: {0.99: (7, 18), 0.975: (8, 17), 0.95: (9, 16), 0.05: (9, 16), 0.025: (8, 17), 0.01: (7, 18)},
  25: {0.99: (7, 19), 0.975: (8, 18), 0.95: (9, 17), 0.05: (9, 17), 0.025: (8, 18), 0.01: (7, 19)},
  26: {0.99: (8, 19), 0.975: (9, 18), 0.95: (10, 17), 0.05: (10, 17), 0.025: (9, 18), 0.01: (8, 19)},
  27: {0.99: (8, 20), 0.975: (9, 19), 0.95: (10, 18), 0.05: (10, 18), 0.025: (9, 19), 0.01: (8, 20)},
  28: {0.99: (9, 20), 0.975: (10, 19), 0.95: (11, 18), 0.05: (11, 18), 0.025: (10, 19), 0.01: (9, 20)},
  29: {0.99: (9, 21), 0.975: (10, 20), 0.95: (11, 19), 0.05: (11, 19), 0.025: (10, 20), 0.01: (9, 21)},
  30: {0.99: (10, 21), 0.975: (11, 20), 0.95: (12, 19), 0.05: (12, 19), 0.025: (11, 20), 0.01: (10, 21)},
  40: {0.99: (22, 58), 0.975: (24, 56), 0.95: (25, 55), 0.05: (25, 55), 0.025: (24, 56), 0.01: (22, 58)},
  45: {0.99: (27, 63), 0.975: (28, 62), 0.95: (29, 61), 0.05: (29, 61), 0.025: (28, 62), 0.01: (27, 63)},
  50: {0.99: (32, 68), 0.975: (40, 61), 0.95: (41, 60), 0.05: (41, 60), 0.025: (40, 61), 0.01: (32, 68)},
}


def find_series_critical_values(n, alpha):
  """
  Возвращает (lower, upper, chosen_half, key_low, key_high).
  lower — квантиль уровня 1 − α/2 (нижняя граница)
  upper — квантиль уровня α/2     (верхняя граница)
  """
  half_n = n // 2
  available = sorted(SERIES_CRITICAL_TABLE.keys())
  chosen = available[0]
  for key in available:
    if key <= half_n:
      chosen = key

  row = SERIES_CRITICAL_TABLE[chosen]
  alpha_keys = sorted(row.keys())

  target_low = 1.0 - alpha / 2.0    # например 0.975
  target_high = alpha / 2.0          # например 0.025

  # нижняя граница: наибольший ключ <= target_low
  key_low = alpha_keys[0]
  for a in alpha_keys:
    if a <= target_low:
      key_low = a

  # верхняя граница: наименьший ключ >= target_high
  key_high = alpha_keys[-1]
  for a in alpha_keys:
    if a >= target_high:
      key_high = a
      break

  lower = row[key_low][0]
  upper = row[key_high][1]
  return lower, upper, chosen, key_low, key_high


def series_test(data, alpha=0.05):
  n = len(data)
  print_header("КРИТЕРИЙ СЕРИЙ (проверка случайности последовательности)")

  print_subheader("ШАГ 1. Вариационный ряд и выборочная медиана")

  sorted_data = sorted(data)
  print("  Вариационный ряд: x_(1) ≤ x_(2) ≤ … ≤ x_(N)")
  print()
  columns = 5
  sep = "  +" + "-" * 8 + "+" + ("-" * 10 + "+") * columns
  print(sep)
  header = "  |{:^8}|".format("i")
  for j in range(columns):
    header += "{:^10}|".format(f"x({j + 1})")
  print(header)
  print(sep)
  rows = (n + columns - 1) // columns
  for row in range(rows):
    line = "  |{:^8}|".format(row * columns + 1)
    for col in range(columns):
      idx = row * columns + col
      if idx < n:
        line += "{:^10}|".format(fmt(sorted_data[idx], 4))
      else:
        line += "{:^10}|".format("")
    print(line)
  print(sep)
  print()

  left = sorted_data[n // 2 - 1]
  right = sorted_data[n // 2]
  median = 0.5 * (left + right)
  print(f"  N = {n} — чётное")
  print(f"  med = (x_(N/2) + x_(N/2+1)) / 2 = "
        f"({fmt(left, 6)} + {fmt(right, 6)}) / 2 = {fmt(median, 6)}")
  print()

  print_subheader("ШАГ 2. Последовательность знаков")

  signs = ["+" if v >= median else "−" for v in data]
  print("  Правило: u_i ≥ med → «+»; иначе → «−»")
  print()

  chunk_size = 50
  sep = "  +" + "-" * 12 + "+" + "-" * chunk_size + "+"
  print(sep)
  print("  |{:^12}|{:^50}|".format("i", "Знаки"))
  print(sep)
  for i in range(0, n, chunk_size):
    chunk = signs[i:i + chunk_size]
    label = f"{i + 1}–{i + len(chunk)}"
    print("  |{:^12}|{:^50}|".format(label, "".join(chunk)))
  print(sep)
  print(f"  «+»: {signs.count('+')},  «−»: {signs.count('−')}")
  print()

  print_subheader("ШАГ 3. Подсчёт числа серий")

  series_count = 1
  for i in range(1, n):
    if signs[i] != signs[i - 1]:
      series_count += 1

  print(f"  S = {series_count}")
  print()

  print_subheader("ШАГ 4. Критические значения распределения серий")

  lower, upper, chosen_half, key_low, key_high = find_series_critical_values(n, alpha)
  print(f"  N/2 = {chosen_half}")
  print(f"  S(N/2; {fmt(key_low, 4)}) = {lower}")
  print(f"  S(N/2; {fmt(key_high, 4)}) = {upper}")
  print()

  print_subheader("ШАГ 5. Проверка гипотезы")
  print(f"  Условие: {lower} < S < {upper}")
  print(f"  Проверка: {lower} < {series_count} < {upper}")
  print()
  if lower < series_count < upper:
    print("  Условие выполнено  →  гипотеза о случайности принимается.")
  else:
    print("  Условие НЕ выполнено  →  гипотеза о случайности отвергается.")
  print()
  print_line("=")
  print()


def laplace_z_value(alpha):
  """
  z_α из условия Ф(z_α) = (1 − α)/2.
  Используется таблица для типичных α и итерация для остальных.
  """
  table = {0.10: 1.6449, 0.05: 1.9600, 0.02: 2.3263, 0.01: 2.5758}
  if alpha in table:
    return table[alpha]

  target = (1.0 - alpha) / 2.0
  z = 1.96
  for _ in range(100):
    phi = 0.5 * (1.0 + math.erf(z / math.sqrt(2)))
    deriv = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    if deriv < 1e-15:
      break
    new_z = z - (phi - target) / deriv
    if abs(new_z - z) < 1e-12:
      return new_z
    z = new_z
  return z


def independence_test(data, alpha=0.05):
  n = len(data)
  print_header("ПРОВЕРКА НЕЗАВИСИМОСТИ (коэффициент корреляции r(x_i, i))")

  print_subheader("ШАГ 1. Промежуточные суммы")

  sum_i = n * (n + 1) / 2.0
  sum_xi = sum(data)
  sum_i_xi = sum((i + 1) * v for i, v in enumerate(data))
  sum_xi_sq = sum(v * v for v in data)

  print(f"  Σi       = N(N+1)/2 = {n}·{n + 1}/2 = {fmt(sum_i, 4)}")
  print(f"  Σu_i     = {fmt(sum_xi, 6)}")
  print(f"  Σi·u_i   = {fmt(sum_i_xi, 6)}")
  print(f"  Σu_i²    = {fmt(sum_xi_sq, 6)}")
  print()

  mean_i_xi = sum_i_xi / n
  mean_xi = sum_xi / n
  mean_xi_sq = sum_xi_sq / n
  mean_i = (n + 1) / 2.0

  print_subheader("ШАГ 2. Коэффициент корреляции r(x_i, i)")

  numerator = mean_i_xi - mean_xi * mean_i
  denom_part1 = mean_xi_sq - mean_xi ** 2
  denom_part2 = (n ** 2 - 1) / 12.0
  denominator = math.sqrt(denom_part1 * denom_part2)
  r = numerator / denominator

  print("  r = [ (1/N)Σi·u_i − (1/N)Σu_i·(N+1)/2 ] /")
  print("      √( [ (1/N)Σu_i² − ((1/N)Σu_i)² ] · (N²−1)/12 )")
  print()
  print(f"  Числитель: {fmt(numerator, 6)}")
  print(f"  Знаменатель: {fmt(denominator, 6)}")
  print(f"  r = {fmt(r, 6)}")
  print()

  print_subheader("ШАГ 3. Верхняя граница r_max")

  z_alpha = laplace_z_value(alpha)
  r_max = z_alpha * (1 - r ** 2) / math.sqrt(n)

  print(f"  Ф(z_α) = (1 − α)/2 = {fmt((1 - alpha) / 2, 4)}")
  print(f"  z_α = {fmt(z_alpha, 4)}")
  print(f"  r_max = z_α·(1 − r²)/√N = {fmt(r_max, 6)}")
  print()

  print_subheader("ШАГ 4. Проверка гипотезы")
  print(f"  |r| = {fmt(abs(r), 6)}")
  print(f"  r_max = {fmt(r_max, 6)}")
  print()
  if abs(r) <= r_max:
    print("  |r| ≤ r_max  →  гипотеза о независимости принимается.")
  else:
    print("  |r| > r_max  →  гипотеза о независимости отвергается.")
  print()
  print_line("=")
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

  chi_square_test(float_sequence, alpha)
  series_test(float_sequence, alpha)
  independence_test(float_sequence, alpha)


if __name__ == "__main__":
  main()
