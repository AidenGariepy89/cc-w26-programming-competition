from enum import Enum

''' This file will contain your implementation.
    Please do not modify the code in the `Types` section, but below that
    write as much code as you would like.
'''

#######################
# Types (DO NOT MODIFY)

class Passenger:
    ''' Contains information about an elevator's passenger. '''

    def __init__(self):
        self.time_boarded = 0
        self.target_floor = 0


class ElevatorState(Enum):
    DoorClosed = 0
    DoorOpen   = 1
    Moving     = 2

    def __str__(self):
        if self == ElevatorState.DoorClosed:
            return "DOOR_CLOSED"
        elif self == ElevatorState.DoorOpen:
            return "DOOR_OPEN"
        else:
            return "MOVING"


class Floor:
    ''' Contains information about a floor in the building. '''

    def __init__(self):
        self.up_pressed      = False # True if people are waiting at this floor to go up.
        self.down_pressed    = False # True if people are waiting at this floor to go down.
        self.up_pressed_at   = -1    # The tick when people started waiting to go up.
        self.down_pressed_at = -1    # The tick when people started waiting to go down.


class ElevatorStatus:
    ''' `el1` stands for elevator 1, and `el2` stands for elevator 2. '''

    def __init__(self):
        self.current_tick: int               = -1 # Current tick of the sim
        self.el1_state: ElevatorState        = ElevatorState.DoorClosed
        self.el2_state: ElevatorState        = ElevatorState.DoorClosed
        self.el1_floor: int                  = 0  # The floor elevator 1 is currently at.
        self.el2_floor: int                  = 0  # The floor elevator 2 is currently at.
        self.el1_target: int                 = -1 # The floor elevator 1 is moving to. -1 if the elevator is not moving.
        self.el2_target: int                 = -1 # The floor elevator 2 is moving to. -1 if the elevator is not moving.
        self.el1_passengers: list[Passenger] = []
        self.el2_passengers: list[Passenger] = []
        self.floor_list: list[Floor]         = [] # Info about each floor of the building.

    #####################################
    # Helper functions (if you want them)

    def get_floor(self, floor: int) -> Floor:
        assert floor >= 0 and floor < len(self.floor_list)
        return self.floor_list[floor]

    def floors(self) -> int:
        return len(self.floor_list)

    def get_el_state(self, el_id: int) -> ElevatorState:
        if el_id == 1:
            return self.el1_state
        elif el_id == 2:
            return self.el2_state
        assert not "el_id must be either 1 or 2"

    def get_el_floor(self, el_id: int) -> int:
        if el_id == 1:
            return self.el1_floor
        elif el_id == 2:
            return self.el2_floor
        assert not "el_id must be either 1 or 2"

    def get_el_target(self, el_id: int) -> int:
        if el_id == 1:
            return self.el1_target
        elif el_id == 2:
            return self.el2_target
        assert not "el_id must be either 1 or 2"

    def get_el_passengers(self, el_id: int) -> list[Passenger]:
        if el_id == 1:
            return self.el1_passengers
        elif el_id == 2:
            return self.el2_passengers
        assert not "el_id must be either 1 or 2"

    def el_at_capacity(self, el_id: int) -> bool:
        if el_id == 1:
            return len(self.el1_passengers) == 10
        elif el_id == 2:
            return len(self.el2_passengers) == 10
        assert not "el_id must be either 1 or 2"


class InstructionType(Enum):
    OpenDoor  = 0
    CloseDoor = 1
    GotoFloor = 2


class Instruction:
    ''' Example of creating the three types of instructions:
        ```python
        i0 = Instruction(1, InstructionType.OpenDoor)      # tells elevator 1 to open its doors.
        i1 = Instruction(2, InstructionType.CloseDoor)     # tells elevator 2 to close its doors.
        i2 = Instruction(2, InstructionType.GotoFloor, 13) # tells elevator 2 to go to floor 13.
        ``` '''

    def __init__(self, e_id: int, i_type: InstructionType, floor: int = -1):
        self.elevator_id = e_id
        self.type  = i_type
        self.floor = floor

    def __str__(self):
        if self.type == InstructionType.OpenDoor:
            return "OPEN_DOOR"
        elif self.type == InstructionType.CloseDoor:
            return "CLOSE_DOOR"
        else:
            return f"GOTO_FLOOR({self.floor})"


class InstructionQueue:
    ''' This queue will be read by the simulation to dispatch instructions
        to the elevators. '''

    def __init__(self):
        self._queue: list[Instruction] = []

    def push(self, inst: Instruction):
        self._queue.append(inst)


class BoardingStyle(Enum):
    JustGetOn      = 0 # Passengers will board the elevator, with priority given
                       # to the elevator's direction, but it will not stop anyone
                       # from getting on.

    BasedOnHeading = 1 # Passengers will board *only* if the elevator is heading
                       # in the same direction they wish to travel.


############
# Implement!

class MyState:
    ''' Your custom state object. Put whatever you want here! '''
    def __init__(self):
        pass

def elevator_setup() -> (any, BoardingStyle):
    ''' This function will run once at the beginning of the elevator simulation.
        Please return from this function a tuple containing whatever state you
        want passed to your `elevators_tick` function, and also the boarding
        style you wish the simulation to follow (the default is set to `JustGetOn`. '''
    return ( MyState(), BoardingStyle.JustGetOn )

def elevators_tick(
    user_state,
    status: ElevatorStatus,
    instruction_queue: InstructionQueue
):
    '''
    This function will run once per tick.

    Use the `status` object to see get info about the elevators and to see if
    floors have people waiting.

    Use the `instruction_queue` to send instructions to the two elevators. On
    the following tick the elevators will begin performing those instructions.
    For example:
    ```python
    if status.current_tick == 10:
        instruction_queue.push(Instruction(1, InstructionType.CloseDoor))
        instruction_queue.push(Instruction(1, InstructionType.GotoFloor, 13))
    ```
    This code snippet on tick 10 will tell elevator 1 to close its door and then
    go to floor 13. Elevator 1 will close its door on tick 11, and then begin
    moving on tick 12.

    You can put your entire solution in this one function, but I recommend splitting
    across functions. And don't forget to make use of your custom state object
    to create whatever data structures you want!
    '''

    state: MyState = user_state
