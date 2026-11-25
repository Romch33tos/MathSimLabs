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
