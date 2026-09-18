# -*- coding: utf-8 -*-

# %% Definition of the inputs
"""
Input data definition
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.core import User
from datetime import datetime
import importlib
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

startTime = datetime.now()
#%% input definitions
charging = True 
write_variables = True
 
countries = ['NL']
total_users = 200

# Define attributes for charging profiles
charging_mode = 'Plan-day-ahead'
infr_prob = 'piecewise'
logistic = False

#%% User and EV initialisation

#get the country data
def load_country_data(country):
    module_path = f"ramp.mobility_database.Europe.{country}"

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        #only raise custom error if the *module itself* was not found
        if e.name == module_path:
            raise ValueError(f"No EV data found for country '{country}'.")
        else:
            raise  #propagate internal import errors inside the module

    if not hasattr(module, "load_country_ev_data"):
        raise ValueError(f"Module {module_path} does not define load_country_ev_data().")

    return module.load_country_ev_data()  #this should return a dictionary with 3 types of users and 3 types of EV's or 9 sets of data to create the objects
    

#create the objects with country data
def create_users_for_country(country, total_users = total_users):
    country_data = load_country_data(country) #contains all top level data from the file
    User_list = []
    
    for user_type in ['working', 'student', 'inactive']:
        for vehicle_type, params in country_data[user_type].items():

            name = f"{user_type.capitalize()}_{vehicle_type.capitalize()}"
            EVUSER = User(user_name=name, num_users=int(round(total_users*country_data['pop_sh'][user_type]*country_data['vehicle_sh'][vehicle_type])))
            
            EVUSER.add_appliance(
                number=2,
                fixed="no",
                fixed_cycle=0,
                flat="no",
                name=f"{name}_EV",
                car_type=vehicle_type,
                user_type=user_type,
                distance_random_variability=params["distance_random_variability"],
                velocity_random_variability=params["velocity_random_variability"],
                power_random_variability=params["power_random_variability"],
                power_parameters = params["power_parameters"],
                battery_capacity = params["battery_capacity"],
                minimum_waiting_time = 60,
                location_preference_factor=params["location_preference_factor"]
            )

            User_list.append(EVUSER)
            

    return User_list

#%%

if __name__ == "__main__":
    from core.core import UseCase

    for country in countries:
        User_list = create_users_for_country(country)
        
        uc = UseCase(
            users=User_list,
            parallel_processing=False,
            date_start='2018-06-01', 
            date_end = '2018-06-30', 
            peak_enlarge=0.2,
            random_seed=1000,
            country = country
            
        )
        #Mobility demand, generated via the original Appliance pipeline
        Profiles_list = uc.generate_daily_load_profiles(flat=False)  
        
        #Charging demand, generated via new charging pipeline
        if charging:
            Charging_list, Location_charging_list = uc.generate_daily_charging_profiles(charging_mode=charging_mode,
                                                                infr_prob = infr_prob,
                                                                SOC_initial= 0.8, 
                                                                #Ch_stations = ([3.7,11], [1.0,0]),
                                                                logistic = logistic)
            
        #metrics
        charging_coincidence, mobility_usage,total_kwh_per_session = uc.mobility_and_charging_factor()
        ev_locations = uc.ev_locations()
        #travel_counts = uc.daily_travel_counter()
       
        print('\nExecution Time:', datetime.now() - startTime)
        
        # post-processing
        from post_process import post_process as pp
        Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(
            Profiles_list
        )
        Charging_avg, Charging_list_kW, Charging_series = pp.Profile_formatting(
            Charging_list
        )

        pp.Profile_series_plot( #Profiles_series
            Profiles_series
        )  # by default, profiles are plotted as a series
        pp.Profile_series_plot(
            Charging_series
        )

        if (
           len(Profiles_list) > 1
        ):  # if more than one daily profile is generated, also cloud plots are shown 
            pp.Profile_cloud_plot(Profiles_list, Profiles_avg)
        
        if (
           len(Charging_list) > 1
        ):  # if more than one daily profile is generated, also cloud plots are shown 
            pp.Profile_cloud_plot(Charging_list, Charging_avg)

        
        
        dummy_days_corrected = pp.Charging_series_dummy_days(Charging_series, uc.days)
        
        pp.plot_traveling_share(mobility_usage, uc.days)
        pp.Location_mobility_stacked(ev_locations, uc.days)
        pp.plot_locational_load_stacked(Location_charging_list, uc.days)
        #pp.location_curves_non_stacked(ev_locations)
        #pp.Car_trips_distribution(travel_counts)
        
        #export the data
        if write_variables:
            pp.export_series(Profiles_series,4,f"mobility_profile_{country}")
            pp.export_series(dummy_days_corrected,1,f"charging_profile_{country}_{charging_mode}")
            pp.export_series(total_kwh_per_session,1,f"total_kwh_per_session_{country}")
            pp.export_series(mobility_usage,1,f"mobility_usage_{country}")
            #pp.export_stacked_data_to_csv(locational_charging,reference_array=Charging_series,filename=f"locations_scenario_{charging_mode}")
        
        
        

       
