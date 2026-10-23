!  Copyright (C) 2002 Regents of the University of Michigan,
!  portions used with permission
!  For more information, see http://csem.engin.umich.edu/tools/swmf

! This module is for simple PS->GM coupling. The 2nd fluid, HpPs, is
! interpreted as plasmaspheric protons.

module ModVarIndexes

  use ModExtraVariables, &
       Redefine => iPparIon_I

  implicit none

  save

  character (len=*), parameter :: &
       NameEquationFile = "ModEquationMultiIonPs.f90"

  character (len=*), parameter :: &
       NameEquation = 'Multi-ion MHD with Hp and HpPs for PS->GM Coupling'

  integer, parameter :: nVar = 13

  ! There are two ion fluids but no total ion fluid
  integer, parameter :: nFluid    = 2
  integer, parameter :: nIonFluid = 2
  logical, parameter :: IsMhd     = .false.
  real               :: MassFluid_I(nFluid) = [ 1.0, 1.0 ]

  character (len=3), parameter :: NameFluid_I(nFluid) = [ 'SwH', 'Hp ' ]

  ! Named indexes for State_VGB and other variables
  ! These indexes should go subsequently, from 1 to nVar+nFluid.
  ! The energies are handled as an extra variable, so that we can use
  ! both conservative and non-conservative scheme and switch between them.
  integer, parameter :: &
       Rho_     =  1,          &
       RhoUx_   =  2, Ux_ = 2, &
       RhoUy_   =  3, Uy_ = 3, &
       RhoUz_   =  4, Uz_ = 4, &
       Bx_        =  5, &
       By_        =  6, &
       Bz_        =  7, &
       p_       =  8, &
       HpRho_     =  9, &
       HpRhoUx_   = 10, &
       HpRhoUy_   = 11, &
       HpRhoUz_   = 12, &
       HpP_       = 13, &
       Energy_  = nVar+1, &
       HpEnergy_  = nVar+2

  ! This allows to calculate RhoUx_ as RhoU_+x_ and so on.
  integer, parameter :: U_ = Ux_ - 1, RhoU_ = RhoUx_-1, B_ = Bx_-1

  ! These arrays are useful for multifluid
  integer, parameter :: iRho_I(nFluid)   = [Rho_,   HpRho_]
  integer, parameter :: iRhoUx_I(nFluid) = [RhoUx_, HpRhoUx_]
  integer, parameter :: iRhoUy_I(nFluid) = [RhoUy_, HpRhoUy_]
  integer, parameter :: iRhoUz_I(nFluid) = [RhoUz_, HpRhoUz_]
  integer, parameter :: iP_I(nFluid)     = [p_,     HpP_]

  integer, parameter :: iPparIon_I(nIonFluid) = [1,2]

  ! The default values for the state variables:
  ! Variables which are physically positive should be set to 1,
  ! variables that can be positive or negative should be set to 0:
  real, parameter :: DefaultState_V(nVar+nFluid) = [ &
       1.0, & ! SwRho_
       0.0, & ! SwRhoUx_
       0.0, & ! SwRhoUy_
       0.0, & ! SwRhoUz_
       0.0, & ! SwBx_
       0.0, & ! SwBy_
       0.0, & ! SwBz_
       1.0, & ! SwP_
       1.0, & ! HpRho_
       0.0, & ! HpRhoUx_
       0.0, & ! HpRhoUy_
       0.0, & ! HpRhoUz_
       1.0, & ! HpP_
       1.0, & ! SwEnergy_
       1.0 ]  ! HpEnergy_

  ! The names of the variables used in i/o
  character(len=7) :: NameVar_V(nVar+nFluid) = [ &
       'SwHRho', & ! Rho_
       'SwHMx ', & ! RhoUx_
       'SwHMy ', & ! RhoUy_
       'SwHMz ', & ! RhoUz_
       'Bx    ', & ! Bx_
       'By    ', & ! By_
       'Bz    ', & ! Bz_
       'SwHP  ', & ! p_
       'HpRho ', & ! HpRho_
       'HpMx  ', & ! HpRhoUx_
       'HpMy  ', & ! HpRhoUy_
       'HpMz  ', & ! HpRhoUz_
       'HpP   ', & ! HpP_
       'SwHE  ', & ! Energy_
       'HpE   ' ]  ! HpEnergy_

  ! There are no extra scalars
  integer, parameter :: ScalarFirst_ = 2, ScalarLast_ = 1

end module ModVarIndexes
!==============================================================================
