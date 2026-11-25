import math
import random


def fmt(value, digits):
  if value == 0:
    return "0"
  rounded = round(value, digits)
  if rounded == 0:
    return "0"
  text = f"{rounded:.{digits}f}"
  if "." in text:
    text = text.rstrip("0").rstrip(".")
  return text


def print_header(title):
  line = "=" * 78
  print(line)
  print(title.upper().center(78))
  print(line)


def print_subheader(title):
  line = "-" * 78
  print(line)
  print(title.center(78))
  print(line)


def print_step(step_number, step_name):
  print_subheader(f"ШАГ {step_number}. {step_name}")


def print_indented(text):
  print("  " + text)

def print_table(headers, rows):
  str_headers = [str(h) for h in headers]
  str_rows = [[str(cell) for cell in row] for row in rows]

  widths = []
  for col_index in range(len(str_headers)):
    column_values = [str_headers[col_index]] + [
      row[col_index] for row in str_rows
    ]
    max_length = max(len(value) for value in column_values)
    widths.append(max(max_length + 2, 8))

  separator = "+" + "+".join("-" * w for w in widths) + "+"

  print(separator)

  header_line = "|"
  for width, title in zip(widths, str_headers):
    header_line += title.center(width) + "|"
  print(header_line)
  print(separator)

  for row in str_rows:
    row_line = "|"
    for width, cell in zip(widths, row):
      row_line += cell.center(width) + "|"
    print(row_line)
  print(separator)
  print()

def task_1_analytical():
  print_header("ЗАДАЧА 1. ДОСТУПНОСТЬ IT-ИНФРАСТРУКТУРЫ")

  print_step(1, "Доступность слоя авторизации (Блок 1)")
  print_indented("Слой падает, только если падают оба сервера A и B.")
  print_indented("P(A) = 0.80, P(B) = 0.70")
  print_indented("P(слой1 работает) = 1 - (1 - P(A)) * (1 - P(B))")
  availability_layer1 = 1 - (1 - 0.80) * (1 - 0.70)
  print_indented(f"  = 1 - 0.20 * 0.30 = {fmt(availability_layer1, 6)}")
  print()

  print_step(2, "Доступность шлюза API (Блок 2)")
  print_indented("Единственный прокси-сервер C, резерва нет.")
  print_indented("P(C) = 0.95")
  availability_layer2 = 0.95
  print_indented(f"P(слой2 работает) = {fmt(availability_layer2, 6)}")
  print()

  print_step(3, "Доступность слоя базы данных (Блок 3)")
  print_indented("Три независимые реплики D, E, F. Работает, если жива хотя бы одна.")
  print_indented("P(D) = 0.85, P(E) = 0.90, P(F) = 0.70")
  print_indented("P(слой3 работает) = 1 - (1 - P(D)) * (1 - P(E)) * (1 - P(F))")
  availability_layer3 = 1 - (1 - 0.85) * (1 - 0.90) * (1 - 0.70)
  print_indented(f"  = 1 - 0.15 * 0.10 * 0.30 = {fmt(availability_layer3, 6)}")
  print()

  print_step(4, "Целевая доступность всего сервиса")
  print_indented("Слои последовательны: сервис работает, если работают все три.")
  print_indented("P(система) = P(слой1) * P(слой2) * P(слой3)")
  availability_total = availability_layer1 * availability_layer2 * availability_layer3
  print_indented(
    f"  = {fmt(availability_layer1, 4)} * {fmt(availability_layer2, 4)} * "
    f"{fmt(availability_layer3, 4)} = {fmt(availability_total, 6)}"
  )
  print()
  return availability_total

def simulate_layer1(rng):
  return rng.random() < 0.80 or rng.random() < 0.70


def simulate_layer2(rng):
  return rng.random() < 0.95


def simulate_layer3(rng):
  return rng.random() < 0.85 or rng.random() < 0.90 or rng.random() < 0.70


def task_1_monte_carlo(analytical_probability, n_requests=1000, seed=42):
  print_step(5, "Симуляция Монте-Карло (1000 запросов)")
  rng = random.Random(seed)
  successful_requests = 0
  for _ in range(n_requests):
    if simulate_layer1(rng) and simulate_layer2(rng) and simulate_layer3(rng):
      successful_requests += 1

  empirical_probability = successful_requests / n_requests
  print_indented(f"Число успешных запросов: {successful_requests} из {n_requests}")
  print_indented(f"Эмпирическая вероятность: {fmt(empirical_probability, 6)}")
  print_indented(f"Аналитическая вероятность: {fmt(analytical_probability, 6)}")

  absolute_error = abs(empirical_probability - analytical_probability)
  relative_error = absolute_error / analytical_probability * 100
  print_indented(f"Абсолютная ошибка: {fmt(absolute_error, 6)}")
  print_indented(f"Относительная ошибка: {fmt(relative_error, 4)} %")

  standard_error = math.sqrt(
    empirical_probability * (1 - empirical_probability) / n_requests
  )
  print_indented(f"Стандартная ошибка оценки: {fmt(standard_error, 6)}")
  print_indented(
    f"Доверительный интервал (95%): "
    f"[{fmt(empirical_probability - 1.96 * standard_error, 4)}; "
    f"{fmt(empirical_probability + 1.96 * standard_error, 4)}]"
  )
  print()

  print_table(
    ["Показатель", "Значение"],
    [
      ["Аналит.", fmt(analytical_probability, 6)],
      ["Монте-Карло", fmt(empirical_probability, 6)],
      ["Абс. ошибка", fmt(absolute_error, 6)],
      ["Отн. ошибка, %", fmt(relative_error, 4)],
    ],
  )

  print_indented("Вывод: эмпирическая оценка близка к аналитической,")
  print_indented("относительная ошибка мала, что подтверждает корректность модели.")
  print("=" * 78)
  print()


def run_task_1():
  analytical_1 = task_1_analytical()
  task_1_monte_carlo(analytical_1, n_requests=1000)

def task_2_analytical():
  print_header("ЗАДАЧА 2. ОБНАРУЖЕНИЕ СБОЯ КОМПЬЮТЕРА")

  print_step(1, "Вероятности возникновения сбоя по устройствам")
  print_indented("Отношение n1:n2:n3 = 2:3:5, сумма частей = 10")
  probability_alu = 2 / 10
  probability_ram = 3 / 10
  probability_other = 5 / 10
  print_indented(f"P(АЛУ) = 2/10 = {fmt(probability_alu, 4)}")
  print_indented(f"P(ОЗУ) = 3/10 = {fmt(probability_ram, 4)}")
  print_indented(f"P(прочие) = 5/10 = {fmt(probability_other, 4)}")
  print()

  print_step(2, "Вероятности обнаружения сбоя")
  detection_alu = 0.8
  detection_ram = 0.9
  detection_other = 0.95
  print_indented(f"p1 = {fmt(detection_alu, 4)}, p2 = {fmt(detection_ram, 4)}, "
                 f"p3 = {fmt(detection_other, 4)}")
  print()

  print_step(3, "Полная вероятность обнаружения сбоя")
  print_indented("P(обнаружен) = Σ P(устройство) * P(обнаружение | устройство)")
  probability_detected = (
    probability_alu * detection_alu
    + probability_ram * detection_ram
    + probability_other * detection_other
  )
  print_indented(
    f"  = {fmt(probability_alu, 2)}*{fmt(detection_alu, 2)} + "
    f"{fmt(probability_ram, 2)}*{fmt(detection_ram, 2)} + "
    f"{fmt(probability_other, 2)}*{fmt(detection_other, 2)}"
  )
  print_indented(f"  = {fmt(probability_detected, 6)}")
  print()
  return probability_detected

def task_2_monte_carlo(analytical_probability, n_experiments=100, seed=7):
  print_step(4, "Симуляция Монте-Карло (N = 100)")
  rng = random.Random(seed)
  devices = [
    (0.2, 0.8),
    (0.3, 0.9),
    (0.5, 0.95),
  ]
  detected_count = 0
  for _ in range(n_experiments):
    roll = rng.random()
    cumulative = 0.0
    chosen_detection = 0.0
    for failure_prob, detection_prob in devices:
      cumulative += failure_prob
      if roll <= cumulative:
        chosen_detection = detection_prob
        break
    if rng.random() < chosen_detection:
      detected_count += 1

  empirical_probability = detected_count / n_experiments
  print_indented(f"Обнаружено сбоев: {detected_count} из {n_experiments}")
  print_indented(f"Эмпирическая вероятность: {fmt(empirical_probability, 6)}")
  print_indented(f"Аналитическая вероятность: {fmt(analytical_probability, 6)}")

  absolute_error = abs(empirical_probability - analytical_probability)
  relative_error = absolute_error / analytical_probability * 100
  print_indented(f"Абсолютная ошибка: {fmt(absolute_error, 6)}")
  print_indented(f"Относительная ошибка: {fmt(relative_error, 4)} %")

  standard_error = math.sqrt(
    empirical_probability * (1 - empirical_probability) / n_experiments
  )
  print_indented(f"Стандартная ошибка оценки: {fmt(standard_error, 6)}")
  print_indented(
    f"Доверительный интервал (95%): "
    f"[{fmt(empirical_probability - 1.96 * standard_error, 4)}; "
    f"{fmt(empirical_probability + 1.96 * standard_error, 4)}]"
  )
  print()

  print_table(
    ["Показатель", "Значение"],
    [
      ["Аналит.", fmt(analytical_probability, 6)],
      ["Монте-Карло", fmt(empirical_probability, 6)],
      ["Абс. ошибка", fmt(absolute_error, 6)],
      ["Отн. ошибка, %", fmt(relative_error, 4)],
    ],
  )

  print_indented("Вывод: при N = 100 разброс оценки заметен, но результат")
  print_indented("согласуется с аналитическим в пределах статистической погрешности.")
  print("=" * 78)
  print()


def run_task_2():
  analytical_2 = task_2_analytical()
  task_2_monte_carlo(analytical_2, n_experiments=100)

def task_3_optimal_servers(n_trials=1000, seed=123):
  print_header("ЗАДАЧА 3. ОПТИМАЛЬНОЕ ЧИСЛО ОБЛАЧНЫХ СЕРВЕРОВ")

  print_step(1, "Исходные параметры")
  revenue_per_server = 4.00
  reservation_cost = 1.50
  refund_per_unused = 0.20
  print_indented(f"Доход с сервера: {fmt(revenue_per_server, 2)} у.е.")
  print_indented(f"Стоимость резервирования: {fmt(reservation_cost, 2)} у.е.")
  print_indented(f"Возврат за лишний сервер: {fmt(refund_per_unused, 2)} у.е.")
  print()

  print_step(2, "Распределение спроса")
  demand_values = [10000, 20000, 40000, 60000]
  demand_probabilities = [0.10, 0.35, 0.30, 0.25]
  rows = []
  for d, p in zip(demand_values, demand_probabilities):
    rows.append([str(d), fmt(p, 2)])
  print_table(["Спрос", "Вероятность"], rows)

  print_step(3, "Симуляция прибыли для каждого числа серверов")
  rng = random.Random(seed)
  candidate_servers = [
    10000, 20000, 30000, 40000, 50000, 60000, 70000,
  ]
  results = []
  for reserved in candidate_servers:
    total_profit = 0.0
    for _ in range(n_trials):
      roll = rng.random()
      cumulative = 0.0
      demand = demand_values[-1]
      for d, p in zip(demand_values, demand_probabilities):
        cumulative += p
        if roll <= cumulative:
          demand = d
          break

      served = min(demand, reserved)
      unused = max(reserved - demand, 0)
      profit = (
        served * revenue_per_server
        - reserved * reservation_cost
        + unused * refund_per_unused
      )
      total_profit += profit
    average_profit = total_profit / n_trials
    results.append((reserved, average_profit))

  rows = []
  best_reserved = None
  best_profit = -math.inf
  for reserved, profit in results:
    rows.append([str(reserved), fmt(profit, 2)])
    if profit > best_profit:
      best_profit = profit
      best_reserved = reserved
  print_table(["Серверов", "Ср. прибыль"], rows)

  print_step(4, "Выбор оптимального решения")
  print_indented(f"Максимальная средняя прибыль: {fmt(best_profit, 2)} у.е.")
  print_indented(f"Оптимальное число серверов: {best_reserved}")
  print()

  print_indented("Вывод: резервировать следует количество серверов,")
  print_indented("соответствующее максимальной средней прибыли по результатам")
  print_indented("1000 имитационных испытаний для каждого варианта.")
  print("=" * 78)
  print()


def run_task_3():
  task_3_optimal_servers(n_trials=1000)

def simulate_robot_repair(rng):
  components_count = 5
  inspection_time = sum(rng.uniform(2, 5) for _ in range(components_count))

  failed_components = sum(
    1 for _ in range(components_count) if rng.random() < 0.1
  )

  replacement_time = 0.0
  for _ in range(failed_components):
    replacement_time += max(0.0, rng.gauss(5, 1))

  if failed_components == 0:
    adjustment_time = rng.expovariate(1 / 10)
  else:
    adjustment_time = rng.expovariate(1 / 15)

  total_time = inspection_time + replacement_time + adjustment_time
  return total_time, failed_components


def task_4_robot_repair(n_simulations=10000, seed=99):
  print_header("ЗАДАЧА 4. РЕМОНТ ПРОМЫШЛЕННЫХ РОБОТОВ")

  print_step(1, "Параметры модели")
  print_indented("Компонентов: 5, вероятность неисправности каждого: 0.1")
  print_indented("Осмотр: равномерное U(2, 5) мин на компонент")
  print_indented("Замена: нормальное N(5, 1) мин на компонент")
  print_indented("Мелкая наладка: экспоненциальное, среднее 10 мин")
  print_indented("Полная наладка: экспоненциальное, среднее 15 мин")
  print()

  print_step(2, "Симуляция Монте-Карло")
  rng = random.Random(seed)
  total_time_sum = 0.0
  full_adjustment_count = 0
  failed_components_sum = 0
  for _ in range(n_simulations):
    total_time, failed_components = simulate_robot_repair(rng)
    total_time_sum += total_time
    failed_components_sum += failed_components
    if failed_components > 0:
      full_adjustment_count += 1

  average_total_time = total_time_sum / n_simulations
  full_adjustment_share = full_adjustment_count / n_simulations * 100
  average_failed_components = failed_components_sum / n_simulations

  print_indented(f"Число имитаций: {n_simulations}")
  print()

  print_step(3, "Результаты")
  print_indented(f"а) Среднее время ремонта: {fmt(average_total_time, 4)} мин")
  print_indented(f"б) Доля полной наладки: {fmt(full_adjustment_share, 4)} %")
  print_indented(f"в) Среднее число замен: {fmt(average_failed_components, 4)}")

  theoretical_full = (1 - 0.9 ** 5) * 100
  theoretical_components = 5 * 0.1
  print()
  print_indented(
    f"Теоретическая доля полной наладки: {fmt(theoretical_full, 4)} %"
  )
  print_indented(
    f"Теоретическое среднее число замен: {fmt(theoretical_components, 4)}"
  )
  print()

  print_table(
    ["Показатель", "Значение"],
    [
      ["Ср. время, мин", fmt(average_total_time, 4)],
      ["Полная наладка, %", fmt(full_adjustment_share, 4)],
      ["Ср. замен", fmt(average_failed_components, 4)],
    ],
  )

  print_indented("Вывод: результаты имитации согласуются с теоретическими")
  print_indented("оценками; расхождения объясняются случайностью выборки.")
  print("=" * 78)
  print()


def run_task_4():
  task_4_robot_repair(n_simulations=10000)

def print_menu():
  print_header("МЕНЮ ЗАПУСКА ЗАДАЧ")
  print_indented("1 - Доступность IT-инфраструктуры")
  print_indented("2 - Обнаружение сбоя компьютера")
  print_indented("3 - Оптимальное число серверов")
  print_indented("4 - Ремонт промышленных роботов")
  print_indented("0 - Выход")
  print()


def main():
  actions = {
    "1": run_task_1,
    "2": run_task_2,
    "3": run_task_3,
    "4": run_task_4,
  }
  while True:
    print_menu()
    choice = input("  Выберите пункт меню: ").strip()
    print()
    if choice == "0":
      print_indented("Выход из программы.")
      break
    action = actions.get(choice)
    if action is None:
      print_indented("Неверный пункт меню. Введите 1, 2, 3, 4 или 0.")
      print()
      continue
    action()


if __name__ == "__main__":
  main()
