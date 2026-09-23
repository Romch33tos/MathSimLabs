import math
import numpy as np
from scipy import stats


# ============================================================
# ЧАСТЬ 0. ГЕНЕРАЦИЯ ПОСЛЕДОВАТЕЛЬНОСТИ ПСЧ
# ============================================================

def generate_pseudo_random_sequence(multiplier, increment, modulus, seed, count):
    """
    Линейный конгруэнтный генератор:
        next_value = (multiplier * current_value + increment) mod modulus

    Возвращает:
        raw_values      — список целых x_i
        normalized_values — список u_i = x_i / modulus в [0, 1)
    """
    raw_values = []
    current_value = seed

    for _ in range(count):
        raw_values.append(current_value)
        current_value = (multiplier * current_value + increment) % modulus

    normalized_values = [value / modulus for value in raw_values]
    return raw_values, normalized_values


# --- Параметры генератора ---
MODULUS = 9973          # M — простое число
MULTIPLIER = 101        # a — простое, a mod 8 = 5
INCREMENT = 97          # b — того же порядка, что a
SEED = 38               # x0 — затравка
SAMPLE_SIZE = 100       # N — количество чисел

raw_values, normalized_values = generate_pseudo_random_sequence(
    multiplier=MULTIPLIER,
    increment=INCREMENT,
    modulus=MODULUS,
    seed=SEED,
    count=SAMPLE_SIZE
)

print("=" * 60)
print("ЧАСТЬ 0. Сгенерированная последовательность")
print("=" * 60)
print(f"Параметры: M = {MODULUS}, a = {MULTIPLIER}, b = {INCREMENT}, x0 = {SEED}")
print("Первые 10 x_i:", raw_values[:10])
print("Первые 10 u_i:", [round(v, 4) for v in normalized_values[:10]])
print(f"x_min = {min(raw_values)}, x_max = {max(raw_values)}")


# ============================================================
# ЧАСТЬ А. КРИТЕРИЙ χ² ПИРСОНА (проверка равномерности)
# ============================================================

print("\n" + "=" * 60)
print("ЧАСТЬ А. Критерий χ² Пирсона")
print("=" * 60)

SIGNIFICANCE_LEVEL = 0.05
sample_size = len(raw_values)

# --- 1. Определяем число и длину интервалов по формуле Стерджерса ---
min_value = min(raw_values)
max_value = max(raw_values)
value_range = max_value - min_value

interval_width = value_range / (1 + 3.3221 * math.log10(sample_size))
interval_count = int(math.ceil(value_range / interval_width))

print(f"Длина интервала h = {interval_width:.4f}, число интервалов k = {interval_count}")

# --- 2. Строим границы интервалов и считаем эмпирические частоты ---
interval_edges = [min_value + i * interval_width for i in range(interval_count + 1)]
interval_edges[-1] = max_value + 1e-9  # чтобы включить максимальное значение

empirical_frequencies = [0] * interval_count
for value in raw_values:
    for i in range(interval_count):
        if interval_edges[i] <= value < interval_edges[i + 1]:
            empirical_frequencies[i] += 1
            break

print("Интервалы и эмпирические частоты:")
for i in range(interval_count):
    print(f"  [{interval_edges[i]:.2f}, {interval_edges[i+1]:.2f}): "
          f"n_{i+1} = {empirical_frequencies[i]}")

# --- 3. Оценки параметров a* и b* равномерного распределения ---
sample_mean = np.mean(raw_values)
sample_std = np.std(raw_values, ddof=1)

estimated_lower_bound = sample_mean - math.sqrt(3) * sample_std
estimated_upper_bound = sample_mean + math.sqrt(3) * sample_std

print(f"\nОценки: a* = {estimated_lower_bound:.4f}, b* = {estimated_upper_bound:.4f}")

# --- 4. Теоретические частоты для каждого интервала ---
theoretical_frequencies = [0.0] * interval_count
for i in range(interval_count):
    left_edge = max(interval_edges[i], estimated_lower_bound)
    right_edge = min(interval_edges[i + 1], estimated_upper_bound)
    overlap_width = max(0.0, right_edge - left_edge)
    theoretical_frequencies[i] = (
        sample_size * overlap_width / (estimated_upper_bound - estimated_lower_bound)
    )

print("\nТеоретические частоты n_i':")
for i in range(interval_count):
    print(f"  n'_{i+1} = {theoretical_frequencies[i]:.3f}")

# --- 5. Объединяем малочисленные интервалы (n_i < 5) ---
MIN_EXPECTED_FREQUENCY = 5

merged_empirical = []
merged_theoretical = []
i = 0
while i < interval_count:
    empirical_sum = empirical_frequencies[i]
    theoretical_sum = theoretical_frequencies[i]
    j = i
    while empirical_sum < MIN_EXPECTED_FREQUENCY and j + 1 < interval_count:
        j += 1
        empirical_sum += empirical_frequencies[j]
        theoretical_sum += theoretical_frequencies[j]
    merged_empirical.append(empirical_sum)
    merged_theoretical.append(theoretical_sum)
    i = j + 1

group_count = len(merged_empirical)
print(f"\nПосле объединения: число групп s = {group_count}")

# --- 6. Статистика χ² ---
chi_squared_observed = sum(
    (empirical - theoretical) ** 2 / theoretical
    for empirical, theoretical in zip(merged_empirical, merged_theoretical)
    if theoretical > 0
)
degrees_of_freedom = group_count - 3
print(f"χ²_набл = {chi_squared_observed:.4f}, "
      f"число степеней свободы = {degrees_of_freedom}")

# --- 7. Сравнение с критическим значением ---
if degrees_of_freedom > 0:
    chi_squared_critical = stats.chi2.ppf(1 - SIGNIFICANCE_LEVEL, degrees_of_freedom)
    print(f"χ²_кр(α={SIGNIFICANCE_LEVEL}; df={degrees_of_freedom}) = "
          f"{chi_squared_critical:.4f}")

    if chi_squared_observed < chi_squared_critical:
        print(">>> Гипотеза о равномерном распределении НЕ отвергается.")
    else:
        print(">>> Гипотеза о равномерном распределении ОТВЕРГАЕТСЯ.")
else:
    print(">>> Недостаточно степеней свободы — увеличьте выборку.")


# ============================================================
# ЧАСТЬ Б. КРИТЕРИЙ СЕРИЙ (проверка случайности)
# ============================================================

print("\n" + "=" * 60)
print("ЧАСТЬ Б. Критерий серий")
print("=" * 60)

# --- 1. Вариационный ряд и медиана ---
sorted_values = sorted(raw_values)
total_count = len(sorted_values)

if total_count % 2 == 1:
    median_value = sorted_values[(total_count + 1) // 2 - 1]
else:
    median_value = 0.5 * (
        sorted_values[total_count // 2 - 1] + sorted_values[total_count // 2]
    )

print(f"N = {total_count}, медиана med(N) = {median_value}")

# --- 2. Последовательность знаков (+ / -) ---
signs = ['+' if value >= median_value else '-' for value in raw_values]
sign_string = ''.join(signs)
print(f"Последовательность знаков (первые 60): {sign_string[:60]}...")

# --- 3. Подсчёт числа серий ---
series_count = 1
for i in range(1, total_count):
    if signs[i] != signs[i - 1]:
        series_count += 1

print(f"Число серий S = {series_count}")

# --- 4. Критические границы из таблицы (Приложение 1) ---
# Для N = 100 и α = 0.05 (N/2 = 50):
lower_critical_series = 36
upper_critical_series = 64

print(f"Критические границы: S_low = {lower_critical_series}, "
      f"S_high = {upper_critical_series}")

if lower_critical_series < series_count < upper_critical_series:
    print(">>> Гипотеза о случайности НЕ отвергается.")
else:
    print(">>> Гипотеза о случайности ОТВЕРГАЕТСЯ.")


# ============================================================
# ЧАСТЬ В. ПРОВЕРКА НЕЗАВИСИМОСТИ (коэффициент корреляции)
# ============================================================

print("\n" + "=" * 60)
print("ЧАСТЬ В. Проверка независимости")
print("=" * 60)

total_count = len(raw_values)
indices = np.arange(1, total_count + 1)
values_array = np.array(raw_values, dtype=float)

# --- 1. Коэффициент корреляции между x_i и его номером i ---
sum_index_times_value = np.sum(indices * values_array)
sum_values = np.sum(values_array)
sum_values_squared = np.sum(values_array ** 2)

correlation_numerator = (
    (1 / total_count) * sum_index_times_value
    - (1 / total_count) * sum_values * (total_count + 1) / 2
)
correlation_denominator = math.sqrt(
    (
        (1 / total_count) * sum_values_squared
        - ((1 / total_count) * sum_values) ** 2
    ) * (total_count ** 2 - 1) / 12
)

correlation_coefficient = correlation_numerator / correlation_denominator
print(f"r(x_i, i) = {correlation_coefficient:.6f}")

# --- 2. Верхняя граница доверительного интервала ---
z_alpha = stats.norm.ppf(1 - SIGNIFICANCE_LEVEL / 2)
correlation_threshold = (
    z_alpha * (1 - correlation_coefficient ** 2) / math.sqrt(total_count)
)

print(f"z_alpha = {z_alpha:.4f}")
print(f"r_max = {correlation_threshold:.6f}")

# --- 3. Сравнение ---
if abs(correlation_coefficient) > correlation_threshold:
    print(">>> Есть корреляционная связь — "
          "гипотеза независимости ОТВЕРГАЕТСЯ.")
else:
    print(">>> Корреляционная связь не значима — "
          "гипотеза независимости ПРИНИМАЕТСЯ.")
