import math

# ============================================================
# ГЕНЕРАЦИЯ ПОСЛЕДОВАТЕЛЬНОСТИ ПСЕВДОСЛУЧАЙНЫХ ЧИСЕЛ
# ============================================================

def generate_random_sequence(seed, a, b, m, count):
  """Генерация последовательности ПСЧ линейным конгруэнтным методом.
  Затравка seed НЕ входит в результат — первым элементом идёт x1."""
  sequence = []
  x = seed
  for i in range(count):
    x = (a * x + b) % m   # сначала вычисляем x_{i+1}
    sequence.append(x)    # затем записываем его в последовательность
  return sequence


def print_sequence(title, seq):
  """Вывод последовательности в консоль."""
  print(title)
  for i in range(0, len(seq), 10):
    chunk = seq[i:i+10]
    print("  " + " ".join(f"{v:>6}" for v in chunk))
  print()


# ============================================================
# КРИТЕРИЙ ХИ-КВАДРАТ ПИРСОНА (ПРОВЕРКА РАВНОМЕРНОСТИ)
# ============================================================

def sturges_interval_length(x_max, x_min, n):
  """Длина интервала по формуле Стерджерса."""
  return (x_max - x_min) / (1 + 3.3221 * math.log10(n))


def build_intervals(data, h):
  """Разбиение данных на интервалы и подсчёт частот."""
  x_min = min(data)
  x_max = max(data)
  num_intervals = int(math.ceil((x_max - x_min) / h))
  if num_intervals < 4:
    num_intervals = 4

  intervals = []
  frequencies = []
  start = x_min
  for i in range(num_intervals):
    end = start + h
    if i == num_intervals - 1:
      count = sum(1 for v in data if start <= v <= end)
    else:
      count = sum(1 for v in data if start <= v < end)
    intervals.append((start, end))
    frequencies.append(count)
    start = end
  return intervals, frequencies


def print_intervals(intervals, frequencies, data):
  """Наглядный вывод интервалов и чисел, попавших в них."""
  print("РАЗБИЕНИЕ НА ИНТЕРВАЛЫ (содержимое интервалов):")
  for i, (start, end) in enumerate(intervals):
    numbers_in = [v for v in data if start <= v < end]
    if i == len(intervals) - 1:
      numbers_in = [v for v in data if start <= v <= end]
    preview = numbers_in[:8]
    suffix = "..." if len(numbers_in) > 8 else ""
    print(f"  Интервал {i+1}: [{start:8.2f}; {end:8.2f})  n={frequencies[i]:>3}  "
          f"числа: {preview}{suffix}")
  print()


def chi_square_test(data, alpha=0.05):
  """Проверка гипотезы о равномерном распределении по критерию Пирсона."""
  n = len(data)
  print("=" * 60)
  print("КРИТЕРИЙ ХИ-КВАДРАТ ПИРСОНА")
  print("=" * 60)

  mean = sum(data) / n
  variance = sum((x - mean) ** 2 for x in data) / n
  sigma = math.sqrt(variance)
  a_est = mean - math.sqrt(3) * sigma
  b_est = mean + math.sqrt(3) * sigma

  print(f"Выборочное среднее x̄    = {mean:.4f}")
  print(f"Выборочная дисперсия D  = {variance:.4f}")
  print(f"Стандартное отклонение σ = {sigma:.4f}")
  print(f"Оценка a* = x̄ - √3·σ    = {a_est:.4f}")
  print(f"Оценка b* = x̄ + √3·σ    = {b_est:.4f}")

  density = 1.0 / (b_est - a_est)
  print(f"Плотность f(x) = 1/(b*-a*) = {density:.6f}")
  print()

  x_min = min(data)
  x_max = max(data)
  h = sturges_interval_length(x_max, x_min, n)
  print(f"Длина интервала h (Стерджерс) = {h:.4f}")

  intervals, frequencies = build_intervals(data, h)
  print_intervals(intervals, frequencies, data)

  k = len(intervals)

  merged_intervals = []
  merged_frequencies = []
  buffer_start = None
  buffer_count = 0

  for i in range(k):
    if buffer_start is None:
      buffer_start = intervals[i][0]
    buffer_count += frequencies[i]
    if buffer_count >= 5:
      merged_intervals.append((buffer_start, intervals[i][1]))
      merged_frequencies.append(buffer_count)
      buffer_start = None
      buffer_count = 0

  if buffer_count > 0:
    if merged_intervals:
      prev_start = merged_intervals[-1][0]
      merged_intervals[-1] = (prev_start, intervals[-1][1])
      merged_frequencies[-1] += buffer_count
    else:
      merged_intervals.append((buffer_start, intervals[-1][1]))
      merged_frequencies.append(buffer_count)

  s = len(merged_intervals)
  print(f"После объединения малочисленных частот: s = {s} интервалов")
  for i, (start, end) in enumerate(merged_intervals):
    print(f"  [{start:8.2f}; {end:8.2f})  n = {merged_frequencies[i]}")
  print()

  theoretical = []
  for i in range(s):
    start, end = merged_intervals[i]
    left = max(start, a_est)
    right = min(end, b_est)
    if right < left:
      right = left
    p = (right - left) / (b_est - a_est)
    theoretical.append(n * p)

  print("ТЕОРЕТИЧЕСКИЕ ЧАСТОТЫ:")
  for i in range(s):
    print(f"  Интервал {i+1}: n' = {theoretical[i]:.4f}")
  print()

  chi_square = 0.0
  print("РАСЧЁТ СТАТИСТИКИ χ²:")
  for i in range(s):
    if theoretical[i] > 0:
      term = (merged_frequencies[i] - theoretical[i]) ** 2 / theoretical[i]
      chi_square += term
      print(f"  ({merged_frequencies[i]} - {theoretical[i]:.3f})² / {theoretical[i]:.3f} = {term:.4f}")
  print(f"\nχ²_набл = {chi_square:.4f}")

  degrees = s - 3
  if degrees < 1:
    degrees = 1
  chi_critical = get_chi_square_critical(degrees, alpha)
  print(f"Число степеней свободы k = s - 3 = {degrees}")
  print(f"Критическая точка χ²_кр({alpha}; {degrees}) ≈ {chi_critical}")

  if chi_square < chi_critical:
    print("ВЫВОД: χ²_набл < χ²_кр — нет оснований отвергнуть гипотезу о равномерном распределении.")
  else:
    print("ВЫВОД: χ²_набл > χ²_кр — гипотеза о равномерном распределении отвергается.")
  print()
  return chi_square < chi_critical


def get_chi_square_critical(degrees, alpha):
  """Приближённые критические значения χ² для уровня значимости 0.05."""
  table = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070,
    6: 12.592, 7: 14.067, 8: 15.507, 9: 16.919, 10: 18.307,
    11: 19.675, 12: 21.026, 13: 22.362, 14: 23.685, 15: 24.996,
    16: 26.296, 17: 27.587, 18: 28.869, 19: 30.144, 20: 31.410,
    21: 32.671, 22: 33.924, 23: 35.172, 24: 36.415, 25: 37.652,
    26: 38.885, 27: 40.113, 28: 41.337, 29: 42.557, 30: 43.773
  }
  if degrees in table:
    return table[degrees]
  return degrees + 1.645 * math.sqrt(2 * degrees)


# ============================================================
# КРИТЕРИЙ СЕРИЙ (ПРОВЕРКА СЛУЧАЙНОСТИ)
# ============================================================

def median_test(data, alpha=0.05):
  """Проверка случайности последовательности по критерию серий."""
  n = len(data)
  print("=" * 60)
  print("КРИТЕРИЙ СЕРИЙ (проверка случайности)")
  print("=" * 60)

  sorted_data = sorted(data)
  if n % 2 == 1:
    median = sorted_data[n // 2]
  else:
    median = 0.5 * (sorted_data[n // 2 - 1] + sorted_data[n // 2])
  print(f"Объём выборки N = {n}")
  print(f"Медиана med(N) = {median:.4f}")
  print()

  signs = []
  for x in data:
    if x >= median:
      signs.append("+")
    else:
      signs.append("-")

  print("Последовательность знаков:")
  for i in range(0, len(signs), 40):
    print("  " + "".join(signs[i:i+40]))
  print()

  num_series = 1
  for i in range(1, n):
    if signs[i] != signs[i-1]:
      num_series += 1
  print(f"Число серий S = {num_series}")

  mean_series = n / 2 + 1
  std_series = math.sqrt(n - 1) / 2
  z = get_z_critical(alpha)
  lower = mean_series - z * std_series
  upper = mean_series + z * std_series
  print(f"Математическое ожидание S: {mean_series:.2f}")
  print(f"СКО σ(S) = √(N-1)/2 = {std_series:.4f}")
  print(f"Критические границы: [{lower:.2f}; {upper:.2f}]")

  if lower < num_series < upper:
    print("ВЫВОД: число серий в допустимых границах — гипотеза о случайности принимается.")
  else:
    print("ВЫВОД: число серий выходит за критические границы — гипотеза о случайности отвергается.")
  print()
  return lower < num_series < upper


def get_z_critical(alpha):
  """Квантиль нормального распределения для двусторонней критической области."""
  if alpha == 0.10:
    return 1.645
  elif alpha == 0.05:
    return 1.960
  elif alpha == 0.02:
    return 2.326
  elif alpha == 0.01:
    return 2.576
  else:
    return 1.960


# ============================================================
# ПРОВЕРКА НЕЗАВИСИМОСТИ (КОЭФФИЦИЕНТ КОРРЕЛЯЦИИ)
# ============================================================

def correlation_test(data, alpha=0.05):
  """Проверка независимости через коэффициент корреляции r(x_i, i)."""
  n = len(data)
  print("=" * 60)
  print("ПРОВЕРКА НЕЗАВИСИМОСТИ (коэффициент корреляции)")
  print("=" * 60)

  sum_i_xi = 0.0
  sum_xi = 0.0
  sum_xi_sq = 0.0
  for i in range(n):
    idx = i + 1
    sum_i_xi += idx * data[i]
    sum_xi += data[i]
    sum_xi_sq += data[i] ** 2

  mean_i_xi = sum_i_xi / n
  mean_xi = sum_xi / n
  mean_xi_sq = sum_xi_sq / n

  numerator = mean_i_xi - mean_xi * (n + 1) / 2
  denominator = math.sqrt((mean_xi_sq - mean_xi ** 2) * (1.0 / 12.0) * (n ** 2 - 1))

  if denominator == 0:
    r = 0.0
  else:
    r = numerator / denominator

  print(f"Коэффициент корреляции r(x_i, i) = {r:.6f}")

  z = get_z_critical(alpha)
  r_max = z * (1 - r ** 2) / math.sqrt(n)
  print(f"Z_α (при α={alpha}) = {z}")
  print(f"r_max = Z_α · (1 - r²) / √N = {r_max:.6f}")

  if abs(r) < abs(r_max):
    print("ВЫВОД: |r| < r_max — гипотеза о независимости принимается.")
  else:
    print("ВЫВОД: |r| ≥ r_max — имеет место корреляционная связь.")
  print()
  return abs(r) < abs(r_max)


# ============================================================
# ГЛАВНАЯ ПРОГРАММА
# ============================================================

def main():
  print("=" * 60)
  print("ЛАБОРАТОРНАЯ РАБОТА: ПРОВЕРКА КАЧЕСТВА ГЕНЕРАТОРА ПСЧ")
  print("=" * 60)
  print()

  m = 1000
  a = 37
  b = 1
  seed = 38
  n = 100
  alpha = 0.05

  print("ПАРАМЕТРЫ ГЕНЕРАТОРА:")
  print(f"  M = {m}")
  print(f"  a = {a}")
  print(f"  b = {b}")
  print(f"  x0 (затравка, НЕ входит в выборку) = {seed}")
  print(f"  N (количество чисел) = {n}")
  print(f"  α (уровень значимости) = {alpha}")
  print()

  int_sequence = generate_random_sequence(seed, a, b, m, n)
  print_sequence("СГЕНЕРИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ x_i (начиная с x1):", int_sequence)

  float_sequence = [x / m for x in int_sequence]
  print_sequence("НОРМИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ u_i = x_i / M:", float_sequence)

  chi_square_test(float_sequence, alpha)
  median_test(float_sequence, alpha)
  correlation_test(float_sequence, alpha)

  print("=" * 60)
  print("РАБОТА ЗАВЕРШЕНА")
  print("=" * 60)


if __name__ == "__main__":
  main()
