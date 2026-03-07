# Computer Club W26 Programming Competition - The Elevator Challenge

Welcome to the Winter 2026 programming competition!
The theme for this programming challenge is "The Elevator Challenge".

Your task is to write the controller for a system of two elevators that must
deliver passengers to their desired location. This simulation runs in "ticks":
on each tick the elevators will update based on their instructions and passengers
may arrive at different floors asking for transportation. You will earn points
for delivering all passengers before the deadline (1920 ticks). You will also
earn points based on how speedily the passengers' waits and trips are.

## Passengers

### Boarding

Each tick, there is a chance that a passenger will appear on a floor of the
building. If an elevator is present, and the doors are open, the passenger will
board the elevator based on two styles:

* `JustGetOn`      : Passenger will board if there is space available.
* `BasedOnHeading` : Passenger will board only if the elevator is moving in the
                     direction the passenger wishes to go.

Only one passenger can board an elevator per tick.

### Exiting

If the elevator has its doors open at a passengers target floor, the passenger
will leave. Any number of passengers can leave the elevator per tick.

## Elevators

You have two elevators to work with. In order to control the elevators, you send
instructions, which will be processed FIFO.

## Internet / AI Usage.

Using AI is against the spirit of this competition, but sometimes it is nice to
google something about python specifics. You are free to talk to your competitors
and ask them, and also Aiden will be available to approve Google searches or
answer any questions you may have.

## Grading

Once all passengers have been transportation, or once the deadline is hit, the
simulation will stop and then report your grade. Points will be assigned for
various metrics. However, there are addition ways to get/lose points outside of
your autograded score:

* Each bug you catch and report to Aiden (that hasn't already been reported) is
  worth 200 points each.
* Using unauthorized internet/AI will result in the deduction of 1500 points.
* Each minute that passes after your submission (before the deadline) will count as 5 points.

Your submission will be scored against 3 grading seeds and then the resulting
scores will be averaged and then added to any additional points earned.
