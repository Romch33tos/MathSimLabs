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
