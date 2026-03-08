import random, math
import elevator
import display
from elevator import ( BoardingStyle,
                       ElevatorState,
                       ElevatorStatus,
                       Floor,
                       Instruction,
                       InstructionType,
                       InstructionQueue,
                       Passenger,
                       elevators_tick )

#######
# Types


class Request:
    def __init__(self):
        self.time:           int  = -1 # tick when the request will be made
        self.floor:          int  = 0 # floor they are on
        self.target:         int  = 0 # target floor
        self.time_boarded:   int  = -1
        self.delivered:      bool = False
        self.time_delivered: int  = -1

    def __str__(self):
        return f"(t = {self.time}, from {self.floor} to {self.target})"


class Elevator:
    def __init__(self, id: int):
        self.id = id
        self.floor = 0
        self.passengers: list[Request] = []
        self.capacity = 10 # constant
        self.state = ElevatorState.DoorClosed
        self.current_inst: Instruction|None = None
        self.heading: int = 1 # Up is 1, down is -1

    def __str__(self):
        return f"(floor = {self.floor}, #passenger = {len(self.passengers)})"

    def state_change(self, new_state: ElevatorState):
        if self.state == new_state:
            return

        assert not (self.state == ElevatorState.Moving and new_state == ElevatorState.DoorOpen)
        if self.state == ElevatorState.DoorOpen and new_state == ElevatorState.Moving:
            display.fatal_error(f"Uh oh! Elevator {self.id} started moving while the doors were open!")

        self.state = new_state


class FloorState:
    def __init__(self):
        self.up:   list[Request] = []
        self.down: list[Request] = []


class Sim:
    def __init__(self, floors: int, reqs: list[Request]):
        self.current_tick                  = -1
        self.requests                      = reqs
        self.request_cursor                = 0
        self.el1                           = Elevator(1)
        self.el2                           = Elevator(2)
        self.floors: list[FloorState]      = [FloorState() for _ in range(floors)]
        self.iq                            = InstructionQueue()
        self.d                             = display.Display()
        self.last_floor_state: list[Floor] = [Floor() for _ in range(floors)]
        self.finished                      = False
        self.el1_was_used                  = False
        self.el2_was_used                  = False
        self.boarding_style                = BoardingStyle.BasedOnHeading

    def get_delivered(self) -> int:
        sum = 0
        for req in self.requests:
            if req.delivered:
                sum += 1
        return sum

    def handle_issuing_request(self):
        if self.request_cursor >= len(self.requests):
            return

        peek = self.requests[self.request_cursor]
        if peek.time != self.current_tick:
            return

        self.request_cursor += 1

        floor_state = self.floors[peek.floor]

        assert peek.target != peek.floor
        if peek.target > peek.floor:
            floor_state.up.append(peek)
        else:
            floor_state.down.append(peek)

        self.handle_issuing_request()

    def handle_issuing_instructions(self):
        if len(self.iq._queue) == 0:
            return

        remaining = []

        for inst in self.iq._queue:
            el = None
            if inst.elevator_id == 1:
                el = self.el1
                self.el1_was_used = True
            elif inst.elevator_id == 2:
                el = self.el2
                self.el2_was_used = True
            else:
                display.fatal_error(f"Unknown elevator id = {inst.elevator_id}")

            if el.current_inst != None:
                remaining.append(inst)
                continue

            el.current_inst = inst

        self.iq._queue = remaining

    def construct_status(self) -> ElevatorStatus:
        status = ElevatorStatus()
        status.current_tick = self.current_tick
        status.el1_state = self.el1.state
        status.el2_state = self.el2.state
        status.el1_floor = self.el1.floor
        status.el2_floor = self.el2.floor
        status.el1_target = self.el1.current_inst.floor if self.el1.current_inst != None else -1
        status.el2_target = self.el2.current_inst.floor if self.el2.current_inst != None else -1
        for req in self.el1.passengers:
            p = Passenger()
            p.time_boarded = req.time_boarded
            p.target_floor = req.target
            status.el1_passengers.append(p)
        for req in self.el2.passengers:
            p = Passenger()
            p.time_boarded = req.time_boarded
            p.target_floor = req.target
            status.el2_passengers.append(p)
        for i in range(len(self.floors)):
            floor = self.floors[i]
            f     = Floor()
            f.up_pressed   = len(floor.up) > 0
            f.down_pressed = len(floor.down) > 0
            if f.up_pressed:
                if self.last_floor_state[i].up_pressed:
                    f.up_pressed_at = self.last_floor_state[i].up_pressed_at
                else:
                    f.up_pressed_at = self.current_tick
            if f.down_pressed:
                if self.last_floor_state[i].down_pressed:
                    f.down_pressed_at = self.last_floor_state[i].down_pressed_at
                else:
                    f.down_pressed_at = self.current_tick
            status.floor_list.append(f)
        return status

    def update_elevator(self, el: Elevator, other_el: Elevator):
        if el.current_inst != None:
            inst = el.current_inst
            if inst.type == InstructionType.OpenDoor:
                el.state_change(ElevatorState.DoorOpen)
                el.current_inst = None
            elif inst.type == InstructionType.CloseDoor:
                el.state_change(ElevatorState.DoorClosed)
                el.current_inst = None
            elif inst.type == InstructionType.GotoFloor:
                el.state_change(ElevatorState.Moving)
                if inst.floor < 0 or inst.floor >= len(self.floors):
                    display.fatal_error(f"Floor {inst.floor} not found.")
                if inst.floor > el.floor:
                    el.heading = 1
                elif inst.floor < el.floor:
                    el.heading = -1

        if el.state == ElevatorState.Moving:

            assert el.current_inst != None
            if el.floor == el.current_inst.floor:
                el.state_change(ElevatorState.DoorClosed)
                el.current_inst = None
                # Set the headings at the ends so that people will board the bottom
                # elevator even if the second elevator is not in use.
                if el.floor == 0:
                    el.heading = 1
                elif el.floor == len(self.floors) - 1:
                    el.heading = -1
            else:
                el.floor += el.heading

        elif el.state == ElevatorState.DoorOpen:

            remaining = []
            for passenger in el.passengers:
                if el.floor == passenger.target:
                    passenger.delivered = True
                    passenger.time_delivered = self.current_tick
                else:
                    remaining.append(passenger)
            el.passengers = remaining

            if len(el.passengers) < el.capacity:
                boarding_passenger = None

                if el.heading == 1 and len(self.floors[el.floor].up) > 0:
                    boarding_passenger = self.floors[el.floor].up.pop(0)
                elif el.heading == -1 and len(self.floors[el.floor].down) > 0:
                    boarding_passenger = self.floors[el.floor].down.pop(0)

                if boarding_passenger == None:
                    if self.boarding_style == BoardingStyle.JustGetOn:
                        if len(self.floors[el.floor].up) > 0:
                            boarding_passenger = self.floors[el.floor].up.pop(0)
                        elif len(self.floors[el.floor].down) > 0:
                            boarding_passenger = self.floors[el.floor].down.pop(0)

                if boarding_passenger:
                    boarding_passenger.time_boarded = self.current_tick
                    el.passengers.append(boarding_passenger)

    def check_for_finished(self) -> bool:
        all_delivered = True
        for req in self.requests:
            if not req.delivered:
                all_delivered = False
                break
        return all_delivered

    def tick(self, user_state):
        if self.check_for_finished():
            self.finished = True
            return

        self.current_tick += 1

        self.update_elevator(self.el1, self.el2)
        self.update_elevator(self.el2, self.el1)
        self.handle_issuing_request()

        status = self.construct_status()
        elevators_tick(user_state, status, self.iq)

        self.handle_issuing_instructions()
        self.last_floor_state = status.floor_list

    def finish(self, seed, more_stats: bool):
        num_req = len(self.requests)
        num_delivered = self.get_delivered()

        points = 0

        # Points for delivering people.

        p_delivered = num_delivered * 10

        # Points for finishing fast.

        p_finish = 0
        if num_delivered == num_req:
            finish_tick = self.current_tick
            last_person_arrival = max([r.time for r in self.requests])
            diff = finish_tick - last_person_arrival
            p_finish = max(2000 - diff, 0)

        # Points for shorter average wait-for-elevator time.
        # Points for shorter average elevator ride time.

        wfe_times = [] # Wait-for-elevator times
        er_times  = [] # Elevator ride times
        for r in self.requests:
            if r.time_boarded == -1:
                wfe_times.append(self.current_tick - r.time)
                continue
            wfe_times.append(r.time_boarded - r.time)
            if r.time_delivered == -1:
                continue
            er_times.append(r.time_delivered - r.time_boarded)

        wfe_avg = None
        er_avg  = None
        p_wfe   = 0
        p_er    = 0

        if len(wfe_times) > 0:
            wfe_avg = round(sum(wfe_times) / len(wfe_times))
            p_wfe = max(1000 - wfe_avg, 0)
        if len(er_times) > 0:
            er_avg  = round(sum(er_times) / len(er_times))
            p_er  = round(max(1000 - er_avg, 0) * (len(er_times) / num_req))

        # Points for using the elevators

        p_el1 = 1000 if self.el1_was_used else 0
        p_el2 = 1000 if self.el2_was_used else 0

        # Points total

        points = p_delivered + p_finish + p_wfe + p_er + p_el1 + p_el2

        C = display.Color
        cprint = display.cprint
        cprint(C.Cyan, "--- Elevator Results ---")

        if more_stats:
            cprint(C.Default, f"Seed: {seed}")
            cprint(C.Default, f"Finished at tick {self.current_tick}.")

        if self.el1_was_used:
            cprint(C.Blue, "Used elevator 1.")
        else:
            cprint(C.Blue, "Did not use elevator 1.")
        cprint(C.Yellow, f"-> {p_el1} points.")

        if self.el2_was_used:
            cprint(C.Blue, "Used elevator 2.")
        else:
            cprint(C.Blue, "Did not use elevator 2.")
        cprint(C.Yellow, f"-> {p_el2} points.")

        cprint(C.Blue, "Delivered ", end='')
        cprint(C.White, str(num_delivered), end='')
        cprint(C.Default, "/", end='')
        cprint(C.White, str(num_req), end='')
        cprint(C.Blue, " passengers.")
        cprint(C.Yellow, f"-> {p_delivered} points.")

        if num_delivered == num_req:
            cprint(C.Blue, "Finished ", end='')
            cprint(C.White, str(diff), end='')
            cprint(C.Blue, " ticks after last passenger arrived.")
        else:
            cprint(C.Blue, "Did not finish.")
        cprint(C.Yellow, f"-> {p_finish} points.")

        if more_stats:
            wfe_times.sort()
            cprint(C.Cyan, "Wait-for-elevator times: ", end='')
            cprint(C.Default, wfe_times)

        cprint(C.Blue, "Average wait-for-elevator time: ", end='')
        cprint(C.White, str(wfe_avg), end='')
        cprint(C.Blue, " ticks.");
        cprint(C.Yellow, f"-> {p_wfe} points.")

        if more_stats:
            er_times.sort()
            cprint(C.Cyan, "Elevator ride times: ", end='')
            cprint(C.Default, er_times)

        cprint(C.Blue, "Average elevator ride time: ", end='')
        cprint(C.White, str(er_avg), end='')
        cprint(C.Blue, " ticks.");
        cprint(C.Yellow, f"-> {p_er} points.")

        cprint(C.Green, "Total: ", end='')
        cprint(C.Yellow, f"{points} points.")

        display.console_reset()


###########
# Functions

def generate_requests(seed: int, n: int, floors: int, total_time_ticks: int) -> list[Request]:

    result: list[Request] = []

    rand = random.Random(seed)

    reqs = []

    first_third  = n // 3
    second_third = first_third + (n // 3)

    for i in range(n):
        req = Request()
        req.time  = round(rand.random() * total_time_ticks)
        req.floor = math.floor(rand.random() * floors)

        if i <= first_third:
            reqs.append((req, "short"))
        elif i <= second_third:
            reqs.append((req, "medium"))
        else:
            reqs.append((req, "long"))

    for (req, dist) in reqs:

        if dist == "short":
            d = round(rand.uniform(1, 3))
        elif dist == "medium":
            d = round(rand.uniform(4, 6))
        else:
            d = round(rand.uniform(7, floors))

        if rand.random() < 0.5:
            d *= -1

        target = req.floor + d
        target = min(target, floors - 1)
        target = max(target, 0)
        req.target = target

        if req.target != req.floor:
            result.append(req)

    result.sort(key=lambda req: req.time)

    return result
