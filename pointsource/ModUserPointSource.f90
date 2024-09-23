!  Copyright (C) 2002 Regents of the University of Michigan,
!  portions used with permission
!  For more information, see http://csem.engin.umich.edu/tools/swmf
!#NOTPUBLIC  email:zghuang@umich.edu  expires:12/31/2099
module ModUser

  ! Should be 1 "implemented" for each subroutine defined, in order that
  ! changes BATS defaults (e.g., not "user_actions", etc.)
  use ModUserEmpty,               &
       IMPLEMENTED1  => user_set_boundary_cells,         &
       IMPLEMENTED2  => user_read_inputs,                &
       IMPLEMENTED3  => user_init_session,               &
       IMPLEMENTED4  => user_set_face_boundary,          &
       IMPLEMENTED5  => user_calc_sources_expl,          &
       IMPLEMENTED6  => user_calc_sources_impl,          &
       IMPLEMENTED7  => user_update_states,              &
       IMPLEMENTED8  => user_set_resistivity,            &
       IMPLEMENTED9  => user_material_properties,        &
       IMPLEMENTED10 => user_init_point_implicit,        &
       IMPLEMENTED11 => user_set_plot_var,               &
       IMPLEMENTED12 => user_set_ICs,                    &
       IMPLEMENTED13 => user_get_log_var,                &
       IMPLEMENTED14 => user_set_cell_boundary,          &
       IMPLEMENTED15 => user_amr_criteria,               &
       IMPLEMENTED16 => user_initial_perturbation,       &
       IMPLEMENTED17 => user_action

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
  character (len=*), parameter :: NameUserFile = "ModUserCometCGfluids.f90"
  character (len=*), parameter :: NameUserModule = &
       'CG Comet, Z. Huang and G. Toth'

  character (len=100) :: NameShapeFile

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
       if(.not.allocated(nStepSave_B)) then
          allocate(nStepSave_B(MaxBlock))
          nStepSave_B = -100
          allocate(TimeSimulationSave_B(MaxBlock))
          TimeSimulationSave_B = -1e30
          allocate(nStepSaveCalcRates_B(MaxBlock))
          nStepSaveCalcRates_B = -100
          allocate(ne20eV_GB(MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
          ne20eV_GB = 0.
          allocate(SPeAdditional_GB(MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
          SPeAdditional_GB =0.0
          allocate(v_IIGB(nNeuFluid,nIonFluid,&
               MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
          allocate(ve_IIGB(1:nNeuFluid,1:nIonFluid, &
               MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
          allocate(TestArray_IGB(8, MinI:MaxI,MinJ:MaxJ,MinK:MaxK,MaxBlock))
          TestArray_IGB = 0.0
       end if
    case('clean module')
       if(allocated(nStepSave_B)) deallocate(nStepSave_B)
       if(allocated(TimeSimulationSave_B)) deallocate(TimeSimulationSave_B)
       if(allocated(nStepSaveCalcRates_B)) deallocate(nStepSaveCalcRates_B)
       if(allocated(ne20eV_GB)) deallocate(ne20eV_GB)
       if(allocated(SPeAdditional_GB)) deallocate(SPeAdditional_GB)
       if(allocated(v_IIGB)) deallocate(v_IIGB)
       if(allocated(ve_IIGB)) deallocate(ve_IIGB)
       if(allocated(TestArray_IGB)) deallocate(TestArray_IGB)
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

    use ModMain,       ONLY: nI, nJ, nK,    &
         nStep, tSimulation, iNewDecomposition
    use ModAdvance,    ONLY: State_VGB, Source_VC, &
         Bx_,By_,Bz_, P_
    use ModConst,      ONLY: cBoltzmann, cElectronMass, cProtonMass, cEV
    use ModGeometry,   ONLY: r_GB, Xyz_DGB
    use ModCurrent,    ONLY: get_current
    use ModPhysics,    ONLY: Si2No_V, No2Si_V, &
         UnitEnergyDens_, UnitN_, UnitRho_, UnitU_, UnitP_, UnitT_, &
         UnitRhoU_, UnitTemperature_, UnitX_,       &
         ElectronPressureRatio, ElectronCharge
    use ModVarIndexes,    ONLY: MassFluid_I
    use ModBlockData,     ONLY: use_block_data, get_block_data, put_block_data

    integer, intent(in) :: iBlock

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
    real, dimension(1:nIonFluid,            1:nI,1:nJ,1:nK) :: &
         Ti_IC, uIonElec2_IC, fei_IC, fie_IC, &
         nIon_IC, SRho_IC, SRhoUx_IC, SRhoUy_IC, SRhoUz_IC, SP_IC
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

    logical :: DoCalcDistance2Fieldline = .false.
    real,    save :: IsWithinTheRingR_III(nI,nJ,nK) = -1.0

    ! OpenMP declarations
    !$omp threadprivate( DoCalcShading )
    !$omp threadprivate( iBlockLast,iLastDecomposition )
    !$omp threadprivate( IsIntersectedShapeR_III )
    !$omp threadprivate( IsWithinTheRingR_III )
    !$omp threadprivate( DoCalcDistance2Fieldline )

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_calc_sources_impl'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest, iBlock)

    if (iNewDecomposition /= iLastDecomposition) then
       iBlockLast         = -100
       iLastDecomposition = iNewDecomposition
    end if

    !! Set the source arrays for this block to zero
    SRho_IC        = 0.
    SRhoTerm_IIC   = 0.
    SRhoUx_IC      = 0.
    SRhoUxTerm_IIC = 0.
    SRhoUy_IC      = 0.
    SRhoUyTerm_IIC = 0.
    SRhoUz_IC      = 0.
    SRhoUzTerm_IIC = 0.
    SBx_C          = 0.
    SBy_C          = 0.
    SBz_C          = 0.
    SP_IC          = 0.
    SPTerm_IIC     = 0.
    SPe_C          = 0.
    SPeTerm_IC     = 0.

    do k=1,nK; do j=1,nJ; do i=1,nI
       if (DoUseHaserBackground) then
          if (r_GB(i,j,k,iBlock) > rSphericalBody) then
             State_VGB(Neu1Rho_,i,j,k,iBlock) = Qprod/                        &
                  (4.*cPi*(r_GB(i,j,k,iBlock)*No2Si_V(UnitX_))**2*uHaser ) * &
                  exp(-vHI*r_GB(i,j,k,iBlock)*No2Si_V(UnitX_)/uHaser)*       &
                  Si2No_V(UnitN_) * MassFluid_I(nFluid)
             State_VGB(Neu1Ux_:Neu1Uz_,i,j,k,iBlock) =                     &
                  State_VGB(Neu1Rho_,i,j,k,iBlock)*uHaser*Si2No_V(UnitU_)* &
                  Xyz_DGB(:,i,j,k,iBlock)/r_GB(i,j,k,iBlock)
             State_VGB(Neu1P_,i,j,k,iBlock)     =                          &
                  State_VGB(Neu1Rho_,i,j,k,iBlock)/MassFluid_I(nFluid)     &
                  *TempNeuMinSi*Si2No_V(UnitTemperature_)
          else
             State_VGB(Neu1Rho_,i,j,k,iBlock) = Qprod/                  &
                  (4.*cPi*rSphericalBodySi**2*uHaser )*                 &
                  exp(-vHI*rSphericalBodySi/uHaser)*                    &
                  Si2No_V(UnitN_) * MassFluid_I(nFluid)
             State_VGB(Neu1Ux_:Neu1Uz_,i,j,k,iBlock) = 0.0
             State_VGB(Neu1P_,i,j,k,iBlock)     =                       &
                  State_VGB(Neu1Rho_,i,j,k,iBlock)/MassFluid_I(nFluid)  &
                  *TempNeuMinSi*Si2No_V(UnitTemperature_)
          end if
       else if (DoUseUniformNeuBackground) then
          State_VGB(Neu1Rho_,i,j,k,iBlock) = nNeuUniform*MassFluid_I(nFluid)
          State_VGB(Neu1Ux_, i,j,k,iBlock) = UxNeuUniform
          State_VGB(Neu1Uy_, i,j,k,iBlock) = UyNeuUniform
          State_VGB(Neu1Uz_, i,j,k,iBlock) = UzNeuUniform
          State_VGB(Neu1P_,  i,j,k,iBlock) = pNeuUniform
       end if
    end do; end do; end do

    ! nElec_C is the electron/ion density in SI units ( n_e=sum(n_i*Zi) )
    do k=1,nK; do j=1,nJ; do i=1,nI
       nIon_IC(1:nIonFluid,i,j,k) = &
            State_VGB(iRhoIon_I,i,j,k,iBlock)/MassIon_I*No2SI_V(UnitN_)
       nElec_C(i,j,k) = &
            sum(nIon_IC(1:nIonFluid,i,j,k)*ChargeIon_I(1:nIonFluid))
    end do; end do; end do

    ! ion velocity components in SI
    uIon_DIC(1,1:nIonFluid,1:nI,1:nJ,1:nK) = &
         State_VGB(iRhoUxIon_I,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(iRhoIon_I,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)
    uIon_DIC(2,1:nIonFluid,1:nI,1:nJ,1:nK) = &
         State_VGB(iRhoUyIon_I,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(iRhoIon_I,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)
    uIon_DIC(3,1:nIonFluid,1:nI,1:nJ,1:nK) = &
         State_VGB(iRhoUzIon_I,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(iRhoIon_I,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)
    uIonMean_DC(1:3,1:nI,1:nJ,1:nK) = 0.

    do iIonFluid=1,nIonFluid
       uIonMean_DC(1,1:nI,1:nJ,1:nK) = uIonMean_DC(1,1:nI,1:nJ,1:nK) + &
            nIon_IC(   iIonFluid,1:nI,1:nJ,1:nK) * &
            uIon_DIC(1,iIonFluid,1:nI,1:nJ,1:nK) * ChargeIon_I(iIonFluid) / &
            nElec_C(1:nI,1:nJ,1:nK)
       uIonMean_DC(2,1:nI,1:nJ,1:nK) = uIonMean_DC(2,1:nI,1:nJ,1:nK) + &
            nIon_IC(   iIonFluid,1:nI,1:nJ,1:nK)* &
            uIon_DIC(2,iIonFluid,1:nI,1:nJ,1:nK) * ChargeIon_I(iIonFluid) / &
            nElec_C(1:nI,1:nJ,1:nK)
       uIonMean_DC(3,1:nI,1:nJ,1:nK) = uIonMean_DC(3,1:nI,1:nJ,1:nK) + &
            nIon_IC(   iIonFluid,1:nI,1:nJ,1:nK)* &
            uIon_DIC(3,iIonFluid,1:nI,1:nJ,1:nK) * ChargeIon_I(iIonFluid) / &
            nElec_C(1:nI,1:nJ,1:nK)
    end do

    ! Neu1 velocity componet in SI
    uNeu1_DC(1, 1:nI,1:nJ,1:nK) = &
         State_VGB(Neu1RhoUx_,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(Neu1Rho_,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)
    uNeu1_DC(2, 1:nI,1:nJ,1:nK) = &
         State_VGB(Neu1RhoUy_,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(Neu1Rho_,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)
    uNeu1_DC(3, 1:nI,1:nJ,1:nK) = &
         State_VGB(Neu1RhoUz_,1:nI,1:nJ,1:nK,iBlock) / &
         State_VGB(Neu1Rho_,  1:nI,1:nJ,1:nK,iBlock) *No2SI_V(UnitU_)

    ! Neu1 temperature in SI
    TempNeu1_C = State_VGB(Neu1P_,1:nI,1:nJ,1:nK,iBlock)* &
         MassFluid_I(nFluid)/State_VGB(Neu1Rho_,1:nI,1:nJ,1:nK,iBlock) * &
         No2SI_V(UnitTemperature_)

    ! Neu1 density in SI
    if (DoEnhanceNeu) then
       nNeu1_C  = State_VGB(Neu1Rho_,1:nI,1:nJ,1:nK,iBlock) &
            / MassFluid_I(nFluid)*No2SI_V(UnitN_) &
            * max((EnhancedRatio*(DecadeDn+nStepEnhanceNeu-nStep))/DecadeDn,&
            1.0)
    else
       nNeu1_C  = State_VGB(Neu1Rho_,1:nI,1:nJ,1:nK,iBlock) &
            / MassFluid_I(nFluid)*No2SI_V(UnitN_)
    end if

    ! (u_i-u_n)^2 in SI
    do iIonFluid=1,nIonFluid
       do iNeuFluid=1,nNeuFluid
          uIonNeu2_IIC(iIonFluid,iNeuFluid,1:nI,1:nJ,1:nK) = &
               (uIon_DIC(1,iIonFluid,1:nI,1:nJ,1:nK) - &
               uNeu1_DC( 1,          1:nI,1:nJ,1:nK))**2 + &
               (uIon_DIC(2,iIonFluid,1:nI,1:nJ,1:nK) - &
               uNeu1_DC( 2,          1:nI,1:nJ,1:nK))**2 + &
               (uIon_DIC(3,iIonFluid,1:nI,1:nJ,1:nK) - &
               uNeu1_DC( 3,          1:nI,1:nJ,1:nK))**2
       end do
    end do

    !! (u_i1-u_i2)^2 in SI
    do iIonFluid=1,nIonFluid
       do jIonFluid=1,nIonFluid
          uIonIon2_IIC(iIonFluid,jIonFluid,:,:,:) = &
               (uIon_DIC(1,iIonFluid,1:nI,1:nJ,1:nK) - &
               uIon_DIC( 1,jIonFluid,1:nI,1:nJ,1:nK))**2+&
               (uIon_DIC(2,iIonFluid,1:nI,1:nJ,1:nK) - &
               uIon_DIC( 2,jIonFluid,1:nI,1:nJ,1:nK))**2+&
               (uIon_DIC(3,iIonFluid,1:nI,1:nJ,1:nK) - &
               uIon_DIC( 3,jIonFluid,1:nI,1:nJ,1:nK))**2
       end do
    end do

    if (UseElectronPressure) then
       ! Electron temperature calculated from electron pressure
       ! Ion temperature is calculated from ion pressure
       do k=1,nK; do j=1,nJ; do i=1,nI
          Ti_IC(1:nIonFluid,i,j,k) = &
               State_VGB(iPIon_I,i,j,k,iBlock)*NO2SI_V(UnitP_) / &
               (cBoltzmann* &
               State_VGB(iRhoIon_I,i,j,k,iBlock)/MassIon_I*NO2SI_V(UnitN_))
          Te_C(i,j,k) = State_VGB(Pe_,i,j,k,iBlock)*NO2SI_V(UnitP_) / &
               (cBoltzmann*nElec_C(i,j,k))
       end do; end do; end do
    else
       ! Electron temperature calculated from pressure
       ! assuming Te_C=Ti_IC*ElectronTemperatureRatio:
       ! p=nkT with n_e=n_i*Z_i (quasi-neutrality),
       ! n=n_e+n_i and p=p_e+p_i=p_i*(1+ElectronPressureRatio)
       do k=1,nK; do j=1,nJ; do i=1,nI
          Ti_IC(1:nIonFluid,i,j,k) = &
               State_VGB(iPIon_I,i,j,k,iBlock)*NO2SI_V(UnitP_)/ &
               (cBoltzmann* &
               State_VGB(iRhoIon_I,i,j,k,iBlock)/MassIon_I*NO2SI_V(UnitN_))
          Te_C(i,j,k) = State_VGB(P_,i,j,k,iBlock)*ElectronPressureRatio / &
               (1.+ElectronPressureRatio)*NO2SI_V(UnitP_) / &
               (cBoltzmann*nElec_C(i,j,k))
       end do; end do; end do
    end if

    if (iBlock /= iBlockLast) then
       iBlocklast = iBlock
       if (use_block_data(iBlock) .and. .not. DoCalcShading) then
          call get_block_data(iBlock,nI,nJ,nK, IsIntersectedShapeR_III)
          !          write(*,*) 'iProc, iBlock get block data: ', iProc, iBlock, nStep
       end if

       if (use_block_data(iBlock) .and. .not.  DoCalcDistance2Fieldline) then
          call get_block_data(iBlock,nI,nJ,nK, IsWithinTheRingR_III)
          ! write(*,*) 'getting block data for IsWithinTheRingR_III'
       end if

       if (.not. use_block_data(iBlock)) then
          DoCalcShading = .true.
          DoCalcDistance2Fieldline = .true.
          if (iProc == 1 .and. iBlock ==1) &
               write(*,*) 'Calculating the distance to the field line.'
       end if
    end if

    do k=1,nK; do j=1,nJ; do i=1,nI

       DoTestCell = DoTest .and. i == iTest .and. j == jTest .and. k == kTest

       call get_current(i,j,k,iBlock,Current_DC(:,i,j,k))

       ! calculate uElec_DC from Hall velocity -J/(e*n) [m/s]
       uElec_DC(1:3,i,j,k) = uIonMean_DC(1:3,i,j,k) - &
            Current_DC(1:3,i,j,k)/(nElec_C(i,j,k)*Si2No_V(UnitN_) * &
            ElectronCharge)*No2SI_V(UnitU_)

       call calc_electron_collision_rates( &
            Te_C(i,j,k),nElec_C(i,j,k),i,j,k,iBlock,fen_IC(1:nNeuFluid,i,j,k),&
            fei_IC(1:nIonFluid,i,j,k))
       call user_calc_rates( &
            Ti_IC(1:nIonFluid,i,j,k), Te_C(i,j,k),i,j,k,iBlock, &
            nElec_C(i,j,k), nIon_IC(1:nIonFluid,i,j,k),&
            fin_IIC(1:nIonFluid,1:nNeuFluid,i,j,k), &
            fii_IIC(1:nIonFluid,1:nIonFluid,i,j,k),fie_IC(1:nIonFluid,i,j,k),&
            alpha_IC(1:nIonFluid,i,j,k), &
            kin_IIIIC(1:nIonFluid,1:nNeuFluid,1:nNeuFluid,1:nIonFluid,i,j,k),&
            v_IIGB(1:nNeuFluid,1:nIonFluid,i,j,k,iBlock), &
            ve_IIGB(1:nNeuFluid,1:nIonFluid,i,j,k,iBlock),&
            uElec_DC(1:3,i,j,k),uIon_DIC(1:3,1:nIonFluid,i,j,k),&
            Qexc_II(1:nNeuFluid,1:nIonFluid),Qion_II(1:nNeuFluid,1:nIonFluid),&
            DoCalcShading, IsIntersectedShapeR_III(i,j,k), &
            DoCalcDistance2Fieldline,IsWithinTheRingR_III(i,j,k))

       ! Zeroth moment
       ! Sources separated into the terms by
       ! Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       kinAdd_I = 0. ; kinSub_I = 0.
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   ! addition to individual fluid from charge exchange
                   ! unit in [1/(m^3*s)]
                   kinAdd_I(jIonFluid) = kinAdd_I(jIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)* &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k) * nNeu1_C(i,j,k)
                   ! subtraction to individual fluid from charge exchange
                   ! unit in [1/(m^3*s)]
                   kinSub_I(iIonFluid) = kinSub_I(iIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)* &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k) * nNeu1_C(i,j,k)
                end do
             end do
          end do
       end do

       ! Sources divideded into the terms
       ! by Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       vAdd_I = 0. ; veAdd_I = 0.
       do iNeuFluid=1,nNeuFluid
          vAdd_I(1:nIonFluid)  = vAdd_I(1:nIonFluid)  + &
               v_IIGB(iNeuFluid, 1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)
          veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid) + &
               ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)
       end do

       ! photo-ionization
       SRhoTerm_IIC(1,1:nIonFluid,i,j,k) = &
            vAdd_I(1:nIonFluid)*Si2No_V(UnitN_)/Si2No_V(UnitT_)*MassIon_I

       ! electron impact ionization
       SRhoTerm_IIC(2,1:nIonFluid,i,j,k) = &
            veAdd_I(1:nIonFluid)*Si2No_V(UnitN_)/Si2No_V(UnitT_)*MassIon_I

       ! ion-neutral charge exchange
       SRhoTerm_IIC(3,1:nIonFluid,i,j,k) = &
            kinAdd_I(1:nIonFluid)*Si2No_V(UnitN_)/Si2No_V(UnitT_)*MassIon_I

       ! ion-neutral charge exchange
       SRhoTerm_IIC(4,1:nIonFluid,i,j,k) = &
            -kinSub_I(1:nIonFluid)*Si2No_V(UnitN_)/Si2No_V(UnitT_)*MassIon_I

       ! loss due to recombination
       SRhoTerm_IIC(5,1:nIonFluid,i,j,k) = &
            -alpha_IC(1:nIonFluid,i,j,k)*(nElec_C(i,j,k)* &
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitN_)/Si2No_V(UnitT_)) * &
            MassIon_I

       ! First moment, x component
       ! d(rho_s*u_s)/dt = rho_s*du_s/dt + u_s*drho_s/dt
       ! combined from zeroth and first moment
       ! by Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       fiiTot_I = 0. ; finTot_I = 0. ; vAdd_I = 0. ; veAdd_I = 0.

       ! ion-ion collisions
       do iIonFluid=1,nIonFluid
          fiiTot_I(1:nIonFluid) = fiiTot_I(1:nIonFluid) + &
               fii_IIC(1:nIonFluid,iIonFluid,i,j,k)     * &
               (uIon_DIC(1,iIonFluid,i,j,k)-uIon_DIC(1,1:nIonFluid,i,j,k))
       end do

       ! momentum transfer by ion-neutral collisions
       do iNeuFluid=1,nNeuFluid
          finTot_I(1:nIonFluid) = finTot_I(1:nIonFluid)                   + &
               fin_IIC(1:nIonFluid,iNeuFluid,i,j,k)                       * &
               (uNeu1_DC(1,i,j,k)-uIon_DIC(1,1:nIonFluid,i,j,k))
          vAdd_I(1:nIonFluid)  = vAdd_I(1:nIonFluid)                      + &
               v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)  * &
               (uNeu1_DC(1,i,j,k)-uIon_DIC(1,1:nIonFluid,i,j,k))
          veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid)                     + &
               ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k) * &
               (uNeu1_DC(1,i,j,k)-uIon_DIC(1,1:nIonFluid,i,j,k))
       end do

       kinAdd_I = 0.
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   ! addition to individual fluid from charge exchange
                   ! in [1/(m^3*s)]
                   kinAdd_I(jIonFluid) = kinAdd_I(jIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)* &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k)*nNeu1_C(i,j,k)*&
                        (uNeu1_DC(1,i,j,k)-uIon_DIC(1,jIonFluid,i,j,k))
                end do
             end do
          end do
       end do

       ! newly photoionized neutrals
       SRhoUxTerm_IIC(1,1:nIonFluid,i,j,k) =    &
            vAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! newly electron-impact
       SRhoUxTerm_IIC(2,1:nIonFluid,i,j,k) =     &
            veAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! charge exchange
       SRhoUxTerm_IIC(3,1:nIonFluid,i,j,k) =      &
            kinAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*MassIon_I*Si2No_V(UnitU_)

       ! ion-electron
       SRhoUxTerm_IIC(4,1:nIonFluid,i,j,k) = -fie_IC(1:nIonFluid,i,j,k) / &
            Si2No_V(UnitT_)*MassIon_I*nIon_IC(1:nIonFluid,i,j,k)* &
            Si2No_V(UnitN_)* &
            (uIon_DIC(1,1:nIonFluid,i,j,k)-uElec_DC(1,i,j,k)) * &
            Si2No_V(UnitU_)

       ! ion-ion collisions
       SRhoUxTerm_IIC(5,1:nIonFluid,i,j,k) = &
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitRho_) * &
            fiiTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! ion neutral collisions
       SRhoUxTerm_IIC(6,1:nIonFluid,i,j,k) = &
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitRho_) * &
            finTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! Add u_s*drho_s/dt for d(rho_s*u_s)/dt = rho_s*du_s/dt + u_s*drho_s/dt
       do iIonFluid=1,nIonFluid
          SRhoUxTerm_IIC(7,iIonFluid,i,j,k) = &
               sum(SRhoTerm_IIC(1:5,iIonFluid,i,j,k))&
               *uIon_DIC(1,iIonFluid,i,j,k)*Si2No_V(UnitU_)
       end do

       ! First moment, y component
       ! Sources separated into the terms by
       ! Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       fiiTot_I = 0. ; finTot_I = 0. ; vAdd_I = 0. ; veAdd_I = 0.

       ! momentum transfer by ion-ion collisions
       do iIonFluid=1,nIonFluid
          fiiTot_I(1:nIonFluid) = fiiTot_I(1:nIonFluid) + &
               fii_IIC(1:nIonFluid,iIonFluid,i,j,k)     * &
               (uIon_DIC(2,iIonFluid,i,j,k)-uIon_DIC(2,1:nIonFluid,i,j,k))
       end do

       ! ion-neutral collisions
       do iNeuFluid=1,nNeuFluid
          finTot_I(1:nIonFluid) = finTot_I(1:nIonFluid)                   + &
               fin_IIC(1:nIonFluid,iNeuFluid,i,j,k)                       * &
               (uNeu1_DC(2,i,j,k)-uIon_DIC(2,1:nIonFluid,i,j,k))
          vAdd_I(1:nIonFluid)  = vAdd_I(1:nIonFluid)                      + &
               v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)  * &
               (uNeu1_DC(2,i,j,k)-uIon_DIC(2,1:nIonFluid,i,j,k))
          veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid)                     + &
               ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k) * &
               (uNeu1_DC(2,i,j,k)-uIon_DIC(2,1:nIonFluid,i,j,k))
       end do

       ! addition to individual fluid from charge exchange [1/(m^3*s)]
       kinAdd_I = 0.
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   kinAdd_I(jIonFluid) = kinAdd_I(jIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)* &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k)*nNeu1_C(i,j,k)*&
                        (uNeu1_DC(2,i,j,k)-uIon_DIC(2,jIonFluid,i,j,k))
                end do
             end do
          end do
       end do

       ! newly photoionized neutrals
       SRhoUyTerm_IIC(1,1:nIonFluid,i,j,k) =    &
            vAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! newly electron-impact
       SRhoUyTerm_IIC(2,1:nIonFluid,i,j,k) =     &
            veAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! charge exchange
       SRhoUyTerm_IIC(3,1:nIonFluid,i,j,k) =      &
            kinAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*MassIon_I*Si2No_V(UnitU_)

       ! ion-electron
       SRhoUyTerm_IIC(4,1:nIonFluid,i,j,k) = &
            -fie_IC(1:nIonFluid,i,j,k)/Si2No_V(UnitT_)*MassIon_I*&
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitN_)* &
            (uIon_DIC(2,1:nIonFluid,i,j,k)-uElec_DC(2,i,j,k))* &
            Si2No_V(UnitU_)

       ! ion-ion collisions
       SRhoUyTerm_IIC(5,1:nIonFluid,i,j,k) = &
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitRho_)* &
            fiiTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! ion neutral collisions
       SRhoUyTerm_IIC(6,1:nIonFluid,i,j,k) = &
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitRho_)* &
            finTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! Add u_s*drho_s/dt for d(rho_s*u_s)/dt = rho_s*du_s/dt + u_s*drho_s/dt
       do iIonFluid=1,nIonFluid
          SRhoUyTerm_IIC(7,iIonFluid,i,j,k) = &
               sum(SRhoTerm_IIC(1:5,iIonFluid,i,j,k))&
               *uIon_DIC(2,iIonFluid,i,j,k)*Si2No_V(UnitU_)
       end do

       ! First moment, z component
       ! Sources separated into the terms by
       ! Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       fiiTot_I = 0. ; finTot_I = 0. ; vAdd_I = 0. ; veAdd_I = 0.

       ! momentum transfer by ion-ion collisions
       do iIonFluid=1,nIonFluid
          fiiTot_I(1:nIonFluid) = fiiTot_I(1:nIonFluid) + &
               fii_IIC(1:nIonFluid,iIonFluid,i,j,k)*&
               (uIon_DIC(3,iIonFluid,i,j,k)-uIon_DIC(3,1:nIonFluid,i,j,k))
       end do

       ! ion-neutral collisions
       do iNeuFluid=1,nNeuFluid
          finTot_I(1:nIonFluid) = finTot_I(1:nIonFluid)                    + &
               fin_IIC(1:nIonFluid,iNeuFluid,i,j,k)                        * &
               (uNeu1_DC(3,i,j,k)-uIon_DIC(3,1:nIonFluid,i,j,k))
          vAdd_I(1:nIonFluid)  = vAdd_I(1:nIonFluid)                       + &
               v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock) * nNeu1_C(i,j,k) * &
               (uNeu1_DC(3,i,j,k)-uIon_DIC(3,1:nIonFluid,i,j,k))
          veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid)                      + &
               ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)* nNeu1_C(i,j,k) * &
               (uNeu1_DC(3,i,j,k)-uIon_DIC(3,1:nIonFluid,i,j,k))
       end do

       kinAdd_I = 0.
       ! addition to individual fluid from charge exchange [1/(m^3*s)]
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   kinAdd_I(jIonFluid) = kinAdd_I(jIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)* &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k) * nNeu1_C(i,j,k)*&
                        (uNeu1_DC(3,i,j,k)-uIon_DIC(3,jIonFluid,i,j,k))
                end do
             end do
          end do
       end do

       ! newly photoionized neutrals
       SRhoUzTerm_IIC(1,1:nIonFluid,i,j,k) =    &
            vAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! newly electron-impact
       SRhoUzTerm_IIC(2,1:nIonFluid,i,j,k) =    &
            veAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*Si2No_V(UnitU_)*MassIon_I

       ! charge exchange
       SRhoUzTerm_IIC(3,1:nIonFluid,i,j,k) =      &
            kinAdd_I(1:nIonFluid)/Si2No_V(UnitT_) &
            *Si2No_V(UnitN_)*MassIon_I*Si2No_V(UnitU_)

       ! ion-electron
       SRhoUzTerm_IIC(4,1:nIonFluid,i,j,k) = &
            -fie_IC(1:nIonFluid,i,j,k)/Si2No_V(UnitT_)*MassIon_I*&
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitN_)* &
            (uIon_DIC(3,1:nIonFluid,i,j,k)-uElec_DC(3,i,j,k))* &
            Si2No_V(UnitU_)

       ! ion-ion collisions
       SRhoUzTerm_IIC(5,1:nIonFluid,i,j,k) = nIon_IC(1:nIonFluid,i,j,k) * &
            Si2No_V(UnitRho_)*fiiTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! ion neutral collisions
       SRhoUzTerm_IIC(6,1:nIonFluid,i,j,k) = nIon_IC(1:nIonFluid,i,j,k) * &
            Si2No_V(UnitRho_)*finTot_I(1:nIonFluid)* &
            Si2No_V(UnitU_)/Si2No_V(UnitT_)*cProtonMass*MassIon_I

       ! Add u_s*drho_s/dt for d(rho_s*u_s)/dt = rho_s*du_s/dt + u_s*drho_s/dt
       do iIonFluid=1,nIonFluid
          SRhoUzTerm_IIC(7,iIonFluid,i,j,k) = &
               sum(SRhoTerm_IIC(1:5,iIonFluid,i,j,k)) &
               *uIon_DIC(3,iIonFluid,i,j,k)*Si2No_V(UnitU_)
       end do

       ! Second moment
       ! ------------------------------------------------------------------
       ! (u_n-u_e)^2 difference in neutral and electron speeds qubed [m^2/s^2]
       do iNeuFluid=1,nNeuFluid
          uNeuElec2_IC(iNeuFluid,i,j,k) =  &
               (uNeu1_DC(1,i,j,k)-uElec_DC(1,i,j,k))**2 + &
               (uNeu1_DC(2,i,j,k)-uElec_DC(2,i,j,k))**2 + &
               (uNeu1_DC(3,i,j,k)-uElec_DC(3,i,j,k))**2
       end do

       ! (u_i-u_e)^2 difference in ion and electron speeds qubed [m^2/s^2]
       do iIonFluid=1,nIonFluid
          uIonElec2_IC(iIonFluid,i,j,k) = &
               (uIon_DIC(1,iIonFluid,i,j,k)-uElec_DC(1,i,j,k))**2 +&
               (uIon_DIC(2,iIonFluid,i,j,k)-uElec_DC(2,i,j,k))**2+&
               (uIon_DIC(3,iIonFluid,i,j,k)-uElec_DC(3,i,j,k))**2
       end do

       ! Sources separated into the terms by
       ! Tamas' "Transport Equations for Multifluid Magnetized Plasmas"
       ! subtraction to individual fluid from charge exchange [1/(m^3*s)]
       kinSub_I = 0.
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   kinSub_I(iIonFluid) = kinSub_I(iIonFluid) + &
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k)* nNeu1_C(i,j,k)
                end do
             end do
          end do
       end do

       ! lost ions through charge exchange
       SPTerm_IIC(1,1:nIonFluid,i,j,k) = &
            -kinSub_I(1:nIonFluid)/Si2No_V(UnitT_)/Si2No_V(UnitT_)* &
            State_VGB(iPIon_I,i,j,k,iBlock)

       ! lost ions through recombination
       SPTerm_IIC(2,1:nIonFluid,i,j,k) = &
            -alpha_IC(1:nIonFluid,i,j,k)*nElec_C(i,j,k)/Si2No_V(UnitT_)*&
            State_VGB(iPIon_I,i,j,k,iBlock)

       ! ion-ion collisions, temperature
       fiiTot_I(1:nIonFluid) = 0.
       do iIonFluid=1,nIonFluid
          fiiTot_I(1:nIonFluid) = fiiTot_I(1:nIonFluid) + &
               fii_IIC(1:nIonFluid,iIonFluid,i,j,k) * &
               nIon_IC(1:nIonFluid,i,j,k) * MassIon_I(1:nIonFluid) / &
               (MassIon_I(1:nIonFluid)+MassIon_I(iIonFluid))*&
               cBoltzmann*(Ti_IC(iIonFluid,i,j,k)-Ti_IC(1:nIonFluid,i,j,k))
       end do

       SPTerm_IIC(3,1:nIonFluid,i,j,k) = &
            2.*fiiTot_I(1:nIonFluid)/Si2No_V(UnitT_)*Si2No_V(UnitEnergyDens_)

       ! ion-ion collisions, velocity
       fiiTot_I(1:nIonFluid) = 0.
       do iIonFluid=1,nIonFluid
          fiiTot_I(1:nIonFluid) = fiiTot_I(1:nIonFluid)+ &
               fii_IIC(1:nIonFluid,iIonFluid,i,j,k)* &
               nIon_IC(1:nIonFluid,i,j,k)* &
               MassIon_I(1:nIonFluid)*MassIon_I(iIonFluid) / &
               (MassIon_I(1:nIonFluid)+MassIon_I(iIonFluid))*&
               uIonIon2_IIC(1:nIonFluid,iIonFluid,i,j,k)
       end do

       SPTerm_IIC(4,1:nIonFluid,i,j,k) = 2./3.*fiiTot_I(1:nIonFluid) / &
            Si2No_V(UnitT_)*Si2No_V(UnitN_)*Si2No_V(UnitU_)**2

       ! ion-neutral collisions, temperature
       finTot_I(1:nIonFluid) = 0.
       do iNeuFluid=1,nNeuFluid
          finTot_I(1:nIonFluid) = finTot_I(1:nIonFluid)+ &
               fin_IIC(1:nIonFluid,iNeuFluid,i,j,k)* &
               nIon_IC(1:nIonFluid,i,j,k)*MassIon_I(1:nIonFluid) / &
               (MassIon_I(1:nIonFluid)+MassFluid_I(nFluid))*&
               cBoltzmann*(TempNeu1_C(i,j,k)-Ti_IC(1:nIonFluid,i,j,k))
       end do

       SPTerm_IIC(5,1:nIonFluid,i,j,k) = 2.*finTot_I(1:nIonFluid) / &
            Si2No_V(UnitT_)*Si2No_V(UnitEnergyDens_)

       ! ion-neutral collisions, velocity
       finTot_I(1:nIonFluid) = 0.
       do iNeuFluid=1,nNeuFluid
          finTot_I(1:nIonFluid) = finTot_I(1:nIonFluid) + &
               fin_IIC(1:nIonFluid,iNeuFluid,i,j,k) * &
               nIon_IC(1:nIonFluid,i,j,k)*&
               MassIon_I(1:nIonFluid)*MassFluid_I(nFluid) / &
               (MassIon_I(1:nIonFluid)+MassFluid_I(nFluid))*&
               uIonNeu2_IIC(1:nIonFluid,iNeuFluid,i,j,k)
       end do

       SPTerm_IIC(6,1:nIonFluid,i,j,k) = 2./3.*finTot_I(1:nIonFluid) / &
            Si2No_V(UnitT_)*Si2No_V(UnitN_)*Si2No_V(UnitU_)**2

       ! ion-electron, temperature
       SPTerm_IIC(7,1:nIonFluid,i,j,k) = 2.*fie_IC(1:nIonFluid,i,j,k) / &
            Si2No_V(UnitT_)*nIon_IC(1:nIonFluid,i,j,k)*&
            cBoltzmann*(Te_C(i,j,k)-Ti_IC(1:nIonFluid,i,j,k)) * &
            Si2No_V(UnitEnergyDens_)

       ! ion-electron collisional exchange (due to Hall velocity)
       SPTerm_IIC(8,1:nIonFluid,i,j,k) = 2./3.*fie_IC(1:nIonFluid,i,j,k) / &
            Si2No_V(UnitT_)*cElectronMass*&
            nIon_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitRho_)* &
            uIonElec2_IC(1:nIonFluid,i,j,k)*Si2No_V(UnitU_)**2

       ! photoionization
       vAdd_I = 0.
       do iNeuFluid=1,nNeuFluid
          vAdd_I(1:nIonFluid) = vAdd_I(1:nIonFluid) + &
               v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)* &
               uIonNeu2_IIC(1:nIonFluid,iNeuFluid,i,j,k)
       end do

       SPTerm_IIC(9,1:nIonFluid,i,j,k) = 1./3.*vAdd_I(1:nIonFluid)   / &
            Si2No_V(UnitT_) * MassIon_I(1:nIonFluid)*Si2No_V(UnitN_)   &
            *Si2No_V(UnitU_)**2

       ! electron-impact
       veAdd_I = 0.
       do iNeuFluid=1,nNeuFluid
          veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid) + &
               ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)* &
               uIonNeu2_IIC(1:nIonFluid,iNeuFluid,i,j,k)
       end do

       SPTerm_IIC(10,1:nIonFluid,i,j,k) = 1./3.*veAdd_I(1:nIonFluid) / &
            Si2No_V(UnitT_) * MassIon_I(1:nIonFluid)*Si2No_V(UnitN_)   &
            *Si2No_V(UnitU_)**2

       ! addition to individual fluid from charge exchange [1/(m*s^2)]
       kinAdd_I = 0.
       do iIonFluid=1,nIonFluid
          do jIonFluid=1,nIonFluid
             do iNeuFluid=1,nNeuFluid
                do jNeutral=1,nNeuFluid
                   kinAdd_I(jIonFluid) = kinAdd_I(jIonFluid) + &
                        nIon_IC(iIonFluid,i,j,k)*&
                        kin_IIIIC(iIonFluid,iNeuFluid,jNeutral,jIonFluid, &
                        i,j,k) * nNeu1_C(i,j,k)* &
                        uIonNeu2_IIC(jIonFluid,iNeuFluid,i,j,k)
                end do
             end do
          end do
       end do

       SPTerm_IIC(11,1:nIonFluid,i,j,k) = 1./3.*kinAdd_I(1:nIonFluid) &
            /Si2No_V(UnitT_)*MassIon_I(1:nIonFluid)*Si2No_V(UnitN_)   &
            *Si2No_V(UnitU_)**2

       if (UseElectronPressure) then
          ! lost electrons through recombination
          SPeTerm_IC(1,i,j,k) = -sum( &
               alpha_IC(1:nIonFluid,i,j,k)*nIon_IC(1:nIonFluid,i,j,k)) / &
               Si2No_V(UnitT_)*State_VGB(Pe_,i,j,k,iBlock)

          vAdd_I(1:nIonFluid) = 0.
          do iNeuFluid=1,nNeuFluid
             vAdd_I(1:nIonFluid) = vAdd_I(1:nIonFluid) + &
                  v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)* &
                  uNeuElec2_IC(iNeuFluid,i,j,k)
          end do

          ! new electrons through photoionized neutrals
          SPeTerm_IC(2,i,j,k) = 1./3.*cElectronMass*sum(vAdd_I) * &
               Si2No_V(UnitRho_)/Si2No_V(UnitT_)*Si2No_V(UnitU_)**2

          veAdd_I(1:nIonFluid) = 0.
          do iNeuFluid=1,nNeuFluid
             veAdd_I(1:nIonFluid) = veAdd_I(1:nIonFluid) + &
                  ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock)*nNeu1_C(i,j,k)* &
                  uNeuElec2_IC(iNeuFluid,i,j,k)
          end do

          ! new electrons through electron-impact
          SPeTerm_IC(3,i,j,k) = 1./3.*cElectronMass*sum(veAdd_I) * &
               Si2No_V(UnitRho_)/Si2No_V(UnitT_)*Si2No_V(UnitU_)**2

          feiTot = 0.
          do iIonFluid=1,nIonFluid
             feiTot = feiTot+fei_IC(iIonFluid,i,j,k)/MassIon_I(iIonFluid)*&
                  (Ti_IC(iIonFluid,i,j,k)-Te_C(i,j,k))
          end do

          ! ion-electron collisional exchange (thermal motion)
          SPeTerm_IC(4,i,j,k) = 2.*cElectronMass* &
               Si2No_V(UnitRho_)/Si2No_V(UnitN_)*&
               nElec_C(i,j,k)*cBoltzmann*Si2No_V(UnitEnergyDens_) * &
               feiTot/Si2No_V(UnitT_)

          fenTot = 0.
          do iNeuFluid=1,nNeuFluid
             fenTot = fenTot + &
                  fen_IC(iNeuFluid,i,j,k)/MassFluid_I(nFluid)/cProtonMass*&
                  (TempNeu1_C(i,j,k)-Te_C(i,j,k))
          end do

          ! electron-neutral collisional exchange (thermal motion)
          SPeTerm_IC(5,i,j,k) = 2.*cElectronMass*nElec_C(i,j,k)*cBoltzmann*&
               Si2No_V(UnitEnergyDens_)*fenTot/Si2No_V(UnitT_)

          ! ion-electron collisional exchange (due to Hall velocity)
          SPeTerm_IC(6,i,j,k) = 2./3. * sum( &
               fei_IC(1:nIonFluid,i,j,k)*uIonElec2_IC(1:nIonFluid,i,j,k) ) / &
               Si2No_V(UnitT_)*cElectronMass*nElec_C(i,j,k) * &
               Si2No_V(UnitRho_)*Si2No_V(UnitU_)**2

          ! electron-neutral collisional exchange (bulk motion)
          SPeTerm_IC(7,i,j,k) = 2./3.*sum( &
               fen_IC(1:nNeuFluid,i,j,k)*uNeuElec2_IC(1:nNeuFluid,i,j,k)) / &
               Si2No_V(UnitT_)*cElectronMass*nElec_C(i,j,k) * &
               Si2No_V(UnitRho_)*Si2No_V(UnitU_)**2

          vAdd_I(1:nIonFluid) = 0.
          do iNeuFluid=1,nNeuFluid
             vAdd_I(1:nIonFluid) = vAdd_I(1:nIonFluid) + &
                  (v_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock) * &
                  Qexc_II(iNeuFluid,1:nIonFluid) - &
                  ve_IIGB(iNeuFluid,1:nIonFluid,i,j,k,iBlock) * &
                  Qion_II(iNeuFluid,1:nIonFluid))*ChargeIon_I(1:nIonFluid) * &
                  nNeu1_C(i,j,k)
          end do

          ! heating of electrons due to ionization excess energy
          SPeTerm_IC(8,i,j,k) = 2./3.*sum(vAdd_I) * &
               Si2No_V(UnitEnergyDens_)/Si2No_V(UnitT_)

          ! electron cooling due to collisions w/ water vapor

          ! logTe = log(Te_C(i,j,k))
          ! SPeTerm_IC(8,i,j,k) = &
          !     exp(-188.4701+33.2547*logTe-2.0792*logTe**2+0.0425*logTe**3)
          !
          ! if(Te_C(i,j,k)<1.5*TempNeu1_C(i,j,k)) then
          !   SPeTerm_IC(8,i,j,k)=4.5e-9/(0.5*TempNeu1_C(i,j,k))* &
          !        (Te_C(i,j,k)-TempNeu1_C(i,j,k))
          ! else
          !   SPeTerm_IC(8,i,j,k)=SPeTerm_IC(8,i,j,k)+4.5e-9
          ! end if

          SPeTerm_IC(9,i,j,k) = 4e-9* &
               (1-exp(-cBoltzmann*(Te_C(i,j,k)-TempNeu1_C(i,j,k)) &
               /0.033/cEV))

          if (Te_C(i,j,k) > 2181.65) then
             SPeTerm_IC(9,i,j,k) = SPeTerm_IC(9,i,j,k) + &
                  6.5e-9*(0.415-exp(-(cBoltzmann*Te_C(i,j,k)-0.1*cEV)/&
                  (0.1*cEV)))
          end if

          SPeTerm_IC(9,i,j,k) = min(-2./3.*nNeu1_C(i,j,k)*nElec_C(i,j,k)* &
               SPeTerm_IC(9,i,j,k)/1e6*cEV* &
               Si2No_V(UnitEnergyDens_)/Si2No_V(UnitT_), 0.0)

          ! SPeTerm_IC(8,i,j,k) = -2./3.*nNeu1_C(i,j,k)*nElec_C(i,j,k)* &
          !     SPeTerm_IC(8,i,j,k)/1e6*1.60217733e-19* &
          !     Si2No_V(UnitEnergyDens_)/Si2No_V(UnitT_)

          If (IsWithinTheRingR_III(i,j,k) == 1.0    .and. &
               tSimulation >  TimeEnhanceStart  .and. &
               tSimulation < TimeEnhanceEnd) then
             SPeTerm_IC(10,i,j,k) =  SPeAdditional_GB(i,j,k,iBlock)
          end If

       end if

       ! sum up individual terms
       do iTerm=1,nRhoTerm
          SRho_IC(1:nIonFluid,i,j,k) = SRho_IC(1:nIonFluid,i,j,k) + &
               SRhoTerm_IIC(iTerm,1:nIonFluid,i,j,k)
       end do

       do iTerm=1,nRhoUTerm
          SRhoUx_IC(1:nIonFluid,i,j,k) = SRhoUx_IC(1:nIonFluid,i,j,k) + &
               SRhoUxTerm_IIC(iTerm,1:nIonFluid,i,j,k)
          SRhoUy_IC(1:nIonFluid,i,j,k) = SRhoUy_IC(1:nIonFluid,i,j,k) + &
               SRhoUyTerm_IIC(iTerm,1:nIonFluid,i,j,k)
          SRhoUz_IC(1:nIonFluid,i,j,k) = SRhoUz_IC(1:nIonFluid,i,j,k) + &
               SRhoUzTerm_IIC(iTerm,1:nIonFluid,i,j,k)
       end do

       do iTerm=1,nPTerm
          SP_IC(1:nIonFluid,i,j,k) = SP_IC(1:nIonFluid,i,j,k) + &
               SPTerm_IIC(iTerm,1:nIonFluid,i,j,k)
       end do

       if(UseElectronPressure) then
          SPe_C(i,j,k) = sum(SPeTerm_IC(1:nPeTerm,i,j,k))
       end if

       Source_VC(iRhoIon_I   ,i,j,k) = SRho_IC(1:nIonFluid,i,j,k)    + &
            Source_VC(iRhoIon_I   ,i,j,k)
       Source_VC(iRhoUxIon_I ,i,j,k) = SRhoUx_IC(1:nIonFluid,i,j,k)  + &
            Source_VC(iRhoUxIon_I ,i,j,k)
       Source_VC(iRhoUyIon_I ,i,j,k) = SRhoUy_IC(1:nIonFluid,i,j,k)  + &
            Source_VC(iRhoUyIon_I ,i,j,k)
       Source_VC(iRhoUzIon_I ,i,j,k) = SRhoUz_IC(1:nIonFluid,i,j,k)  + &
            Source_VC(iRhoUzIon_I ,i,j,k)
       Source_VC(iPIon_I     ,i,j,k) = SP_IC(1:nIonFluid,i,j,k)      + &
            Source_VC(iPIon_I     ,i,j,k)

       Source_VC(Bx_    ,i,j,k) = SBx_C(i,j,k)                       + &
            Source_VC(Bx_    ,i,j,k)
       Source_VC(By_    ,i,j,k) = SBy_C(i,j,k)                       + &
            Source_VC(By_    ,i,j,k)
       Source_VC(Bz_    ,i,j,k) = SBz_C(i,j,k)                       + &
            Source_VC(Bz_    ,i,j,k)

       if(UseElectronPressure) then
          Source_VC(Pe_    ,i,j,k) = SPe_C(i,j,k)                    + &
               Source_VC(Pe_    ,i,j,k)
       end if

       if (DoSaveSource) call save_user_source
    end do;  end do;  end do

    if (DoCalcShading) then
       call put_block_data(iBlock,nI,nJ,nK,IsIntersectedShapeR_III)
       DoCalcShading = .false.
    end if
    if (DoCalcDistance2Fieldline) then
       call put_block_data(iBlock,nI,nJ,nK,IsWithinTheRingR_III)
       DoCalcDistance2Fieldline = .false.
    end if

    if(DoTest) call print_test

    call test_stop(NameSub, DoTest, iBlock)
  contains
    !==========================================================================
    subroutine save_user_source

      !------------------------------------------------------------------------
      select case(NameSource)
      case('H2OpRho')
         do iTerm = 1, nRhoTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =  &
                 SRhoTerm_IIC(iTerm,H2Op_,i,j,k) &
                 *No2SI_V(UnitRho_)/No2SI_V(UnitT_)
         end do
      case('H2OpUx')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =    &
                 SRhoUxTerm_IIC(iTerm,H2Op_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('H2OpUy')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =    &
                 SRhoUyTerm_IIC(iTerm,H2Op_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('H2OpUz')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =    &
                 SRhoUzTerm_IIC(iTerm,H2Op_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('H2OpP')
         do iTerm = 1, nPTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) = &
                 SPTerm_IIC(iTerm,H2Op_,i,j,k)  &
                 *No2SI_V(UnitP_)/No2SI_V(UnitT_)
         end do
      case('SwRho')
         do iTerm = 1, nRhoTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) = &
                 SRhoTerm_IIC(iTerm,Sw_,i,j,k)  &
                 *No2SI_V(UnitRho_)/No2SI_V(UnitT_)
         end do
      case('SwUx')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =  &
                 SRhoUxTerm_IIC(iTerm,Sw_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('SwUy')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =  &
                 SRhoUyTerm_IIC(iTerm,Sw_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('SwUz')
         do iTerm = 1, nRhoUTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) =  &
                 SRhoUzTerm_IIC(iTerm,Sw_,i,j,k) &
                 *No2SI_V(UnitRhoU_)/No2SI_V(UnitT_)
         end do
      case('SwP')
         do iTerm = 1, nPTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) = &
                 SPTerm_IIC(iTerm,Sw_,i,j,k)    &
                 *No2SI_V(UnitP_)/No2SI_V(UnitT_)
         end do

      case('Pe')
         do iTerm = 1, nPeTerm
            TestArray_IGB(iTerm,i,j,k,iBlock) = &
                 SPeTerm_IC(iTerm,i,j,k)        &
                 *No2SI_V(UnitP_)/No2SI_V(UnitT_)
         end do
      case default
         if(iProc==0) call stop_mpi( &
              NameSub//' invalid NameSource='//trim(NameSource))
      end select
    end subroutine save_user_source
    !==========================================================================

    subroutine print_test
      character(len=100) :: TestFmt1, TestFmt2, TestFmt3

      !------------------------------------------------------------------------
      i=iTest;j=jTest;k=kTest

      !---------------------------------------------------------------------
      TestFmt1 = '(a, 100es22.15)'
      TestFmt2 = '(a, 2es22.15, 2x, f7.2)'
      TestFmt3 = '(a, i2, a, 2es22.15, 2x, f7.2)'
      write(*,*) '========================================================'
      write(*,*) 'Neutral background:'
      write(*,TestFmt1) '  n, u_D, T (SI)  =', &
           nNeu1_C(i,j,k), uNeu1_DC(:,i,j,k),  &
           TempNeu1_C(i,j,k)
      write(*,TestFmt1) '  n, u_D, T (NO)  =', &
           nNeu1_C(i,j,k)   *Si2No_V(UnitN_),  &
           uNeu1_DC(:,i,j,k)*Si2No_V(UnitU_),  &
           TempNeu1_C(i,j,k)*Si2No_V(UnitTemperature_)
      write(*,*) '-----------------------------------------------------'
      write(*,'(a,i2)') ' Ion information: nIonFluid =', nIonFluid
      write(*,*) ' MassIon_I   =',  MassIon_I
      write(*,*) ' ChargeIon_I =',ChargeIon_I
      do iIonFluid = 1, nIonFluid
         write(*,'(a,i1,100es22.15)')                        &
              '  iFluid, n, u_D, T  (SI) = ', iIonFluid,    &
              nIon_IC(iIonFluid,i,j,k),         &
              uIon_DIC(:,iIonFluid,i,j,k),      &
              Ti_IC(iIonFluid,i,j,k)
         write(*,'(a,i1,100es22.15)') &
              '  iFluid, n, u_D, T  (NO) = ', iIonFluid,    &
              nIon_IC(iIonFluid,i,j,k)    *Si2NO_V(UnitN_), &
              uIon_DIC(:,iIonFluid,i,j,k) *Si2NO_V(UnitU_), &
              Ti_IC(iIonFluid,i,j,k)      *Si2NO_V(UnitTemperature_)
      end do
      write(*,*) '-----------------------------------------------------'
      write(*,'(a,i2)') ' Electron information:'
      write(*,'(a,100es22.15)') &
           '  Te  (SI) = ', Te_C(i,j,k)
      write(*,'(a,100es22.15)') &
           '  Te  (SI) = ', Te_C(i,j,k)*Si2NO_V(UnitTemperature_)

      do iIonFluid = 1, nIonFluid
         write(*,*) '-----------------------------------------------------'
         write(*,'(a4,i2,a)') ' Ion ', iIonFluid, ':'
         write(*,'(a, f7.2)') ' MassIon_I(iIonFluid) =', &
              MassIon_I(iIonFluid)
         write(*,TestFmt1) ' vIonizationSi  =', &
              v_IIGB(1,iIonFluid,i,j,k,iBlockTest)
         write(*,TestFmt1) ' veSi_III       =', &
              ve_IIGB(1,iIonFluid,i,j,k,iBlockTest)
         write(*,TestFmt1) ' kinSi_IIII     =', &
              kin_IIIIC(iIonFluid,1,1,:,i,j,k)
         write(*,TestFmt1) ' finSi_II       =', &
              fin_IIC(iIonFluid, 1, i,j,k)
         write(*,TestFmt1) ' fiiSi_II       =', &
              fii_IIC(iIonFluid, :, i,j,k)
         write(*,TestFmt1) ' fieSi_I        =', &
              fie_IC(iIonFluid, i,j,k)
         write(*,TestFmt1) ' alphaSi_II     =', &
              alpha_IC(iIonFluid,i,j,k)
         write(*,*) '*****************************************************'
         write(*,TestFmt2) ' Source_VC  (NO, SI, rate)            =', &
              Source_VC(iRhoIon_I(iIonFluid),i,j,k),      &
              Source_VC(iRhoIon_I(iIonFluid),i,j,k)       &
              *No2SI_V(UnitRho_)/No2Si_V(UnitT_),         &
              Source_VC(iRhoIon_I(iIonFluid),i,j,k)*100   &
              /State_VGB(iRhoIon_I(iIonFluid),i,j,k,iBlock)
         write(*,TestFmt2) ' SRho_IC  (NO, SI, rate)              =', &
              SRho_IC(iIonFluid,i,j,k),             &
              SRho_IC(iIonFluid,i,j,k)              &
              *No2SI_V(UnitRho_)/No2Si_V(UnitT_),   &
              SRho_IC(iIonFluid,i,j,k)*100          &
              /State_VGB(iRhoIon_I(iIonFluid),i,j,k,iBlock)
         do iTerm =1,nRhoTerm
            write(*,TestFmt3) &
                 '  SRhoTerms_II(',iTerm, ')   (NO, SI, rate)   =', &
                 SRhoTerm_IIC(iTerm,iIonFluid,i,j,k),   &
                 SRhoTerm_IIC(iTerm,iIonFluid,i,j,k)    &
                 *No2SI_V(UnitRho_)/No2Si_V(UnitT_),    &
                 SRhoTerm_IIC(iTerm,iIonFluid,i,j,k)    &
                 /State_VGB(iRhoIon_I(iIonFluid),i,j,k,iBlock)*100
         end do
         write(*,*) '*****************************************************'
         write(*,'(a,i1)') ' iDir = ', 1
         write(*,TestFmt2) ' Source_VC  (NO, SI, rate)              =', &
              Source_VC(iRhoUxIon_I(iIonFluid),i,j,k),    &
              Source_VC(iRhoUxIon_I(iIonFluid),i,j,k)     &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),        &
              Source_VC(iRhoUxIon_I(iIonFluid),i,j,k)*100 &
              /max(abs(State_VGB(iRhoUxIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         write(*,TestFmt2) ' SRhoU_IC  (NO, SI, rate)               =', &
              SRhoUx_IC(iIonFluid,i,j,k),             &
              SRhoUx_IC(iIonFluid,i,j,k)              &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),    &
              SRhoUx_IC(iIonFluid,i,j,k)*100          &
              /max(abs(State_VGB(iRhoUxIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         do iTerm = 1,nRhoUTerm
            write(*,TestFmt3) &
                 '  SRhoUTerms_IID(',iTerm, ')   (NO, SI, rate)   =',  &
                 SRhoUxTerm_IIC(iTerm,iIonFluid,i,j,k),    &
                 SRhoUxTerm_IIC(iTerm,iIonFluid,i,j,k)     &
                 *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),      &
                 SRhoUxTerm_IIC(iTerm,iIonFluid,i,j,k)*100 &
                 /max(cTiny, &
                 abs(State_VGB(iRhoUxIon_I(iIonFluid),i,j,k,iBlock)))
         end do
         write(*,'(a,i1)') ' iDir = ', 2
         write(*,TestFmt2) ' Source_VC  (NO, SI, rate)              =', &
              Source_VC(iRhoUyIon_I(iIonFluid),i,j,k),    &
              Source_VC(iRhoUyIon_I(iIonFluid),i,j,k)     &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),        &
              Source_VC(iRhoUyIon_I(iIonFluid),i,j,k)*100 &
              /max(abs(State_VGB(iRhoUyIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         write(*,TestFmt2) ' SRhoU_IC  (NO, SI, rate)               =', &
              SRhoUy_IC(iIonFluid,i,j,k),            &
              SRhoUy_IC(iIonFluid,i,j,k)             &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),   &
              SRhoUy_IC(iIonFluid,i,j,k)*100         &
              /max(abs(State_VGB(iRhoUyIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         do iTerm = 1,nRhoUTerm
            write(*,TestFmt3) &
                 '  SRhoUTerms_IID(',iTerm, ')   (NO, SI, rate)   =',  &
                 SRhoUyTerm_IIC(iTerm,iIonFluid,i,j,k),                &
                 SRhoUyTerm_IIC(iTerm,iIonFluid,i,j,k)                 &
                 *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),                  &
                 SRhoUyTerm_IIC(iTerm,iIonFluid,i,j,k)*100             &
                 /max(cTiny, &
                 abs(State_VGB(iRhoUyIon_I(iIonFluid),i,j,k,iBlock)))
         end do
         write(*,'(a,i1)') ' iDir = ', 3
         write(*,TestFmt2) ' Source_VC  (NO, SI, rate)              =', &
              Source_VC(iRhoUzIon_I(iIonFluid),i,j,k),    &
              Source_VC(iRhoUzIon_I(iIonFluid),i,j,k)     &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),        &
              Source_VC(iRhoUzIon_I(iIonFluid),i,j,k)*100 &
              /max(abs(State_VGB(iRhoUzIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         write(*,TestFmt2) ' SRhoU_IC  (NO, SI, rate)               =', &
              SRhoUz_IC(iIonFluid,i,j,k),           &
              SRhoUz_IC(iIonFluid,i,j,k)            &
              *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),  &
              SRhoUz_IC(iIonFluid,i,j,k)*100        &
              /max(abs(State_VGB(iRhoUzIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         do iTerm = 1,nRhoUTerm
            write(*,TestFmt3) &
                 '  SRhoUTerms_IID(',iTerm, ')   (NO, SI, rate)   =',  &
                 SRhoUzTerm_IIC(iTerm,iIonFluid,i,j,k),                &
                 SRhoUzTerm_IIC(iTerm,iIonFluid,i,j,k)                 &
                 *No2SI_V(UnitRhoU_)/No2Si_V(UnitT_),                  &
                 SRhoUzTerm_IIC(iTerm,iIonFluid,i,j,k)*100             &
                 /max(cTIny, &
                 abs(State_VGB(iRhoUzIon_I(iIonFluid),i,j,k,iBlock)))
         end do
         write(*,*) '*****************************************************'
         write(*,TestFmt2) ' Source_VC  (NO, SI, rate)          =',  &
              Source_VC(iPIon_I(iIonFluid),i,j,k),       &
              Source_VC(iPIon_I(iIonFluid),i,j,k)        &
              *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_), &
              Source_VC(iPIon_I(iIonFluid),i,j,k)*100    &
              /max(abs(State_VGB(iPIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         write(*,TestFmt2) ' SP_IC  (NO, SI, rate)              =',  &
              SP_IC(iIonFluid,i,j,k),                    &
              SP_IC(iIonFluid,i,j,k)                     &
              *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_), &
              SP_IC(iIonFluid,i,j,k)*100                 &
              /max(abs(State_VGB(iPIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         do iTerm = 1,nPTerm
            write(*,TestFmt3) &
                 '  SPTerms_II(',iTerm, ')   (NO, SI, rate)   =',  &
                 SPTerm_IIC(iTerm,iIonFluid,i,j,k),                &
                 SPTerm_IIC(iTerm,iIonFluid,i,j,k)                 &
                 *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_),        &
                 SPTerm_IIC(iTerm,iIonFluid,i,j,k)*100             &
                 /max(abs(State_VGB(iPIon_I(iIonFluid),i,j,k,iBlock)),cTiny)
         end do
      end do

      write(*,*) '-----------------------------------------------------'
      write(*,'(a10,i2,a)') ' Electron:'
      write(*,TestFmt1) ' fenSi_II       =', fen_IC(1, i,j,k)
      write(*,TestFmt1) ' feiSi_II       =', fei_IC(:, i,j,k)
      write(*,TestFmt1) ' alphaSi_II     =', alpha_IC(:,i,j,k)
      write(*,TestFmt2) ' Source_VC  (NO, SI, rate)           =', &
           Source_VC(Pe_,i,j,k),                      &
           Source_VC(Pe_,i,j,k)                       &
           *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_), &
           Source_VC(Pe_,i,j,k)*100                   &
           /max(abs(State_VGB(Pe_,i,j,k,iBlock)),cTiny)
      write(*,TestFmt2) ' SPe_IC  (NO, SI, rate)              =', &
           SPe_C(i,j,k),                              &
           SPe_C(i,j,k)                               &
           *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_), &
           SPe_C(i,j,k)*100                           &
           /max(abs(State_VGB(Pe_,i,j,k,iBlock)),cTiny)
      do iTerm = 1,nPeTerm
         write(*,TestFmt3) &
              '  SPeTerms_II(',iTerm, ')   (NO, SI, rate)   =', &
              SPeTerm_IC(iTerm,i,j,k),                          &
              SPeTerm_IC(iTerm,i,j,k)                           &
              *No2SI_V(UnitEnergyDens_)/No2Si_V(UnitT_),        &
              SPeTerm_IC(iTerm,i,j,k)*100                       &
              /max(abs(State_VGB(Pe_,i,j,k,iBlock)),cTiny)
      end do
      write(*,*) '========================================================'
    end subroutine print_test
    !==========================================================================

  end subroutine user_calc_sources_impl
  !============================================================================
  subroutine user_calc_sources_expl(iBlock)

    integer, intent(in) :: iBlock

    !--------------------------------------------------------------------------
  end subroutine user_calc_sources_expl
  !============================================================================

end module ModUser
!==============================================================================
