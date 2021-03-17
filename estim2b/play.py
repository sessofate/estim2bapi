import time
import numpy as np

from estim2b import Estim

def jolt(e2b, level, jolt_time, mode=None, power=None, block=False):
    '''
    Increase the output level, and optionally mode/power for a set time period.
    e2b: A running instance of Estim.
    level: the output level for channels A and B.
    jolt_time: the length of time to increase output for before it's set to 0.
    mode: the mode to use, if not None. If None existing mode is used.
    power: the power level (H or L) to use. If None existing power level will be used.
    block: if block=True this function won't return until the jolt has finished.
    '''
    if power is not None:
        if power == "H":
            e2b.set_high()
        else:
            e2b.set_low()

    if mode is not None:
        e2b.set_mode(mode)

    e2b.set_output("A", level)
    e2b.set_output("B", level)
    e2b.wait(jolt_time)
    e2b.kill(block=block)


def ramp(e2b, start_level, end_level, dt, mode=None, power=None, block=False):
    '''
    Gradually increase (or decrease) from start_level to end_level with time steps of dt.
    e2b: A running instance of Estim.
    start_level: the initial output level for channels A and B.
    end_level: the final output level for channels A and B.
    dt: the time (in seconds) between each increment.
    mode: the mode to use, if not None. If None existing mode is used.
    power: the power level (H or L) to use. If None existing power level will be used.
    block: if block=True this function won't return until the jolt has finished.
    '''
    if power is not None:
        if power == "H":
            e2b.set_high()
        else:
            e2b.set_low()

    if mode is not None:
        e2b.set_mode(mode)

    direction = 1
    if end_level < start_level:
        direction = -1

    for level in range(start_level, end_level + 1, direction):
        e2b.set_output("A", level)
        e2b.set_output("B", level)
        e2b.wait(dt, block=block)



def rampAB(e2b, start_level_A, end_level_A, start_level_B, end_level_B, duration, mode=None, power=None, block=False):
    '''
    Gradually increase (or decrease) from start_level to end_level with time steps of dt.
    e2b: A running instance of Estim.
    start_level_A/B: the initial output level for channels A and B respectively.
    end_level_A/B: the final output level for channels A and B respectively.
    duration: the time (in seconds) to ramp from start level to end level.
    mode: the mode to use, if not None. If None existing mode is used.
    power: the power level (H or L) to use. If None existing power level will be used.
    block: if block=True this function won't return until the jolt has finished.
    '''
    if power is not None:
        if power == "H":
            e2b.set_high()
        else:
            e2b.set_low()

    if mode is not None:
        e2b.set_mode(mode)

    # Now an issue - duration needs to be big enough, prob. 1 second. Steps adjustments need increment
    # assume response time minimum is 100ms
    duration_total = max(1.0, duration)
    # find dt: largest of 100ms or change of 1 in the level
    total_change_A = end_level_A - start_level_A
    total_change_B = end_level_B - start_level_B
    if min(total_change_B, total_change_A) < duration_total * 10:
        # the smaller change is less than the number of timesteps - take bigger timesteps
        # using max here, but floor during the progression should make this step correctly with the larger
        # value progressing faster. Also using at least step sizes of 100ms (0.1s)
        dt = max(0.1, duration_total / max(np.abs(total_change_B), np.abs(total_change_A)))
        dx_A = total_change_A / (duration_total/dt)
        dx_B = total_change_B / (duration_total/dt)
    else:
        dt = 0.1  # take 100 ms timesteps
        dx_A = total_change_A / (duration_total/dt)
        dx_B = total_change_B / (duration_total/dt)

    level_A = start_level_A
    level_B = start_level_B
    current_time = 0.0
    # time better move forward or we are infinitely messing with this
    assert(dt > 0.0)
    while current_time <= duration_total:
        e2b.set_output("A", np.floor(level_A))
        e2b.set_output("B", np.floor(level_B))
        e2b.wait(dt, block=block)
        current_time = current_time + dt
        level_A = level_A + dx_A
        level_B = level_B + dx_B
