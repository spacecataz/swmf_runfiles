# Initial Condition Comparison

This input set is for creating a super-simple situation where
the impact of initial conditions can be tested on the development
of DGCPM results.

The included PARAM and Kp profile should be run twice:

- Once with the default initial conditions, where plasma outside the separatrix for low Kp is very low.

- Once with saturated condtions, where plasma flux tubes at all L-shells are full.

## Configuration
To turn on scenario 2, **comment out the following line in
`DGCPM/src/dgcpm_setup.f90`:

```
call load_restart_file(trim(filename))
```
(This is at or near line 205).