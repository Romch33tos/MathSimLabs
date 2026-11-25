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
