from enum import Enum
from typing import Literal
import core
import elevator
import sys

class Color(Enum):
    Black   = 30
    Red     = 31
    Green   = 32
    Yellow  = 33
    Blue    = 34
    Magenta = 35
    Cyan    = 36
    White   = 37
    Default = 39

CONSOLE_PREFIX = "\u001b"

WIDTH = 34
BLOCK = "█"

class Display:
    def __init__(self):
        self.debug_print_line_count = 0

    def print(self, *args):
        self.debug_print_line_count += 1
        print(*args)

    def display_tick(self, t: int, sim: "core.Sim", debug: bool = False):
        max_digits = len(str(len(sim.floors)))

        console_cursor_reset()

        print("ELEVATOR --- tick =", t)
        print("*" * WIDTH)
        for floor in range(len(sim.floors) - 1, -1, -1):
            floor_str = str(floor)
            digits = len(floor_str)

            line = "* "
            line += " " * (max_digits - digits)
            line += floor_str
            line += " |"
            if sim.el1.floor == floor:
                print(line, end='')
                el_print(sim.el1)
                line = ""
            else:
                line += "  "
            line += "|"
            if sim.el2.floor == floor:
                print(line, end='')
                el_print(sim.el2)
                line = ""
            else:
                line += "  "
            line += "| "

            # Waiting section

            floor_state = sim.floors[floor]

            if len(floor_state.up) > 0:
                line += f" Up: {len(floor_state.up):>3} "
            else:
                line += "         "

            if len(floor_state.down) > 0:
                line += f" Down: {len(floor_state.down):>3} "
            else:
                line += "           "

            line += "*"

            # testing section

            if debug:
                line += " "
                for i in range(min(sim.request_cursor, len(sim.requests))):
                    req = sim.requests[i]
                    if floor == req.floor:
                        line += "S"
                    elif floor == req.target:
                        line += "E"
                    else:
                        smaller = min(req.floor, req.target)
                        larger  = max(req.floor, req.target)
                        if floor > smaller and floor < larger:
                            line += "|"
                        else:
                            line += " "

            print(line)
        print("*" * WIDTH)

        # Additional Request Info

        console_clear_line()
        print(f"Total people waiting: {min(sim.request_cursor, len(sim.requests))}")
        print(f"Total people delivered: {sim.get_delivered()}")

        # Elevator Info

        console_clear_line()
        print(f"[Elevator 1] Floor: {sim.el1.floor:>2} | Passengers: {len(sim.el1.passengers):>2} | State: ", end='')
        cprint(el_state_color(sim.el1.state), sim.el1.state, end='')
        console_reset()
        print(f" | Instruction: {sim.el1.current_inst}")

        console_clear_line()
        print(f"[Elevator 2] Floor: {sim.el2.floor:>2} | Passengers: {len(sim.el2.passengers):>2} | State: ", end='')
        cprint(el_state_color(sim.el2.state), sim.el2.state, end='')
        console_reset()
        print(f" | Instruction: {sim.el2.current_inst}")

def el_state_color(state: "elevator.ElevatorState") -> Color:
    if state == elevator.ElevatorState.DoorOpen:
        return Color.Red
    if state == elevator.ElevatorState.DoorClosed:
        return Color.Green
    if state == elevator.ElevatorState.Moving:
        return Color.Blue


def el_print(el: "core.Elevator"):
    string = el_str(el)
    color = el_state_color(el.state)
    cprint(color, string, end='')
    console_reset()

def el_str(el: "core.Elevator") -> str:
    passenger_count = len(el.passengers)
    if passenger_count == 0:
        return BLOCK*2
    if passenger_count < 10:
        return BLOCK + str(passenger_count)
    return BLOCK + "C"


def fatal_error(msg: str, color: Color = Color.Red):
    cprint(color, "Elevator Error:", msg)
    console_reset()
    sys.exit(1)


def console_clear():
    print(f"{CONSOLE_PREFIX}[2J", end='')


def console_clear_line():
    print(f"{CONSOLE_PREFIX}[0K", end='')


def console_cursor_reset():
    print(f"{CONSOLE_PREFIX}[H", end='')


def console_cursor_down(n):
    if n == 0:
        return
    print(f"{CONSOLE_PREFIX}[{n}B", end='')


def cprint(color: Color, *args, end: str = "\n", bg: bool = False):
    console_color(color, bg)
    print(*args, end=end)


def console_reset():
    print(f"{CONSOLE_PREFIX}[0m", end='')


def console_color(color: Color, bg: bool = False):
    print(f"{CONSOLE_PREFIX}[{color.value + (10 if bg else 0)}m", end='')
