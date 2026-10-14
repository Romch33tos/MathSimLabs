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
    print("  Формулы для расчета частот:")
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


if __name__ == "__main__":
    main()
