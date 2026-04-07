import math

def calc_circle_area(radius: float) -> float:
    return math.pi * radius ** 2

def add(a: int, b: int) -> int:
    return a + b

SKILL_REGISTRY = {
    "calc_circle_area": calc_circle_area,
    "add": add
}