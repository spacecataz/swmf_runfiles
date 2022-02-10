!  Copyright (C) 2002 Regents of the University of Michigan,
!  portions used with permission
!  For more information, see http://csem.engin.umich.edu/tools/swmf
module ModVarIndexes

  use ModExtraVariables, &
       Redefine1 => Pe_, &
       Redefine2 => iPparIon_I

  implicit none

  save

  character (len=*), parameter :: NameEquationFile = "ModEquationRecircPe.f90"

  ! This equation file declares two ion fluids: a combined solar wind/polar
  ! outflow hydrogen fluid and a plasmasphere hydrogen fluid as well as
  ! electron pressure.  This allows for investigations of recirculation of
  ! plasmasphere recirculation with special coupling to CIMI.
  ! Inner boundary values must be controlled with the #MAGNETOSPHERE command.
  ! The HpPs fluid should be set to low values at the inner boundary.
  character (len=*), parameter :: NameEquation = &
       'MHD with total H+, plasmasphere H+, and electron pressure'

  integer, parameter :: nVar = 14

  integer, parameter :: nFluid    = 2
  integer, parameter :: IonFirst_ = 1
  integer, parameter :: IonLast_  = 2
  logical, parameter :: IsMhd     = .false.
  real               :: MassFluid_I(1:2) = [ 1.0, 1.0]

  character (len=5), parameter :: NameFluid_I(nFluid)= &
       [ 'Hp   ', 'HpPs ']

  ! Named indexes for State_VGB and other variables
  ! These indexes should go subsequently, from 1 to nVar+nFluid.
  ! The energies are handled as an extra variable, so that we can use
  ! both conservative and non-conservative scheme and switch between them.
  integer, parameter ::   &
       Rho_     =  1,          &
       RhoUx_   =  2, Ux_ = 2, &
       RhoUy_   =  3, Uy_ = 3, &
       RhoUz_   =  4, Uz_ = 4, &
       Bx_      =  5, &
       By_      =  6, &
       Bz_      =  7, &
       Pe_      =  8, &
       p_       =  9, &
       HpPsRho_   = 10, &
       HpPsRhoUx_ = 11, &
       HpPsRhoUy_ = 12, &
       HpPsRhoUz_ = 13, &
       HpPsP_     = 14, &
       Energy_  = nVar+1, &
       HpPsEnergy_= nVar+2

  ! This allows to calculate RhoUx_ as RhoU_+x_ and so on.
  integer, parameter :: U_ = Ux_ - 1, RhoU_ = RhoUx_-1, B_ = Bx_-1

  ! These arrays are useful for multifluid
  integer, parameter :: &
       iRho_I(nFluid)   = [Rho_,   HpPsRho_],   &
       iRhoUx_I(nFluid) = [RhoUx_, HpPsRhoUx_], &
       iRhoUy_I(nFluid) = [RhoUy_, HpPsRhoUy_], &
       iRhoUz_I(nFluid) = [RhoUz_, HpPsRhoUz_], &
       iP_I(nFluid)     = [p_,     HpPsP_]

  integer, parameter :: iPparIon_I(IonFirst_:IonLast_) = [1,2]

  ! The default values for the state variables:
  ! Variables which are physically positive should be set to 1,
  ! variables that can be positive or negative should be set to 0:
  real, parameter :: DefaultState_V(nVar+nFluid) = [ &
       1.0, & ! Rho_
       0.0, & ! RhoUx_
       0.0, & ! RhoUy_
       0.0, & ! RhoUz_
       0.0, & ! Bx_
       0.0, & ! By_
       0.0, & ! Bz_
       1.0, & ! Pe_
       1.0, & ! p_
       1.0, & ! HpPsRho_
       0.0, & ! HpPsRhoUx_
       0.0, & ! HpPsRhoUy_
       0.0, & ! HpPsRhoUz_
       1.0, & ! HpPsP_
       1.0, & ! Energy_
       1.0 ]  ! HpPsEnergy_

  ! The names of the variables used in i/o
  character(len=7) :: NameVar_V(nVar+nFluid) = [ &
       'Rho    ', & ! Rho_
       'Mx     ', & ! RhoUx_
       'My     ', & ! RhoUy_
       'Mz     ', & ! RhoUz_
       'Bx     ', & ! Bx_
       'By     ', & ! By_
       'Bz     ', & ! Bz_
       'Pe     ', & ! Pe_
       'P      ', & ! p_
       'HpPsRho', & ! HpPsRho_
       'HpPsMx ', & ! HpPsRhoUx_
       'HpPsMy ', & ! HpPsRhoUy_
       'HpPsMz ', & ! HpPsRhoUz_
       'HpPsP  ', & ! HpPsP_
       'E      ', & ! Energy_
       'HpPsE  ' ]    ! HpPsEnergy_

  ! There are no extra scalars
  integer, parameter :: ScalarFirst_ = 2, ScalarLast_ = 1

end module ModVarIndexes
!==============================================================================
