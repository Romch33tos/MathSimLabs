import math
import numpy as np
from scipy import stats

# ============================================================
# ЧАСТЬ 0. ГЕНЕРАЦИЯ ПОСЛЕДОВАТЕЛЬНОСТИ СЛУЧАЙНЫХ ЧИСЕЛ
# ============================================================

def generate_pseudo_random_sequence(multiplier, increment, modulus, seed, count):
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
interval_edges[-1] = max_value + 1e-9  

empirical_frequencies = [0] * interval_count
for value in raw_values:
    for i in range(interval_count):
        if interval_edges[i] <= value < interval_edges[i + 1]:
            empirical_frequencies[i] += 1
            break
