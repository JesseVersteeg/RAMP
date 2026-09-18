# -*- coding: utf-8 -*-

# %% Definition of the inputs
"""
Input data definition
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.core import User
import pandas as pd
import numpy as np
from datetime import date

percentage_list = [0.07, 0.35, 0.2, 0.01, 0.04, 0.02, 0.04, 0.19, 0.11]
total_users = 100
number_users = [round(total_users*i) for i in percentage_list]
User_list = []

"""
First representation of an EV vehicle as appliance for transferring RAMP-mobility to RAMP.
"""

# Create new user classes
Working_L_User = User(user_name = "Large Car - Working", 
                 num_users = number_users[0] )   
User_list.append(Working_L_User)

Working_L_EV = Working_L_User.add_appliance(
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    name ="Working_L_EV",
    car_type = 'large',
    user_type = 'working',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2)



Working_M_User = User(user_name = "Medium Car - Working", 
                 num_users = number_users[1]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Working_M_User)
    
Working_M_EV = Working_M_User.add_appliance(
    name ="Working_M_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'medium',
    user_type = 'working',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2
) 
#Student_M_EV.windows(window_1=[600, 633], window_2=[635, 1113], window_3=[1200,1234], random_var_w = 0.3)

Working_S_User = User(user_name = "Small Car - Working", 
                 num_users = number_users[2]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Working_S_User)
    
Working_S_EV = Working_S_User.add_appliance(
    name ="Working_S_User",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'small',
    user_type = 'working',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

Student_L_User = User(user_name = "Large Car - Student", 
                 num_users = number_users[3]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Student_L_User)
    
Student_L_EV = Student_L_User.add_appliance(
    name ="Student_L_User",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'large',
    user_type = 'student',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 1) 

Student_M_User = User(user_name = "Medium Car - Student", 
                 num_users = number_users[4]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Student_M_User)
    
Student_M_EV = Student_M_User.add_appliance(
    name ="Student_M_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'medium',
    user_type = 'student',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

Student_S_User = User(user_name = "Small Car - Student", 
                 num_users = number_users[5]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Student_S_User)
    
Student_S_EV = Student_S_User.add_appliance(
    name ="Student_S_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'small',
    user_type = 'student',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

Inactive_L_User = User(user_name = "Large Car - Inactive", 
                 num_users = number_users[6]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Inactive_L_User)
    
Inactive_L_EV = Inactive_L_User.add_appliance(
    name ="Inactive_L_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'large',
    user_type = 'inactive',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

Inactive_M_User = User(user_name = "Medium Car - Inactive", 
                 num_users = number_users[7]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Inactive_M_User)
    
Inactive_M_EV = Inactive_M_User.add_appliance(
    name ="Inactive_M_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'medium',
    user_type = 'inactive',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

Inactive_S_User = User(user_name = "Small Car - Inactive", 
                 num_users = number_users[8]) #Add App_list to which the instances of App are saved  #int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Inactive_S_User)
    
Inactive_S_EV = Inactive_S_User.add_appliance(
    name ="Inactive_S_EV",
    number=1,
    fixed="no",
    fixed_cycle=0,
    flat="no",
    car_type = 'small',
    user_type = 'inactive',
    distance_random_variability = 0.3, 
    velocity_random_variability = 0.3,
    power_random_variability = 0.1,
    electric_vehicle = True,
    location_preference_factor = 2) 

if __name__ == "__main__":
    from core.core import UseCase

    uc = UseCase(
        users=User_list,
        parallel_processing=False,
        # date_start='2025-06-12',
        # date_end = '2025-06-20',
        peak_enlarge=0.0,
    )
    
    uc.initialize(num_days=7, peak_enlarge=0.0)
    Profiles_list = uc.generate_daily_load_profiles(flat=False)  #total energy usage, we need the single ones for charging individual EV's
    Charging_list = uc.generate_daily_charging_profiles(charging_mode='Plan-day-ahead', 
                                                        infr_prob = 'piecewise', 
                                                        SOC_initial=0.8, 
                                                        Ch_stations = ([3.7, 11, 120], [0.6, 0.4, 0.0]),
                                                        logistic = False)
    
    
    
   
    # post-processing
    from post_process import post_process as pp

    Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(
        Profiles_list)
    
    pp.export_series(Profiles_series,4,'mobility_base') #this also works for CHarging module: -> test this
    pp.Profile_series_plot(
        Profiles_series
    )  # by default, profiles are plotted as a series
    if (
       len(Profiles_list) > 1
    ):  # if more than one daily profile is generated, also cloud plots are shown 
        pp.Profile_cloud_plot(Profiles_list, Profiles_avg)
    
    Charging_avg, Charging_list_kW, Charging_series = pp.Profile_formatting(
        Charging_list
    )
    travel_counts = uc.daily_travel_counter()
    ev_locations = uc.ev_locations()
    pp.export_series(Charging_series,1,'charging_perfectforesight')
    pp.Charging_series_plot(Charging_series, uc.days)
    pp.Car_trips_distribution(travel_counts)
    pp.Location_stacked_area_plot(ev_locations, uc.days)
        
    #by default, profiles are plotted as a series
    # if (
    #    len(Charging_list) > 1
    # ):  # if more than one daily profile is generated, also cloud plots are shown
    
    pp.Charging_cloud_plot(Charging_list)

    # this would be a new method using work of @mohammadamint
    # result = uc.export_to_dataframe()
    # uc.save('save_test')
