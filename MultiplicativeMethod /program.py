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
