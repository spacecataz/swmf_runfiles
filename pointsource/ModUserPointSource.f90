!  Copyright (C) 2002 Regents of the University of Michigan,
!  portions used with permission
!  For more information, see http://csem.engin.umich.edu/tools/swmf
!#NOTPUBLIC  email:zghuang@umich.edu  expires:12/31/2099
module ModUser

  ! Should be 1 "implemented" for each subroutine defined, in order that
  ! changes BATS defaults (e.g., not "user_actions", etc.)
  use ModUserEmpty,               &
       IMPLEMENTED1  => user_read_inputs,                &
       IMPLEMENTED2  => user_init_session,               &
       IMPLEMENTED3  => user_calc_sources_expl,          &
       IMPLEMENTED4  => user_calc_sources_impl

  use BATL_lib, ONLY: &
       test_start, test_stop, &
       iTest, jTest, kTest, iBlockTest, iProcTest, iVarTest, iProc
  use ModSize
  use ModNumConst,  ONLY: cPi, cTiny
  use ModAdvance,   ONLY: Pe_, UseElectronPressure
  use ModMultiFluid

  include 'user_module.h' ! list of public methods

  ! Here you must define a user routine Version number and a
  ! descriptive string.
  character (len=*), parameter :: NameUserFile = "ModUserPointSource.f90"
  character (len=*), parameter :: NameUserModule = &
       'Point mass source; DTW 2024'

  ! DTW Variable defs
  real :: XyzSource(3) = 0  ! Location of point sources.
  ! ---------

  ! Use the CG shape or not. If not, then use a spherical body.
  logical :: DoUseCGShape = .true.
  real    :: rSphericalBodySi = 2.0e3
  real    :: rSphericalBody

  integer:: nTriangle
  real, allocatable:: XyzTriangle_DII(:,:,:), Normal_DI(:,:)
  real :: rMinShape = 0.0, rMaxShape = 0.0

  ! Position of the sun at the start time
  real :: LatSun=43.5, LonSun=0.0
  real :: NormalSun_D(3)

  ! Rotation matrix to rotate the comet so that the Sun is in the +x direction.
  real:: Rot_DD(3,3) = 0.

  ! Rotation of the comet (changes the direction of the Sun)
  real:: RotationCometHour = 12.0

  ! Angular velocity
  real:: OmegaComet

  ! Maximum change in longitude before updating the boundary conditions
  real:: AngleUpdateDeg = 10.0

  ! The time between updates
  real:: DtUpdateSi

  ! minimum and maximum temperature
  real :: TempCometMinDim, TempCometMaxDim, TempCometMin, TempCometMax

  ! Temperature at 75.5 degree to determin the temperature slope
  real :: TempComet75Dim, TempComet75

  ! Minimum and maximum production rate
  real :: ProductionRateMaxSi, ProductionRateMinSi
  real :: ProductionRateMax, ProductionRateMin

  ! Maximum solar zenith angle for dayside production rate
  real :: SolarAngleMaxDim, SolarAngleMax

  ! Parameters for y=ax+b to mimic the production rate and
  ! temperature distribution
  real :: SlopeProduction, bProduction, SlopeTemp, bTemp

  ! Constant parameters to calculate uNormal and temperature
  ! from TempCometLocal
  real :: TempToUnormal
  real :: TempToPressure

  ! Inner boundary condition for ions
  character (len=10) :: TypeBodyBC = 'default'
  logical :: UseSwBC        = .false.
  logical :: UseReflectedBC = .false.

  ! Inner boundary condition for magnetic field
  character (len=10) :: TypeBfieldBody = 'zero'

  ! Perturbed initial condition parameters:
  real :: R0PerturbedSi  = 1e6, R0Perturbed
  real :: R1PerturbedSi  = 2e6, R1Perturbed
  real :: ratioPerturbed = 1e-10

  ! Parameters to increase the neutral density in the source term to
  ! approach the steady state solution more easily (hopefully)
  logical :: DoEnhanceNeu    = .false.
  real    :: EnhancedRatio   = 20
  integer :: DecadeDn        = 10000
  integer :: nStepEnhanceNeu = -100

  ! minimum temperature for neutral
  real :: TempNeuMinSi = 60.0, TempNeuMin

  ! FaceCoordsTest_D
  real :: FaceCoordsX=0.0, FaceCoordsY=0.0, FaceCoordsZ=0.0
  real :: FaceCoordsTest_D(3) = [0.0, 0.0, 0.0]

  ! Last step and time the inner boundary values were saved for each block
  integer, allocatable :: nStepSave_B(:)

  real, allocatable :: TimeSimulationSave_B(:)

  integer, allocatable :: nStepSaveCalcRates_B(:)
  integer :: nStepPritSetFace = -100

  ! If this variable is set .true., then use the Haser neutral background
  ! Only for testing purpose
  logical :: DoUseHaserBackground = .false.

  ! If this variable is set .true., then use the uniform neutral background
  ! Only for testing purpose
  logical :: DoUseUniformNeuBackground = .false.
  real :: nNeuUniformSi, UxNeuUniformSi, UyNeuUniformSi, UzNeuUniformSi, &
       TNeuUniformSi
  real :: nNeuUniform, UxNeuUniform, UyNeuUniform, UzNeuUniform, &
       pNeuUniform

  ! Increase ionization near a field line
  logical :: DoUseFieldlineFile = .false.
  character (len=100) :: NameFieldlineFile
  integer :: nVarFieldlineFile
  real    :: RadiusTubeSI, RadiusTube, SPeAdditionalSi=5.0e-9, SPeAdditional
  real, allocatable::  XyzFieldline_DI(:,:)
  real    :: TimeEnhanceStartSI = 180.0, TimeEnhanceEndSI = 240.0
  real    :: TimeEnhanceStart, TimeEnhanceEnd

  integer, parameter, public :: nNeuFluid = 1
  integer, parameter :: Neu1_  =  1

  !! Ion species names
  integer, parameter :: SW_   =  1
  integer, parameter :: H2Op_ =  2

  real :: Qprod = 1e22
  real :: TminSi, Tmin, rHelio, vHI, uHaser

  real, allocatable :: ne20eV_GB(:,:,:,:)

  !! logical variable to determine whether to use an artifical perturbed solar
  !! wind at beyond a certain xPerturbedSwIO
  logical :: UsePerturbedSW = .false.
  real :: xPerturbedSwMinIO = 1.5e4, xPerturbedSwMaxIO = 1.6e4
  real :: PerturbedSwNIO = 10.0
  real :: PerturbedSwUxIO = 400.0, PerturbedSwUyIO = 0.0, PerturbedSwUzIO = 0.0
  real :: PerturbedSwTIO = 1.5e5, PerturbedSwTeIO = 1.5e5
  real :: PerturbedSwBxIO = 5.0, PerturbedSwByIO = 0.0, PerturbedSwBzIO = 0.0
  real :: xPerturbedSwMin, xPerturbedSwMax, PerturbedSwN, PerturbedSwRho
  real :: PerturbedSwT,  PerturbedSwTe
  real :: PerturbedSwUx, PerturbedSwUy, PerturbedSwUz
  real :: PerturbedSwBx, PerturbedSwBy, PerturbedSwBz

  !! Make the photo- and electron impact ionization rate global arrays for
  !! user_set_plot_var
  real, allocatable :: v_IIGB(:,:,:,:,:,:), ve_IIGB(:,:,:,:,:,:)

  logical            :: DoSaveSource = .false.
  character (len=10) :: NameSource   = 'none'
  real, allocatable :: TestArray_IGB(:,:,:,:,:)

  real, allocatable :: SPeAdditional_GB(:,:,:,:)

  character (len=6), parameter, public :: NameNeutral_I(nNeuFluid) = &
       [ 'Neu1  ' ]

contains
  !============================================================================
  subroutine user_action(NameAction)

    character(len=*), intent(in):: NameAction

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_action'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest)
    if (NameAction /= 'initialize module' .and. NameAction /= 'clean module') &
         RETURN
    if(iProc==0)write(*,*) NameSub,' called with action ',NameAction
    select case(NameAction)
    case('initialize module')
       ! Do shit here.
    case('clean module')
       ! Do shit here.
    end select
    call test_stop(NameSub, DoTest)
  end subroutine user_action
  !============================================================================
  subroutine user_read_inputs

    use ModReadParam

    character (len=100) :: NameCommand

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_read_inputs'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest)

    do
       if(.not.read_line() ) EXIT
       if(.not.read_command(NameCommand)) CYCLE
       select case(NameCommand)
       case("#SHAPEFILE")
          call read_var('NameShapeFile' ,NameShapeFile)
       case('#USERINPUTEND')
          EXIT
       case default
          if(iProc==0) call stop_mpi( &
               NameSub//' invalid command='//trim(NameCommand))
       end select
    end do

    call test_stop(NameSub, DoTest)
  end subroutine user_read_inputs
  !============================================================================
  subroutine user_init_session

    ! Read shape file and convert units

    use ModMain, ONLY: tSimulation, nStep
    use ModPhysics, ONLY: Io2No_V, Si2No_V, No2Si_V, &
         UnitU_, UnitTemperature_, UnitT_, UnitP_,   &
         UnitN_, UnitX_, UnitB_, UnitEnergyDens_
    use ModNumConst, ONLY: cTwoPi, cDegToRad
    use ModCoordTransform, ONLY: dir_to_xyz
    use ModConst, ONLY: cBoltzmann, cAtomicMass
    use ModVarIndexes, ONLY: MassFluid_I
    use ModBlockData, ONLY: MaxBlockData
    use ModIO, ONLY: IsRestart
    use ModCoordTransform, ONLY: rot_matrix_y, rot_matrix_z

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_init_session'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest)

    ! Obtained the rotation matrix from LatSun and LonSun
    Rot_DD = matmul( rot_matrix_z(-LonSun*cDegToRad), &
         rot_matrix_y(LatSun*cDegToRad) )

    ! Now the Sun is in the +x direction
    LatSun = 0
    LonSun = 0

    ! Test statement, need to remove later
    if (iProc == 0) then
       write(*,*) 'Hey the user module is working.'
    end if

    call test_stop(NameSub, DoTest)
  end subroutine user_init_session
  !============================================================================

  subroutine user_calc_sources_impl(iBlock)

    use ModMain,       ONLY: nI, nJ, nK, tSimulation
    use ModAdvance,    ONLY: State_VGB, Source_VC, Bx_, By_, Bz_, P_
    use ModConst,      ONLY: cBoltzmann, cElectronMass, cProtonMass, cEV
    use ModGeometry,   ONLY: Xyz_DGB
    use ModCurrent,    ONLY: get_current
    use ModPhysics,    ONLY: Si2No_V, No2Si_V, &
         UnitEnergyDens_, UnitN_, UnitRho_, UnitU_, UnitP_, UnitT_, &
         UnitRhoU_, UnitTemperature_, UnitX_,       &
         ElectronPressureRatio, ElectronCharge
    use ModVarIndexes,    ONLY: MassFluid_I
    use ModBlockData,     ONLY: use_block_data, get_block_data, put_block_data

    integer, intent(in) :: iBlock

    integer :: iPoint, i, j, k
    real, dimension(1:nI,1:nJ,1:nK) :: distSource_C = 0

    ! Local source arrays
    real, dimension(1:nI,1:nJ,1:nK) :: SRho_C, SP_C
    !------

    integer, parameter :: nRhoTerm=5, nRhoUTerm=7, nPTerm=11, nPeTerm =10

    real, dimension(1:nI,1:nJ,1:nK) :: nElec_C, Te_C, SBx_C, SBy_C, SBz_C, &
         SPe_C, TempNeu1_C, nNeu1_C

    real, dimension(nRhoTerm, 1:nIonFluid,1:nI,1:nJ,1:nK) :: SRhoTerm_IIC
    real, dimension(nRhoUTerm,1:nIonFluid,1:nI,1:nJ,1:nK) :: SRhoUxTerm_IIC, &
         SRhoUyTerm_IIC, SRhoUzTerm_IIC
    real, dimension(nPTerm,1:nIonFluid,1:nI,1:nJ,1:nK) :: SPTerm_IIC
    real, dimension(nPeTerm,           1:nI,1:nJ,1:nK) :: SPeTerm_IC

    real, dimension(1:3,1:nIonFluid,1:nI,1:nJ,1:nK) :: uIon_DIC

    real, dimension(1:3,1:nI,1:nJ,1:nK) :: Current_DC, uIonMean_DC, uElec_DC, &
         uNeu1_DC

    real, dimension(1:nIonFluid,1:nIonFluid,1:nI,1:nJ,1:nK) :: &
         fii_IIC, uIonIon2_IIC

    real, dimension(1:nIonFluid,            1:nI,1:nJ,1:nK) :: alpha_IC
    real, dimension(1:nIonFluid,1:nNeuFluid, 1:nI,1:nJ,1:nK) :: &
         fin_IIC, uIonNeu2_IIC
    real, dimension(            1:nNeuFluid, 1:nI,1:nJ,1:nK) :: &
         fen_IC, uNeuElec2_IC

    real, dimension(1:nNeuFluid,1:nIonFluid) :: Qexc_II, Qion_II

    real, dimension(1:nIonFluid) :: fiiTot_I, finTot_I, vAdd_I, veAdd_I, &
         kinAdd_I, kinSub_I
    !--------------------------------------------------------------------------
    real, dimension &
         (1:nIonFluid,1:nNeuFluid,1:nNeuFluid,1:nIonFluid,1:nI,1:nJ,1:nK) :: &
         kin_IIIIC

    real    :: fenTot, feiTot
    integer :: i,j,k,iNeuFluid,jNeutral,iIonFluid,jIonFluid,iTerm

    logical :: DoTestCell
    logical :: DoCalcShading = .false.
    integer, save :: iBlockLast = -100
    integer, save :: iLastDecomposition = -100
    real,    save :: IsIntersectedShapeR_III(nI,nJ,nK) = -1.0

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_calc_sources_impl'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest, iBlock)

    if (iNewDecomposition /= iLastDecomposition) then
       iBlockLast         = -100
       iLastDecomposition = iNewDecomposition
    end if

    !! Set the source arrays for this block to zero
    SRho_C = 0.
    SP_C = 0.

    do iPoint=1, nPointSource
    end do

    ! Check time to see if source is active.
    ! HERE!

    ! Calculate source:
    do k=1,nK; do j=1,nJ; do i=1,nI
       ! For each point, get distance from point.
       distSource_C = sqrt(sum((Xyz_GB(:,i, j, k, iBlock) - XyzSource)**2))

       SRho_C =
    end do; end do; end do

    do k=1,nK; do j=1,nJ; do i=1,nI
       Source_VC(iRhoIon_I   ,i,j,k) = SRho_IC(i,j,k)    + &
            Source_VC(iRhoIon_I   ,i,j,k)
       Source_VC(iPIon_I     ,i,j,k) = SP_IC(1:nIonFluid,i,j,k)      + &
            Source_VC(iPIon_I     ,i,j,k)
    end do;  end do;  end do

    call test_stop(NameSub, DoTest, iBlock)

  end subroutine user_calc_sources_impl
  !============================================================================
  subroutine user_calc_sources_expl(iBlock)

    integer, intent(in) :: iBlock

    !--------------------------------------------------------------------------
  end subroutine user_calc_sources_expl
  !============================================================================

end module ModUser
!==============================================================================
