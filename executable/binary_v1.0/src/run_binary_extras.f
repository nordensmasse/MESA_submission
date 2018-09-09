! ***********************************************************************
!
!   Copyright (C) 2012  Bill Paxton
!
!   this file is part of mesa.
!
!   mesa is free software; you can redistribute it and/or modify
!   it under the terms of the gnu general library public license as published
!   by the free software foundation; either version 2 of the license, or
!   (at your option) any later version.
!
!   mesa is distributed in the hope that it will be useful, 
!   but without any warranty; without even the implied warranty of
!   merchantability or fitness for a particular purpose.  see the
!   gnu library general public license for more details.
!
!   you should have received a copy of the gnu library general public license
!   along with this software; if not, write to the free software
!   foundation, inc., 59 temple place, suite 330, boston, ma 02111-1307 usa
!
! *********************************************************************** 
      module run_binary_extras 

      use star_lib
      use star_def
      use const_def
      use chem_def
      use num_lib
      use binary_def
      use crlibm_lib
      
      implicit none
      
      contains
      
      subroutine extras_binary_controls(binary_id, ierr)
         integer :: binary_id
         integer, intent(out) :: ierr
         type (binary_info), pointer :: b
         ierr = 0

         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if
			
         ! Set these function pointers to point to the functions you wish to use in
         ! your run_binary_extras. Any which are not set, default to a null_ version
         ! which does nothing.
         b% how_many_extra_binary_history_columns => how_many_extra_binary_history_columns
         b% data_for_extra_binary_history_columns => data_for_extra_binary_history_columns

         b% extras_binary_startup=> extras_binary_startup
         b% extras_binary_check_model=> extras_binary_check_model
         b% extras_binary_finish_step => extras_binary_finish_step
         b% extras_binary_after_evolve=> extras_binary_after_evolve
         
 	      b% other_extra_jdot => jdot_accretion_routine

         ! Once you have set the function pointers you want, then uncomment this (or set it in your star_job inlist)
         ! to disable the printed warning message,
 	      
         b% warn_binary_extra =.false.
         
      end subroutine extras_binary_controls
      
      subroutine constant_accretion_rate(b)
      	real(dp) :: dotMout, f,f_1,f_2, dotM, Ltotal, q
      	type (binary_info), pointer :: b
			
         dotM = b% s1% x_ctrl(3) !Accretion rate in log(dotM) (Msun/yr)
         
         call distribute_accreted_mass(b,dotM)
         
      end subroutine constant_accretion_rate
		
		subroutine churchwell_henning_accretion_rate(b,Ltotal1,dotM)
			real(dp), intent(in) :: Ltotal1
			real(dp) :: dotMout, f, Ltotal2
			real(dp), intent(out) :: dotM
      	type (binary_info), pointer :: b
			
         Ltotal2 = log10_cr(Ltotal1)
         dotMout = 10**(-5.28 +0.752*(Ltotal2 - 0.0278*Ltotal2*Ltotal2))
         f = 1.d0/11.d0
         dotM = f/(1.d0-f)*dotMout
         
		end subroutine churchwell_henning_accretion_rate
		
		subroutine churchwell_henning_accretion(b)
      	real(dp) :: dotMout, f, dotM, Ltotal
      	type (binary_info), pointer :: b
			
         Ltotal = 10**b% s1% log_surface_luminosity + 10**b% s2% log_surface_luminosity
         call churchwell_henning_accretion_rate(b, Ltotal,dotM)
         call distribute_accreted_mass(b,dotM)

      end subroutine churchwell_henning_accretion

      subroutine exponential_decay_accretion(b)
      	type (binary_info), pointer :: b
      	
      end subroutine exponential_decay_accretion
            	
      subroutine distribute_accreted_mass(b,dotM)
      	real(dp) :: f_1,f_2, dotM, q, q3
      	type (binary_info), pointer :: b
      	
      	if (b% mtransfer_rate/Msun*secyer >= 1d-8) then
				!If donor is overflowing, all accretion onto the system goes to the accretor.
				b% s1% mass_change = 0
				b% s2% mass_change = dotM
! b% s1% x_ctrl(2) defines eta in the equation
! f2/f1 = q^eta
! f1 + f2 = 1
! then
! f2 = f1*q^eta
! and
! f1= 1/(1+q^eta) and f2 = 1 - f1
! for all eta: b% s1% x_ctrl(2)
			else if (b% s1% x_ctrl(2) > 100) then
			! No accretion.
				b% s1% mass_change = 0.d0
				b% s2% mass_change = 0.d0
			else if (b% s1% x_ctrl(2) < -100) then
			! Independent accretion.
				call churchwell_henning_accretion_rate(b,10**b% s1% log_surface_luminosity,dotM)
				b% s1% mass_change = dotM
				call churchwell_henning_accretion_rate(b,10**b% s2% log_surface_luminosity,dotM)
				b% s2% mass_change = dotM
			else	
				! eta = b% s1% x_ctrl(2)
			   ! Bondi Hoyle accretion, eta = 2
				q = b% s2% mstar/b% s1% mstar
         	f_1 = 1.d0 / (1.d0+q**(b% s1% x_ctrl(2)) )	! fraction accreted onto m1
         	f_2 = 1.d0-f_1    				! fraction accreted onto m2
      		b% s1% mass_change = f_1*dotM
      		b% s2% mass_change = f_2*dotM
			endif
			
      end subroutine distribute_accreted_mass
      
      subroutine jdot_accretion_routine(binary_id, ierr)
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr
         real(dp) :: jdot_1, jdot_2,Mdot_in,eta,mdot_1,mdot_2, omega, a3,r1,r2
         type (binary_info), pointer :: b
         ierr = 0
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if!

			! Accretion laws
			if (b% m(1) >= b% s1% x_ctrl(4)*Msun .or. b% m(1) >= b% s1% x_ctrl(4)*Msun) then
				
				write(*,*) 'Stopped accretion'
				! Turn off accretion
				b% s1% x_ctrl(1) = 0
				b% s1% x_ctrl(2) = 1000
				call distribute_accreted_mass(b,0.d0)
				b% use_other_extra_jdot = .false. !Turn off this routine.
				
				! Turn on winds
				b% s1% cool_wind_RGB_scheme = 'Dutch'
   			b% s1% cool_wind_AGB_scheme = 'Dutch'
				b% s1% hot_wind_scheme 		 = 'Dutch'
				
				b% s2% cool_wind_RGB_scheme = 'Dutch'
   			b% s2% cool_wind_AGB_scheme = 'Dutch'
				b% s2% hot_wind_scheme 		 = 'Dutch'
				! New stop condition
				b% s1% stop_near_zams = .true.
				
			else if (b% s1% x_ctrl(1) > 0.5 .and. b% s1% x_ctrl(1) < 1.5) then

				call constant_accretion_rate(b)

			else if (b% s1% x_ctrl(1) > 1.5 .and. b% s1% x_ctrl(1) < 2.5) then

				call churchwell_henning_accretion(b)

			else if (b% s1% x_ctrl(1) > 2.5 .and. b% s1% x_ctrl(1) < 3.5) then

				call exponential_decay_accretion(b)

			end if

      end subroutine jdot_accretion_routine

      integer function how_many_extra_binary_history_columns(binary_id)
         use binary_def, only: binary_info
         integer, intent(in) :: binary_id
         how_many_extra_binary_history_columns = 2
      end function how_many_extra_binary_history_columns
      
      subroutine data_for_extra_binary_history_columns(binary_id, n, names, vals, ierr)
         use const_def, only: dp
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(in) :: n
         character (len=maxlen_binary_history_column_name) :: names(n)
         real(dp) :: vals(n)
         integer :: i
         real(dp) :: star_1_I_rot, star_2_I_rot
         integer, intent(out) :: ierr
         real(dp) :: beta
         ierr = 0
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then
            write(*,*) 'failed in binary_ptr'
            return
         end if
         
         ! column 1
	   	names(1) = 'star_1_I_rot'
	   	star_1_I_rot = 0.d0
	   	i = 0
	   	do i = b% s1% nz, 1, -1
 		  		vals(1) = star_1_I_rot + b% s1%i_rot(i)*b% s1%dm(i)
         end do
         
         names(2) = 'star_2_I_rot'
	   	star_2_I_rot = 0.d0
	   	i = 0
	   	do i = b% s2% nz, 1, -1
 		  		vals(2) = star_2_I_rot + b% s2%i_rot(i)*b% s2%dm(i)
         end do

         ierr = 0
      end subroutine data_for_extra_binary_history_columns
      
      
      integer function extras_binary_startup(binary_id,restart,ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr
         logical, intent(in) :: restart
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if
         
!          b% s1% job% warn_run_star_extras = .false.
      	 extras_binary_startup = keep_going
      end function  extras_binary_startup
      
      !Return either rety,backup,keep_going or terminate
      integer function extras_binary_check_model(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         real(dp) :: max_overflow_factor
         integer :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         
         if (b% rl_relative_gap(2) > -0.005 .and. b% rl_relative_gap(1) > -0.005) then
         	b% s2% termination_code = t_xtra1
            termination_code_str(t_xtra1) = "Terminate because both stars overflow RLO"
            extras_binary_check_model = terminate
            return
			end if
			
			if (log10_cr(abs(b% mtransfer_rate/Msun*secyer)) >= log10_cr(1d-13) ) then
         	b% s2% termination_code = t_xtra2
            termination_code_str(t_xtra2) = "Terminate because mass transfer started"
            extras_binary_check_model = terminate
            return
			end if
			
         extras_binary_check_model = keep_going
        
      end function extras_binary_check_model
      
      
      ! returns either keep_going or terminate.
      ! note: cannot request retry or backup; extras_check_model can do that.
      integer function extras_binary_finish_step(binary_id)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if  
         extras_binary_finish_step = keep_going
         
      end function extras_binary_finish_step
      
      subroutine extras_binary_after_evolve(binary_id, ierr)
         type (binary_info), pointer :: b
         integer, intent(in) :: binary_id
         integer, intent(out) :: ierr
         call binary_ptr(binary_id, b, ierr)
         if (ierr /= 0) then ! failure in  binary_ptr
            return
         end if      
         
 
      end subroutine extras_binary_after_evolve     
      
      end module run_binary_extras
