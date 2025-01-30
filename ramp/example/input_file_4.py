# -*- coding: utf-8 -*-

# %% Definition of the inputs
"""
Input data definition
"""

from ramp.core.core import User
import pandas as pd

User_list = []

#Testcase for NL
tot_users = 10
r_w = {}

P_var = 0.1 #random in power
r_d   = 0.3 #random in distance
r_v   = 0.3 #random in velocity

#Variabilites in functioning windows 
r_w['working'] = 0.25
r_w['student'] = 0.25
r_w['inactive'] = 0.2
r_w['free time'] = 0.2

#Occasional use 
occasional_use = {}

occasional_use['weekday'] = 1
occasional_use['saturday'] = 0.6
occasional_use['sunday'] = 0.5
occasional_use['free time'] = {'weekday': 0.15, 'weekend': 0.3} #1/7, meaning taking car for free time once a week

#Calibration parameters for the Velocity - Power Curve [kW]
Par_P_EV = {}

Par_P_EV['small']  = [0.26, -13, 546]
Par_P_EV['medium'] = [0.3, -14, 600]
Par_P_EV['large']  = [0.35, -15.2, 620]

#Battery capacity [kWh]
Battery_cap = {}

Battery_cap['small']  = 37
Battery_cap['medium'] = 60
Battery_cap['large']  = 100


pop_share_list = [0.608482569,0.064493573,0.327023857]
user_type = ['working', 'student', 'inactive']
pop_sh = dict(zip(user_type,pop_share_list))

vehicle_share_list = [0.0,0.0,1.0]
vehicle_type = ['small', 'medium', 'large']
vehicle_sh = dict(zip(vehicle_type,vehicle_share_list))


"""
Firt representation of an EV vehicle as appliance for transferring RAMP-mobility to RAMP.
"""
#this is work in progress for EV
# Create new user classes
Working_L = User(user_name = "Working - Large car", 
                 user_preference = 0,
                 num_users = int(round(tot_users*pop_sh['working']*vehicle_sh['large'])))
User_list.append(Working_L)
print(User_list)

#HH_shower_P = pd.read_csv("ramp/example/shower_P.csv")
#Working Large, weekday, W-windows
Working_EV_large_wd = Working_L.add_appliance(
    number=1,
    power=1000,
    num_windows=2,
    func_time=50,
    time_fraction_random_variability=0.1,
    func_cycle=3,
    fixed="no",
    fixed_cycle=0,
    occasional_use=1,
    flat="no",
    thermal_p_var=0.2,
    pref_index=0,
    wd_we_type=2,
    name="EV",
    test =1,
    distance_total = 50,
    randomised_distance= 0.3,
    randomised_velocity= 0.3,
    distance_minimal= 50,
    power_parameters = Par_P_EV['large'], 
    battery_capacity = Battery_cap['large'],  
    location = None,  
)
#Working Large, weekday, FT-windows

Working_EV_large_wd.windows(window_1=[390, 540], window_2=[1080, 1200], random_var_w=0.2)

# Working - Large Car - Weekday -> TO DO this needs to be processed for defining the objects above
#Find a better way to define the objects so that not all need to be defined seperatly

def temperature_correction():
    pass

if __name__ == "__main__":
    from ramp.core.core import UseCase

    uc = UseCase(
        users=User_list,
        parallel_processing=False,
    )
    uc.initialize(peak_enlarge=0.15)

    Profiles_list = uc.generate_daily_load_profiles(flat=False)

    # post-processing
    from ramp.post_process import post_process as pp

    Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(
        Profiles_list
    )
    pp.Profile_series_plot(
        Profiles_series
    )  # by default, profiles are plotted as a series
    if (
        len(Profiles_list) > 1
    ):  # if more than one daily profile is generated, also cloud plots are shown
        pp.Profile_cloud_plot(Profiles_list, Profiles_avg)

    # this would be a new method using work of @mohammadamint
    # results = uc.export_results()
