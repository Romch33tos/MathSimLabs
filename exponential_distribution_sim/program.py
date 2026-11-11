import math
import random
from statistics import NormalDist


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


def build_open_intervals(x_min, x_max, k):
  h = (x_max - x_min) / k
  intervals = []
  for i in range(k):
    a = x_min + i * h
    b = x_min + (i + 1) * h
    if i == 0:
      a = -math.inf
    if i == k - 1:
      b = math.inf
    intervals.append((a, b))
  return intervals


def count_frequencies(data, intervals):
  freqs = []
  last = len(intervals) - 1
  for i, (a, b) in enumerate(intervals):
    if i == 0 and i == last:
      cnt = sum(1 for v in data if a < v <= b)
    elif i == 0:
      cnt = sum(1 for v in data if a < v <= b)
    elif i == last:
      cnt = sum(1 for v in data if a <= v < b)
    else:
      cnt = sum(1 for v in data if a <= v < b)
    freqs.append(cnt)
  return freqs


def laplace_phi(z):
  return 0.5 * math.erf(z / math.sqrt(2.0))


def normal_cdf(x, mean, sigma):
  return 0.5 + laplace_phi((x - mean) / sigma)


_CHI2_05 = {
  1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070,
  6: 12.592, 7: 14.067, 8: 15.507, 9: 16.919, 10: 18.307,
  11: 19.675, 12: 21.026, 13: 22.362, 14: 23.685, 15: 24.996,
  16: 26.296, 17: 27.587, 18: 28.869, 19: 30.144, 20: 31.410,
  21: 32.671, 22: 33.924, 23: 35.172, 24: 36.415, 25: 37.652,
  26: 38.885, 27: 40.113, 28: 41.337, 29: 42.557, 30: 43.773,
}


def chi2_critical(alpha, df):
  if alpha == 0.05 and df in _CHI2_05:
    return _CHI2_05[df]
  z_table = {0.10: 1.2816, 0.05: 1.6449, 0.025: 1.9600,
             0.01: 2.3263, 0.005: 2.5758, 0.001: 3.0902}
  z = z_table.get(alpha, 1.6449)
  term = 1 - 2.0 / (9 * df) + z * math.sqrt(2.0 / (9 * df))
  return df * term ** 3


def merge_small(intervals, emp, theo, min_freq=5):
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
          if emp[i - 1] <= emp[i + 1]:
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


def interval_str(a, b):
  left = "−∞" if a == -math.inf else fmt(a)
  right = "+∞" if b == math.inf else fmt(b)
  left_br = "(" if a == -math.inf else "["
  right_br = ")" if b == math.inf else "]"
  return f"{left_br}{left}; {right}{right_br}"


def print_freq_table(intervals, mids, emp, theo):
  sep = ("  +" + "-" * 4 + "+" + "-" * 22 + "+" + "-" * 14 + "+" +
         "-" * 8 + "+" + "-" * 12 + "+" + "-" * 20 + "+")
  print(sep)
  print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
    "№", "Интервал", "Середина x_i", "n_i", "n_i'", "(n_i−n_i')²/n_i'"))
  print(sep)
  s = len(intervals)
  chi2_obs = 0.0
  for i in range(s):
    ivl = interval_str(intervals[i][0], intervals[i][1])
    term = ((emp[i] - theo[i]) ** 2 / theo[i]) if theo[i] > 0 else 0.0
    chi2_obs += term
    mid = mids[i] if mids[i] is not None else "—"
    print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
      i + 1, ivl,
      fmt(mid, 6) if isinstance(mid, float) else mid,
      emp[i], fmt(theo[i], 4), fmt(term, 4)))
  print(sep)
  print("  |{:^4}|{:^22}|{:^14}|{:^8}|{:^12}|{:^20}|".format(
    "Σ", "", "", sum(emp), fmt(sum(theo), 4), fmt(chi2_obs, 4)))
  print(sep)
  print()
  return chi2_obs


def mids_from_intervals(intervals):
  mids = []
  for a, b in intervals:
    if a == -math.inf or b == math.inf:
      mids.append(None)
    else:
      mids.append((a + b) / 2.0)
  return mids


def model_exponential(n=100, lam=0.1, seed=42, alpha=0.05):
  print_header("ШАГ 1. МОДЕЛИРОВАНИЕ ЭКСПОНЕНЦИАЛЬНО РАСПРЕДЕЛЁННОЙ СВ")

  rng = random.Random(seed)
  data = [rng.expovariate(lam) for _ in range(n)]

  print_subheader("1.1. Исходные параметры")
  print(f"  N = {n}")
  print(f"  λ = {fmt(lam, 4)}")
  print(f"  seed = {seed}")
  print("  Стандартный генератор: random.expovariate(λ) (модуль random)")
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

  intervals = build_open_intervals(x_min, x_max, k)
  emp = count_frequencies(data, intervals)
  mids = mids_from_intervals(intervals)

  lam_hat = 1.0 / mean_emp
  print(f"  Оценка λ: λ* = 1/x̄ = {fmt(lam_hat, 6)}")
  print()

  def exp_cdf(x):
    if x == -math.inf:
      return 0.0
    if x == math.inf:
      return 1.0
    return 1.0 - math.exp(-lam_hat * x)

  theo = []
  probs = []
  for a, b in intervals:
    p = exp_cdf(b) - exp_cdf(a)
    probs.append(p)
    theo.append(n * p)

  print("  Вероятности по интервалам:")
  print("  " + "  ".join(fmt(p, 6) for p in probs))
  print(f"  Сумма теоретических вероятностей: Σp = {fmt(sum(probs), 6)}")
  print()

  print("  Таблица ДО объединения малочисленных частот:")
  print_freq_table(intervals, mids, emp, theo)

  intervals2, emp2, theo2 = merge_small(intervals, emp, theo, 5)
  mids2 = mids_from_intervals(intervals2)

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
    print("  χ²_набл < χ²_кр → гипотеза о показательном распределении принимается.")
  else:
    print("  χ²_набл > χ²_кр → гипотеза о показательном распределении отклоняется.")
  print()
  print_line("=")
  print()


def generate_clt(n, mean, sigma, seed):
  rng = random.Random(seed)
  data = []
  for _ in range(n):
    s = sum(rng.random() for _ in range(12))
    data.append(mean + sigma * (s - 6.0))
  return data


def generate_muller(n, mean, sigma, seed):
  rng = random.Random(seed)
  nd = NormalDist(mu=mean, sigma=sigma)
  return [nd.inv_cdf(rng.random()) for _ in range(n)]


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

  intervals = build_open_intervals(x_min, x_max, k)
  emp = count_frequencies(data, intervals)
  mids = mids_from_intervals(intervals)

  x_bar = sample_mean(data)
  s_hat = math.sqrt(sample_variance(data))
  print(f"  Оценка m: x̄ = {fmt(x_bar, 6)}")
  print(f"  Оценка σ: s = {fmt(s_hat, 6)}")
  print()

  def norm_cdf_emp(x):
    if x == -math.inf:
      return 0.0
    if x == math.inf:
      return 1.0
    return normal_cdf(x, x_bar, s_hat)

  theo = []
  probs = []
  for a, b in intervals:
    p = norm_cdf_emp(b) - norm_cdf_emp(a)
    probs.append(p)
    theo.append(n * p)

  print("  Вероятности по интервалам:")
  print("  " + "  ".join(fmt(p, 6) for p in probs))
  print(f"  Сумма теоретических вероятностей: Σp = {fmt(sum(probs), 6)}")
  print()

  print("  Таблица ДО объединения малочисленных частот:")
  print_freq_table(intervals, mids, emp, theo)

  intervals2, emp2, theo2 = merge_small(intervals, emp, theo, 5)
  mids2 = mids_from_intervals(intervals2)

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
    print("  χ²_набл < χ²_кр → гипотеза о нормальном распределении принимается.")
  else:
    print("  χ²_набл > χ²_кр → гипотеза о нормальном распределении отклоняется.")
  print()


def print_ks_normal(data, mean, sigma):
  n = len(data)
  print_subheader("Критерий Колмогорова–Смирнова (нормальное распределение)")

  x_bar = sample_mean(data)
  s_hat = math.sqrt(sample_variance(data))
  print(f"  Оценка m: x̄ = {fmt(x_bar, 6)}")
  print(f"  Оценка σ: s = {fmt(s_hat, 6)}")
  print()

  sorted_data = sorted(data)

  sep = ("  +" + "-" * 14 + "+" + "-" * 10 + "+" + "-" * 12 + "+" +
         "-" * 14 + "+" + "-" * 20 + "+")
  print(sep)
  print("  |{:^14}|{:^10}|{:^12}|{:^14}|{:^20}|".format(
    "x_(i)", "i", "F_n(x)", "F(x)", "|F_n(x) − F(x)|"))
  print(sep)

  d_max = 0.0
  for i, x in enumerate(sorted_data, start=1):
    fn = i / n
    fx = normal_cdf(x, x_bar, s_hat)
    d = abs(fn - fx)
    if d > d_max:
      d_max = d
    if i % 10 == 0 or i == n:
      print("  |{:^14}|{:^10}|{:^12}|{:^14}|{:^20}|".format(
        fmt(x, 4), i, fmt(fn, 4), fmt(fx, 4), fmt(d, 4)))
  print(sep)
  print()

  lam_ks = d_max * math.sqrt(n)
  lam_cr = 1.36
  print(f"  D_max = {fmt(d_max, 6)}")
  print(f"  λ = D_max·√N = {fmt(d_max, 6)}·√{n} = {fmt(lam_ks, 6)}")
  print(f"  λ_кр (α = 0.05) = {fmt(lam_cr, 4)}")
  print()
  if lam_ks < lam_cr:
    print("  λ < λ_кр → гипотеза H0 о нормальном распределении принимается.")
  else:
    print("  λ > λ_кр → гипотеза H0 о нормальном распределении отклоняется.")
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


def main():
  alpha = 0.05
  model_exponential(n=100, lam=0.1, seed=42, alpha=alpha)

  m = 3.0
  sigma = 0.25

  data_clt = generate_clt(100, m, sigma, seed=42)
  run_normal_block("ШАГ 2–3. МЕТОД ЦПТ: z = Σr_i − 6, x = m + σz",
                   data_clt, m, sigma, alpha)

  data_muller = generate_muller(100, m, sigma, seed=42)
  run_normal_block("ШАГ 2–3. МЕТОД ОБРАТНОЙ ФУНКЦИИ: statistics.NormalDist",
                   data_muller, m, sigma, alpha)


if __name__ == "__main__":
  main()
