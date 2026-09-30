import math

def generate_random_sequence(seed, a, b, m, count):
    sequence = []
    x = seed
    for i in range(count):
        x = (a * x + b) % m
        sequence.append(x)
    return sequence

def print_sequence(title, seq):
    print(title)
    for i in range(0, len(seq), 10):
        chunk = seq[i:i+10]
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
        print(f" Интервал {i+1}: [{start:6.4f}; {end:6.4f}{bracket}  n ={frequencies[i]:>3} "
              f"числа: {preview}")
    print()

def chi_square_test(data, alpha = 0.05):
    n = len(data)
    print("Критерий Хи-квадрат Пирсона")
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    sigma = math.sqrt(variance)
    a_est = mean - math.sqrt(3) * sigma
    b_est = mean + math.sqrt(3) * sigma
    
    print(f"Выборочное среднее x̄ = {mean:.4f}")
    print(f"Выборочная дисперсия D = {variance:.4f}")
    print(f"Стандартное отклонение σ = {sigma:.4f}")
    print(f"Оценка a* = x̄ - √3·σ = {a_est:.4f}")
    print(f"Оценка b* = x̄ + √3·σ = {b_est:.4f}")
    density = 1.0 / (b_est - a_est)
    print(f"Плотность f(x) = 1/(b*-a*) = {density:.6f}")
    print() 

def main():
    m = 1000
    a = 37
    b = 1
    seed = 38
    n = 100
    alpha = 0.05
    
    print("ПАРАМЕТРЫ ГЕНЕРАТОРА:")
    print(f" M = {m}")
    print(f" a = {a}")
    print(f" b = {b}")
    print(f" x0 (затравка) = {seed}")
    print(f" N (количество чисел) = {n}")
    print(f" α (уровень значимости) = {alpha}")
    print()
    
    int_sequence = generate_random_sequence(seed, a, b, m, n)
    print_sequence("СГЕНЕРИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ x_i (начиная с x1):", int_sequence)
    
    float_sequence = [x / m for x in int_sequence]
    print_sequence("НОРМИРОВАННАЯ ПОСЛЕДОВАТЕЛЬНОСТЬ u_i = x_i / M:", float_sequence)
    
    x_min = min(float_sequence)
    x_max = max(float_sequence)
    h = sturges_interval_length(x_max, x_min, n)
    intervals, frequencies = build_intervals(float_sequence, h)
    
    print(f" Длина интервала (h) = {h}")
    print_intervals(intervals, frequencies, float_sequence)
    
    chi_square_test(float_sequence, alpha)

if __name__ == "__main__":
    main()
