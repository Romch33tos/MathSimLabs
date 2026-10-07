import math


def generate_random_sequence(seed, a, b, m, count):
    sequence = []
    x = seed
    for _ in range(count):
        x = (a * x + b) % m
        sequence.append(x)
    return sequence


def print_sequence(title, seq):
    print(title)
    for i in range(0, len(seq), 10):
        chunk = seq[i:i + 10]
        print(" " + " ".join(f"{v:>6.3f}" if isinstance(v, float) else f"{v:>6}" for v in chunk))
    print()


def sturges_interval_length(x_max, x_min, n):
    return (x_max - x_min) / (1 + 3.3221 * math.log10(n))


def build_intervals(data, h):
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
    print("РАЗБИЕНИЕ НА ИНТЕРВАЛЫ:")
    for i, (start, end) in enumerate(intervals):
        numbers_in = [v for v in data if start <= v < end]
        if i == len(intervals) - 1:
            numbers_in = [v for v in data if start <= v <= end]
        preview = [round(num, 4) for num in numbers_in]
        bracket = "]" if i == len(intervals) - 1 else ")"
        print(f" Интервал {i + 1}: [{start:6.4f}; {end:6.4f}{bracket}  "
              f"n ={frequencies[i]:>3} числа: {preview}")
    print()


# ---------- χ² Пирсона ----------

def merge_small_frequencies(intervals, frequencies, min_freq=5):
    """Объединяем интервалы, у которых n_i < 5 (замечание из методички)."""
    merged_intervals = []
    merged_freqs = []

    cur_start = intervals[0][0]
    cur_end = intervals[0][1]
    cur_freq = frequencies[0]

    for i in range(1, len(intervals)):
        if cur_freq < min_freq:
            cur_end = intervals[i][1]
            cur_freq += frequencies[i]
        else:
            merged_intervals.append((cur_start, cur_end))
            merged_freqs.append(cur_freq)
            cur_start, cur_end = intervals[i]
            cur_freq = frequencies[i]

    # Последний накопитель
    if merged_freqs and cur_freq < min_freq:
        s, _ = merged_intervals[-1]
        merged_intervals[-1] = (s, cur_end)
        merged_freqs[-1] += cur_freq
    else:
        merged_intervals.append((cur_start, cur_end))
        merged_freqs.append(cur_freq)

    return merged_intervals, merged_freqs


def chi2_critical(alpha, df):
    """
    Критическая точка χ² для правосторонней области.
    Приближение Уилсона–Хилферти (не требует таблиц).
    """
    z_table = {
        0.10: 1.2816, 0.05: 1.6449, 0.025: 1.9600,
        0.01: 2.3263, 0.005: 2.5758, 0.001: 3.0902,
    }
    z = z_table.get(alpha, 1.6449)
    term = 1 - 2.0 / (9 * df) + z * math.sqrt(2.0 / (9 * df))
    return df * term ** 3


def chi_square_test(data, alpha=0.05):
    n = len(data)
    print("=" * 60)
    print("КРИТЕРИЙ ХИ-КВАДРАТ ПИРСОНА")
    print("=" * 60)

    # --- 1. Оценки параметров равномерного распределения ---
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    sigma = math.sqrt(variance)
    a_est = mean - math.sqrt(3) * sigma
    b_est = mean + math.sqrt(3) * sigma
    density = 1.0 / (b_est - a_est)

    print(f"Выборочное среднее x̄ = {mean:.4f}")
    print(f"Выборочная дисперсия D = {variance:.4f}")
    print(f"Стандартное отклонение σ = {sigma:.4f}")
    print(f"Оценка a* = x̄ - √3·σ = {a_est:.4f}")
    print(f"Оценка b* = x̄ + √3·σ = {b_est:.4f}")
    print(f"Плотность f(x) = 1/(b*-a*) = {density:.6f}")
    print()

    # --- 2. Разбиение на интервалы (Стерджерс) ---
    x_min = min(data)
    x_max = max(data)
    h = sturges_interval_length(x_max, x_min, n)
    intervals, frequencies = build_intervals(data, h)

    print(f"Длина интервала h = {h:.4f}")
    print(f"Число интервалов до объединения s = {len(intervals)}")
    print()

    # --- 3. Объединяем малочисленные частоты (n_i < 5) ---
    intervals, frequencies = merge_small_frequencies(intervals, frequencies, min_freq=5)
    s = len(intervals)
    print(f"Число интервалов после объединения s = {s}")
    for i, (start, end) in enumerate(intervals):
        print(f"  Интервал {i + 1}: [{start:.4f}; {end:.4f}]  n_i = {frequencies[i]}")
    print()

    # --- 4. Теоретические частоты (для ОБЪЕДИНЁННЫХ интервалов) ---
    # Через пересечение интервала с [a*, b*] — корректно при любой ширине.
    n_i_theor = []
    for (start, end) in intervals:
        left = max(start, a_est)
        right = min(end, b_est)
        if right <= left:
            p = 0.0
        else:
            p = (right - left) / (b_est - a_est)
        n_i_theor.append(n * p)

    print("ТЕОРЕТИЧЕСКИЕ ЧАСТОТЫ:")
    for i in range(s):
        print(f"  n_{i + 1}' = {n_i_theor[i]:.4f}")
    print()

    # --- 5. Статистика χ² ---
    chi2_obs = 0.0
    print("РАСЧЁТ χ²:")
    header = "  {:>3} {:>6} {:>10} {:>20}".format("i", "n_i", "n_i'", "(n_i-n_i')^2/n_i'")
    print(header)
    for i in range(s):
        diff = frequencies[i] - n_i_theor[i]
        term = (diff ** 2) / n_i_theor[i] if n_i_theor[i] > 0 else 0.0
        chi2_obs += term
        print(f"  {i + 1:>3} {frequencies[i]:>6} {n_i_theor[i]:>10.4f} {term:>20.4f}")
    print(f"\n  χ²_набл = {chi2_obs:.4f}")

    # --- 6. Критическое значение ---
    df = s - 3
    if df < 1:
        df = 1
    chi2_cr = chi2_critical(alpha, df)
    print(f"  Число степеней свободы k = s - 3 = {df}")
    print(f"  α = {alpha}")
    print(f"  χ²_кр(α; k) = {chi2_cr:.4f}")
    print()

    # --- 7. Вывод ---
    if chi2_obs < chi2_cr:
        print("ВЫВОД: χ²_набл < χ²_кр — НЕТ оснований отвергнуть гипотезу")
        print("        о равномерном распределении генеральной совокупности.")
    else:
        print("ВЫВОД: χ²_набл > χ²_кр — гипотеза о равномерном распределении")
        print("        ОТВЕРГАЕТСЯ.")
    print("=" * 60)


def main():
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
    print(f"  x0 (затравка) = {seed}")
    print(f"  N (количество чисел) = {n}")
    print(f"  α (уровень значимости) = {alpha}")
    print()

    int_sequence = generate_random_sequence(seed, a, b, m, n)
    print_sequence("СГЕНЕРИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ x_i (начиная с x1):", int_sequence)

    float_sequence = [x / m for x in int_sequence]
    print_sequence("НОРМИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ u_i = x_i / M:", float_sequence)

    x_min = min(float_sequence)
    x_max = max(float_sequence)
    h = sturges_interval_length(x_max, x_min, n)
    intervals, frequencies = build_intervals(float_sequence, h)

    print(f"Длина интервала (h) = {h}")
    print_intervals(intervals, frequencies, float_sequence)

    chi_square_test(float_sequence, alpha)


if __name__ == "__main__":
    main()
