# Tsurutani & Lakhina Propagation

These run files take the step-function interpretation of the
Tsurutani & Lakhina "Worst Case Scenario" CME characteristics and allow them
to propagate down an MHD box to investigate the evolution of the front,
including the formation of the sheath.

## PARAM Considerations
Start and end time are based on the amount of time it should take for the solar wind conditions to travel the length of the simulation domain (~78 minutes at 350km/s; ~10 minutes at 2700 km/s).
Unlike the Welling et al. [2021] paper, no south-north-south IMF preconditioning step is used.
Half RE grid spacing is used everywhere.
