# St. Patrick's Day Storm, 2015

This set of runfiles is to simulate the St. Pats day storm with and
without GITM.

For GITM, consider decreasing these numbers to get better electrodynamics
resolution (esp. the longitude!):

```
  real :: MagLatRes = 0.5
  real :: MagLonRes = 4.0
```

## IMF Input

Data was obtained from the [Merged Interplanetary Data Library](https://csem.engin.umich.edu/MIDL/download.html).

## Notes on GITM Params

Params for the GITM section are based on testing from June/July 2026 with Ari Gottesman and Aaron Bukowski.