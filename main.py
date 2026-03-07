import core
import display
import elevator
import time
import sys
import random


class Args:
    def __init__(self):
        r = random.Random(time.time())

        self.wait_time = 0.05 # normal = 0.05, fast = 0, slow = 0.15
        self.seed      = r.randint(0, 2**32)
        self.skip_to   = 0
        self.nogui     = False
        self.debug     = False
        self.morestats = False


def parse_args(argv) -> Args:
    result = Args()
    for arg in argv:
        if arg == "fast":
            result.wait_time = 0
        elif arg == "slow":
            result.wait_time = 0.15
        elif arg.startswith("seed="):
            parts = arg.split('=')
            if len(parts) == 2:
                result.seed = int(parts[1])
        elif arg == "nogui":
            result.nogui = True
        elif arg.startswith("skip="):
            parts = arg.split('=')
            if len(parts) == 2:
                result.skip_to = int(parts[1])
        elif arg == "debug":
            result.debug = True
        elif arg == "morestats":
            result.morestats = True
    return result


def main():

    args = parse_args(sys.argv[1:])

    n           = 100
    floors      = 20
    total_ticks = 240

    requests = core.generate_requests(args.seed, n, floors, total_ticks)
    l = len(requests)

    sim = core.Sim(floors, requests)
    user_state, boarding_style = elevator.elevator_setup()
    sim.boarding_style = boarding_style

    if not args.nogui:
        display.console_clear()
        display.console_cursor_reset()
    for tick in range(total_ticks * 8):
        sim.tick(user_state)
        if not args.nogui and args.skip_to <= tick:
            sim.d.display_tick(tick, sim, args.debug)
            time.sleep(args.wait_time)
        if sim.finished:
            break

    sim.finish(args.seed, args.morestats)


if __name__ == "__main__":
    main()
