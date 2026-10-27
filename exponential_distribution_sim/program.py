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

# =========================================================
# ШАГ 1. ЭКСПОНЕНЦИАЛЬНОЕ РАСПРЕДЕЛЕНИЕ
# =========================================================

def model_exponential(n=100, lam=0.1, seed=42, alpha=0.05):
  print_header("ШАГ 1. МОДЕЛИРОВАНИЕ ЭКСПОНЕНЦИАЛЬНО РАСПРЕДЕЛЁННОЙ СВ")

  random.seed(seed)
  data = []
  for _ in range(n):
    r = random.random()
    while r == 0.0:
      r = random.random()
    x = -(1.0 / lam) * math.log(r)
    data.append(x)

  print_subheader("1.1. Исходные параметры")
  print(f"  N = {n}")
  print(f"  λ = {fmt(lam, 4)}")
  print(f"  seed = {seed}")
  print("  Формула метода обратной функции: x_i = −(1/λ)·ln(r_i) = −10·ln(r_i)")
  print()

  print_subheader("1.2. Все 100 смоделированных значений x_i")
  print_sequence_table("", data, is_float=True)

  mean_emp = sample_mean(data)
  var_emp = sample_variance(data)
  mean_theory = 1.0 / lam
  var_theory = 1.0 / (lam ** 2)

  print_subheader("1.3. Теоретические и выборочные характеристики")
  sep = "  +" + "-" * 26 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 18 + "+"
  print(sep)
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "Характеристика", "Теория", "Выборка", "Абс. погрешность"))
  print(sep)
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "Математическое ожидание", fmt(mean_theory, 4),
    fmt(mean_emp, 6), fmt(abs(mean_emp - mean_theory), 6)))
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "Дисперсия", fmt(var_theory, 4),
    fmt(var_emp, 6), fmt(abs(var_emp - var_theory), 6)))
  print(sep)
  print()

  print_subheader("1.4. Критерий Пирсона (показательное распределение)")
  k = sturges_k(n)
  print(f"  k = 1 + 3.3221·lg(N) = {fmt(1 + 3.3221 * math.log10(n), 4)} ≈ {k}")
  x_min = min(data)
  x_max = max(data)
  h = (x_max - x_min) / k
  print(f"  h = (x_max − x_min)/k = ({fmt(x_max, 4)} − {fmt(x_min, 4)})/{k} = {fmt(h, 6)}")
  print()

  intervals = build_intervals(x_min, x_max, k)
  emp = count_frequencies(data, intervals)
  mids = [(a + b) / 2.0 for a, b in intervals]

  lam_hat = 1.0 / mean_emp
  print(f"  Оценка λ: λ* = 1/x̄ = {fmt(lam_hat, 6)}")
  print()

  theo = []
  for a, b in intervals:
    p = math.exp(-lam_hat * a) - math.exp(-lam_hat * b)
    theo.append(n * p)

  # нормировка теоретических частот на n
  scale = n / sum(theo)
  theo = [t * scale for t in theo]

  print("  Таблица ДО объединения малочисленных частот:")
  print_freq_table(intervals, mids, emp, theo)

  intervals2, emp2, theo2 = merge_small(intervals, emp, theo, 5)
  mids2 = [(a + b) / 2.0 for a, b in intervals2]

  print("  Таблица ПОСЛЕ объединения малочисленных частот:")
  chi2_obs = print_freq_table(intervals2, mids2, emp2, theo2)

  df = len(intervals2) - 2
  chi2_cr = chi2_critical(alpha, df)
  print(f"  Число степеней свободы: k − 2 = {len(intervals2)} − 2 = {df}")
  print(f"  α = {alpha}")
  print(f"  χ²_кр(α; {df}) = {fmt(chi2_cr, 4)}")
  print(f"  χ²_набл = {fmt(chi2_obs, 4)}")
  print()
  if chi2_obs < chi2_cr:
    print("  χ²_набл < χ²_кр → гипотеза о показательном распределении НЕ отвергается.")
  else:
    print("  χ²_набл > χ²_кр → гипотеза о показательном распределении ОТВЕРГАЕТСЯ.")
  print()
  print_line("=")
  print()

# =========================================================
# ШАГ 2–3. НОРМАЛЬНОЕ РАСПРЕДЕЛЕНИЕ
# =========================================================

def generate_clt(n, mean, sigma, seed):
  random.seed(seed)
  data = []
  for _ in range(n):
    s = sum(random.random() for _ in range(12))
    z = s - 6.0
    data.append(mean + sigma * z)
  return data


def generate_muller(n, mean, sigma, seed):
  random.seed(seed)
  data = []
  for _ in range(n):
    r1 = random.random()
    while r1 == 0.0:
      r1 = random.random()
    r2 = random.random()
    z = math.sqrt(-2.0 * math.log(r1)) * math.cos(2.0 * math.pi * r2)
    data.append(mean + sigma * z)
  return data

def print_normal_estimates(data, mean, sigma):
  n = len(data)
  x_bar = sample_mean(data)
  s = math.sqrt(sample_variance(data))
  print_subheader("Оценки и абсолютные погрешности")
  sep = "  +" + "-" * 26 + "+" + "-" * 14 + "+" + "-" * 14 + "+" + "-" * 18 + "+"
  print(sep)
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "Характеристика", "Теория", "Выборка", "Абс. погрешность"))
  print(sep)
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "Среднее m", fmt(mean, 4), fmt(x_bar, 6), fmt(abs(x_bar - mean), 6)))
  print("  |{:^26}|{:^14}|{:^14}|{:^18}|".format(
    "СКО σ", fmt(sigma, 4), fmt(s, 6), fmt(abs(s - sigma), 6)))
  print(sep)
  print()


def print_pearson_normal(data, mean, sigma, alpha=0.05):
  n = len(data)
  print_subheader("Критерий Пирсона (нормальное распределение)")
  k = sturges_k(n)
  x_min = min(data)
  x_max = max(data)
  h = (x_max - x_min) / k
  print(f"  k = 1 + 3.3221·lg(N) = {fmt(1 + 3.3221 * math.log10(n), 4)} ≈ {k}")
  print(f"  h = (x_max − x_min)/k = {fmt(h, 6)}")
  print()

  intervals = build_intervals(x_min, x_max, k)
  emp = count_frequencies(data, intervals)
  mids = [(a + b) / 2.0 for a, b in intervals]
  x_bar_mid = sum(ni * mi for ni, mi in zip(emp, mids)) / n
  print(f"  x̄ по серединам интервалов = {fmt(x_bar_mid, 6)}")
  print()

  theo = []
  for a, b in intervals:
    z1 = (a - x_bar_mid) / sigma
    z2 = (b - x_bar_mid) / sigma
    p = normal_cdf(z2, 0.0, 1.0) - normal_cdf(z1, 0.0, 1.0)
    theo.append(n * p)

  scale = n / sum(theo)
  theo = [t * scale for t in theo]

  print("  Таблица ДО объединения малочисленных частот:")
  print_freq_table(intervals, mids, emp, theo)

  intervals2, emp2, theo2 = merge_small(intervals, emp, theo, 5)
  mids2 = [(a + b) / 2.0 for a, b in intervals2]

  print("  Таблица ПОСЛЕ объединения малочисленных частот:")
  chi2_obs = print_freq_table(intervals2, mids2, emp2, theo2)

  df = len(intervals2) - 3
  if df < 1:
    df = 1
  chi2_cr = chi2_critical(alpha, df)
  print(f"  Число степеней свободы: k − 3 = {len(intervals2)} − 3 = {df}")
  print(f"  α = {alpha}")
  print(f"  χ²_кр(α; {df}) = {fmt(chi2_cr, 4)}")
  print(f"  χ²_набл = {fmt(chi2_obs, 4)}")
  print()
  if chi2_obs < chi2_cr:
    print("  χ²_набл < χ²_кр → гипотеза о нормальном распределении НЕ отвергается.")
  else:
    print("  χ²_набл > χ²_кр → гипотеза о нормальном распределении ОТВЕРГАЕТСЯ.")
  print()

def print_ks_normal(data, mean, sigma):
  n = len(data)
  print_subheader("Критерий Колмогорова–Смирнова (нормальное распределение)")
  k = sturges_k(n)
  x_min = min(data)
  x_max = max(data)
  intervals = build_intervals(x_min, x_max, k)
  emp = count_frequencies(data, intervals)
  mids = [(a + b) / 2.0 for a, b in intervals]
  x_bar_mid = sum(ni * mi for ni, mi in zip(emp, mids)) / n
  print(f"  x̄ по серединам = {fmt(x_bar_mid, 6)}")
  print()

  sep = ("  +" + "-" * 14 + "+" + "-" * 6 + "+" + "-" * 10 + "+" +
         "-" * 12 + "+" + "-" * 14 + "+" + "-" * 20 + "+")
  print(sep)
  print("  |{:^14}|{:^6}|{:^10}|{:^12}|{:^14}|{:^20}|".format(
    "x_i (сер.)", "n_i", "n_нак", "F_n(x)", "F(x)", "|F_n(x) − F(x)|"))
  print(sep)

  cum = 0
  d_max = 0.0
  for i in range(len(intervals)):
    cum += emp[i]
    fn = cum / n
    fx = normal_cdf(mids[i], x_bar_mid, sigma)
    d = abs(fn - fx)
    if d > d_max:
      d_max = d
    print("  |{:^14}|{:^6}|{:^10}|{:^12}|{:^14}|{:^20}|".format(
      fmt(mids[i], 4), emp[i], cum, fmt(fn, 4), fmt(fx, 4), fmt(d, 4)))
  print(sep)
  print()

  lam_ks = d_max * math.sqrt(n)
  lam_cr = 1.36
  print(f"  D_max = {fmt(d_max, 6)}")
  print(f"  λ = D_max·√N = {fmt(d_max, 6)}·√{n} = {fmt(lam_ks, 6)}")
  print(f"  λ_кр (α = 0.05) = {fmt(lam_cr, 4)}")
  print()
  if lam_ks < lam_cr:
    print("  λ < λ_кр → гипотеза H0 о нормальном распределении НЕ противоречит данным.")
  else:
    print("  λ > λ_кр → гипотеза H0 о нормальном распределении ОТВЕРГАЕТСЯ.")
  print()


def run_normal_block(title, data, mean, sigma, alpha=0.05):
  print_header(title)
  print_subheader("Все 100 смоделированных значений x_j")
  print_sequence_table("", data, is_float=True)
  print_normal_estimates(data, mean, sigma)
  print_pearson_normal(data, mean, sigma, alpha)
  print_ks_normal(data, mean, sigma)
  print_line("=")
  print()
