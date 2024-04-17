import math
import random

random.seed()

# Compute the temperature at a given time of day (in hours)
# The formula describes a scaled sinusoid with a small random contribution
def __compute_temperature(current_time : float) -> float:
    return 5. * math.sin(2 * math.pi * (current_time - 9 / 24)) + 275 + random.random()

# "Public" alias for the method below
def compute_temperature(current_time) -> float:
    return __compute_temperature(current_time)

# FMU state initialization
def init():
    return __compute_temperature(0.)

# FMU stepping
def do_step(start_time : float, stop_time : float):
    avg_time = (start_time + stop_time) / 2.
    return __compute_temperature(avg_time)