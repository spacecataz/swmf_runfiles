!  Copyright (C) 2002 Regents of the University of Michigan,
!  portions used with permission
!  For more information, see http://csem.engin.umich.edu/tools/swmf
!#NOTPUBLIC  email:zghuang@umich.edu  expires:12/31/2099
module ModUser

  ! Should be 1 "implemented" for each subroutine defined, in order that
  ! changes BATS defaults (e.g., not "user_actions", etc.)
  use ModUserEmpty,               &
       IMPLEMENTED1  => user_action,                     &
       IMPLEMENTED2  => user_read_inputs,                &
       IMPLEMENTED3  => user_init_session,               &
       IMPLEMENTED4  => user_calc_sources_expl ! ,          &
       ! IMPLEMENTED5  => user_calc_sources_impl

  use BATL_lib, ONLY: &
       test_start, test_stop, &
       iTest, jTest, kTest, iBlockTest, iProcTest, iVarTest, iProc
  ! use ModSize
  use CON_time,        ONLY: TimeStart, tSimulation
  use ModTimeConvert,  ONLY: TimeType, time_int_to_real, time_real_to_int
  use ModNumConst,     ONLY: cPi, cDegToRad
  use ModConst,        ONLY: cProtonMass

  include 'user_module.h' ! list of public methods

  ! Here you must define a user routine Version number and a
  ! descriptive string.
  character (len=*), parameter :: NameUserFile = "ModUserPointSource.f90"
  character (len=*), parameter :: NameUserModule = &
       'Point mass source; DTW 2024'

  ! Timing Vars
  type(TimeType) :: TimePointStart, TimePointStop, TimePointNow

  ! DTW Variable defs
  logical, save :: UsePointSource
  integer, save :: nPointSource = 0  ! Number of point sources.
  ! Location and amplitude of sources:
  real, allocatable, save :: Amplitude_I(:), XyzSource_DI(:,:)
  real, allocatable, save :: AngleInit_I(:), RadPoint_I(:)
  real :: rspread = 1.0  ! Spread of gaussian in RE.
  real :: raterot = 0.0  ! Rotation rate in rads/second

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
       TimePointStart % iYear = -1
       TimePointStop % iYear  = -1
    case('clean module')
       ! Do shit here.
    end select
    call test_stop(NameSub, DoTest)
  end subroutine user_action
  !============================================================================
  subroutine user_read_inputs

    use ModReadParam

    character (len=100) :: NameCommand

    real :: sourceAmplitude, FracSecond
    integer :: i

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_read_inputs'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest)

    do
       if(.not.read_line() ) EXIT
       if(.not.read_command(NameCommand)) CYCLE
       select case(NameCommand)
       case("#POINTSTART")
         call read_var('iYear',   TimePointStart % iYear)
         call read_var('iMonth',  TimePointStart % iMonth)
         call read_var('iDay',    TimePointStart % iDay)
         call read_var('iHour',   TimePointStart % iHour)
         call read_var('iMinute', TimePointStart % iMinute)
         call read_var('iSecond', TimePointStart % iSecond)
         FracSecond = TimePointStart % FracSecond ! set default value
         call read_var('FracSecond', FracSecond)
         TimePointStart % FracSecond = FracSecond
         call time_int_to_real(TimePointStart)
       case("#POINTSTOP")
         call read_var('iYear',   TimePointStop % iYear)
         call read_var('iMonth',  TimePointStop % iMonth)
         call read_var('iDay',    TimePointStop % iDay)
         call read_var('iHour',   TimePointStop % iHour)
         call read_var('iMinute', TimePointStop % iMinute)
         call read_var('iSecond', TimePointStop % iSecond)
         FracSecond = TimePointStop % FracSecond ! set default value
         call read_var('FracSecond', FracSecond)
         TimePointStop % FracSecond = FracSecond
         call time_int_to_real(TimePointStop)
       case("#POINTMASSSOURCE")
          call read_var('UsePointSource', UsePointSource)
          if(.not.UsePointSource)cycle
          call read_var('RateRotate', raterot)
          ! Convert units:
          raterot = cDegToRad * raterot / (3600.*24.)
          call read_var('nPointSource', nPointSource)
          write(*,*) 'nPointSource = ', nPointSource
          ! Initialize arrays:
          allocate(XyzSource_DI(3, nPointSource))
          allocate(Amplitude_I(nPointSource))
          allocate(AngleInit_I(nPointSource))
          allocate(RadPoint_I(nPointSource))
          XyzSource_DI = 0
          Amplitude_I = 0
          AngleInit_I = 0
          RadPoint_I = 0
          write(*,*) "READING POINT SOURCE INFO"
          do i=1, nPointSource
              call read_var('SourceAmplitude', Amplitude_I(i))
              call read_var('xPosition', XyzSource_DI(1, i))
              call read_var('yPosition', XyzSource_DI(2, i))
              call read_var('zPosition', XyzSource_DI(3, i))
              ! Set angle & radius:
              RadPoint_I(i) = sqrt(XyzSource_DI(1, i)**2 + &
                                   XyzSource_DI(2, i)**2)
              AngleInit_I(i) = atan2(XyzSource_DI(2, i), XyzSource_DI(1, i))
              write(*,'(a,i02,a,e12.7,a,3f10.7)') 'Source #', i, &
                   ' Amplitude=', Amplitude_I(i), &
                   ' located at xyz=', XyzSource_DI(:, i)
              write(*, '(a,f10.2,a,f10.2)') &
                   '     Radius = ', RadPoint_I(i), &
                   ' Angle = ', AngleInit_I(i) / cDegToRad
               ! Convert to SI Units: amu/cm3/s -> kg/m3/s
              Amplitude_I(i) = cProtonMass * 1.0E6 * Amplitude_I(i)
          end do
         case("#POINTSPREAD")
            call read_var('radSpread', rspread)
            write(*,'(a, f8.3)') "POINTSOURCE: Using an rspread of ", rspread
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

    logical:: DoTest
    character(len=*), parameter:: NameSub = 'user_init_session'
    !--------------------------------------------------------------------------
    call test_start(NameSub, DoTest)

    ! Test statement, need to remove later
    if (iProc == 0) then
       write(*,*) 'Hey the user module is working.'
    end if

    call test_stop(NameSub, DoTest)
  end subroutine user_init_session
  !============================================================================
!
!   subroutine user_calc_sources_impl(iBlock)
!
!     use ModMain,       ONLY: nI, nJ, nK, tSimulation
!     use ModAdvance,    ONLY: State_VGB, Source_VC, p_, Rho_
!     use ModGeometry,   ONLY: Xyz_DGB
!     use ModPhysics,    ONLY: Si2No_V, UnitRho_, UnitP_
!
!     integer, intent(in) :: iBlock
!
!     integer :: iPoint, i, j, k
!
!     ! Local source arrays
!     real, dimension(1:nI,1:nJ,1:nK) :: SRho_C, SP_C
!     real :: distNow_D(3), distSource=0, gauss
!
!     logical :: DoTestCell
!
!     logical:: DoTest
!     character(len=*), parameter:: NameSub = 'user_calc_sources_impl'
!     !--------------------------------------------------------------------------
!     call test_start(NameSub, DoTest, iBlock)
!     write(*,*) NameSub // ' has been called.'
!     if(.not.UsePointSource)return
!
!     !! Set the source arrays for this block to zero
!     SRho_C = 0.
!     SP_C = 0.
!
!     do iPoint=1, nPointSource
!         ! Check time to see if source is active.
!         ! HERE!
!
!         ! Calculate source:
!         do k=1,nK; do j=1,nJ; do i=1,nI
!            ! For each point, get distance from point.
!            distNow_D = Xyz_DGB(:, i, j, k, iBlock) - XyzSource_DI(:, iPoint)
!            distSource = sum((distNow_D)**2)
!
!            if (sqrt(distSource)>5.) cycle
!
!            write(*,'(a,3f10.4,a,f10.4)') ' XYZ=', Xyz_DGB(:, i, j, k, iBlock), &
!                'dist = ', sqrt(distSource)
!
!            gauss = (1/sqrt(2*cPi*rspread)) * exp(-1*distSource/(2*rspread**2))
!            write(*,'(a,e12.7)') 'gauss=', gauss
!
!            ! Apply source as Gaussian about central point.
!            SRho_C(i,j,k) = SRho_C(i,j,k) + &
!            Amplitude_I(iPoint)*(1/sqrt(2*cPi*rspread)) * &
!            exp(-1*distSource/(2*rspread**2)) * SI2No_V(UnitRho_)
!          end do; end do; end do
!     end do
!
!     ! Apply sources to Source_VC
!     do k=1,nK; do j=1,nJ; do i=1,nI
!        Source_VC(Rho_,i,j,k) = SRho_C(i,j,k) + &
!             Source_VC(Rho_,i,j,k)
!        !Source_VC(p_,i,j,k) = SP_C(i,j,k) + &
!        !     Source_VC(p_,i,j,k)
!     end do;  end do;  end do
!
!     call test_stop(NameSub, DoTest, iBlock)
!
!   end subroutine user_calc_sources_impl
  !============================================================================
  subroutine user_calc_sources_expl(iBlock)

     use ModMain,       ONLY: nI, nJ, nK, tSimulation
     use ModAdvance,    ONLY: State_VGB, Source_VC, p_, Rho_
     use ModGeometry,   ONLY: Xyz_DGB
     use ModPhysics,    ONLY: Si2No_V, UnitRho_, UnitP_

     integer, intent(in) :: iBlock

     integer :: iPoint, i, j, k

     ! Local source arrays
     real, dimension(1:nI,1:nJ,1:nK) :: SRho_C, SP_C
     real :: distNow_D(3), distSource=0, angleNow

     logical :: DoTestCell

     logical:: DoTest
     character(len=*), parameter:: NameSub = 'user_calc_sources_expl'
     !--------------------------------------------------------------------------
     call test_start(NameSub, DoTest, iBlock)

     if(.not.UsePointSource)return

     ! Update simulation time:
     TimePointNow % Time = TimeStart % Time + tSimulation
     call time_real_to_int(TimePointNow)
     if(DoTest) write(*,*) NameSub, 'Time Now = ', TimePointNow % string

     ! Check start/stop time. Return if outside applicable time.
     if(TimePointStart % iYear > 0) then
      if(TimePointNow % Time < TimePointStart % Time) then
         if(DoTest) write(*,*) NameSub, ' no source applied -- too early.'
         return
      end if
     end if
     if(TimePointStop % iYear > 0) then
      if(TimePointNow % Time > TimePointStop % Time)then
         if(DoTest) write(*,*) NameSub, ' no source applied -- too late.'
         return
      end if
     end if

     !! Set the source arrays for this block to zero
     SRho_C = 0.
     SP_C = 0.

     do iPoint=1, nPointSource
         ! Update source location if rotation:
         angleNow = AngleInit_I(iPoint) + tSimulation * raterot
         XyzSource_DI(1, iPoint) = RadPoint_I(iPoint) * cos(angleNow)
         XyzSource_DI(2, iPoint) = RadPoint_I(iPoint) * sin(angleNow)

         ! Calculate source:
         do k=1,nK; do j=1,nJ; do i=1,nI
            ! For each point, get distance from point.
            distNow_D = Xyz_DGB(:, i, j, k, iBlock) - XyzSource_DI(:, iPoint)
            distSource = sum((distNow_D)**2)

            ! Apply source as Gaussian about central point.
            SRho_C(i,j,k) = SRho_C(i,j,k) + &
                Amplitude_I(iPoint)*(1/sqrt(2*cPi*rspread)) * &
                exp(-1*distSource/(2*rspread**2)) * SI2No_V(UnitRho_)
          end do; end do; end do
     end do

     ! Apply sources to Source_VC
     do k=1,nK; do j=1,nJ; do i=1,nI
        Source_VC(Rho_,i,j,k) = SRho_C(i,j,k) + &
             Source_VC(Rho_,i,j,k)
        !Source_VC(p_,i,j,k) = SP_C(i,j,k)     + &
        !     Source_VC(p_,i,j,k)
     end do;  end do;  end do

     call test_stop(NameSub, DoTest, iBlock)

  end subroutine user_calc_sources_expl
  !============================================================================

end module ModUser
!==============================================================================
