# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import copy
from pathlib import Path
from datetime import date
import pytz
import random
import holidays

#Files with the inputs to be loaded 
inputfolder = Path(__file__).parent.parent 
inputfolder = inputfolder /"mobility_database/" 

# Total daily distance [km]
d_tot_file =  inputfolder /"d_tot.csv" 
d_tot_data = pd.read_csv(d_tot_file, header = 0, index_col = 0)

# Distance by trip [km]
d_min_file =  inputfolder /"d_min.csv" 
d_min_data = pd.read_csv(d_min_file, header = 0, index_col = [0,1])

# Functioning time by trip [min]
t_func_file =  inputfolder /"t_func.csv" 
t_func_data = pd.read_csv(t_func_file, header = 0, index_col = [0,1])

# Functioning windows 
window_file =  inputfolder /"windows.csv" 
window_data = pd.read_csv(window_file, header = [0,1], index_col = [0,1,2])
window_data = window_data*60
window_data = window_data.astype(int)

# Infrastructure availability per type of location
infrastructure_per_location_file = inputfolder/"charging_infrastructure.xlsx"
infrastructure_per_location_data = pd.read_excel(infrastructure_per_location_file, index_col=[0,1])
#print(infrastructure_per_location_data)

infra_availability_file = inputfolder/"availability_infrastructure.xlsx"
infra_availability_data = pd.read_excel(infra_availability_file, index_col=[0,1])


class MobilityCalendar:
    def __init__(self, country: str, year: int):
        self.country = country
        self.year = year
        self._holidays = None

    @property
    def holidays(self):
        #check for holidays
        if self._holidays is None:
            self._holidays = set(
                holidays.country_holidays(self.country, years=self.year).keys()
            )
        return self._holidays

    def get_day_type_mobility(self, day):
        """Return weekday/saturday/sunday based on date and national holidays."""
        if isinstance(day, str):
            day = date.fromisoformat(day)
        elif hasattr(day, "to_pydatetime"):
            day = day.to_pydatetime().date()
        else:
            day = day.date()

        #holiday acts like sunday in mobility profile
        if day in self.holidays:
            return "sunday"

        wd = day.weekday()
        if wd <= 4:
            return "weekday"
        elif wd == 5:
            return "saturday"
        else:
            return "sunday"
    
#Variabilites in functioning windows 
def get_random_var_w(user_type):
    r_w = {}
    r_w['working'] = 0.25 #0.25
    r_w['student'] = 0.25 #0.25
    r_w['inactive'] = 0.2 #0.2
    return r_w[user_type]

def get_occasional_use(): #get_occasional_use(window_type, day_type):
    #Occasional use 
    occasional_use = {}

    occasional_use['main'] = {'weekday': 1, 'saturday': 1,'sunday': 1} #saturday default setting is 0.6. sunday default setting is 0.5
    # occasional_use['saturday'] = 1 # default setting is 0.6
    # occasional_use['sunday'] = 1 #default setting is 0.5
    occasional_use['free time'] = {'weekday': 0.15, 'saturday': 0.3,'sunday':0.3} #1/7, meaning taking car for free time once a week
    #0.15,0.3,0.3 for the free time values
    return occasional_use

def get_equivalent_country(country):
        # For the data coming from the JRC Survey, a dictionary is defined to assign each country to the neighbouring one
        # these data are: d_tot, d_min, t_func, trips distribution by time (adopted from RAMP-mobility)
        if country is None:
            raise RuntimeError("utils_mobility has not been configured with a country.")

        # country equivalent dictionary
        country_dict = {
            'AT':'DE', 'CH':'DE', 'CZ':'DE', 'DK':'DE', 'FI':'DE', 'HU':'DE', 'NO':'DE','SE':'DE', 'NL':'DE','SK':'DE', 'NL_2':'DE',
            'PT':'ES',
            'BE':'FR', 'LU':'FR',
            'EL':'IT', 'HR':'IT', 'MT':'IT', 'SI':'IT',
            'IE':'UK',
            'BG':'PL', 'CY':'PL', 'EE':'PL', 'LT':'PL', 'LV':'PL', 'RO':'PL'
        }

        # Selection of the equivalent country from the dictionary defined above
        if country in set(country_dict.values()):
            country_equivalent = country
        else:
            country_equivalent = country_dict[country]
        return country_equivalent



def load_mobility_data_country(country):
        #read in residual load file
        inputfile_residual_load = inputfolder/"residual_load"/f"residual_load_{country}.csv"
        read_residual_load = pd.read_csv(inputfile_residual_load, index_col = 0)

        #read in temperature correction file
        temp_file = inputfolder /"temp_ninja_pop_1980-2019.csv"
        temperature_read = pd.read_csv(
            temp_file, 
            index_col=0
            )[[country]]
        
        #make index isoformat with YYYY-MM-DD and get the slice from the dataframe
        temperature_read.index = pd.to_datetime(temperature_read.index)

        temperature_lookup = {}

        for day, group in temperature_read.groupby(temperature_read.index.date):

            #create minute-resolution index
            start_time = pd.Timestamp(day)
            end_time = start_time + pd.Timedelta(days=1) - pd.Timedelta(minutes=1)

            minutes = pd.date_range(
                start=start_time,
                end=end_time,
                freq="min"
            )

            #hourly to minute resolution
            group = group.reindex(minutes, method="ffill")

            temp = group[country].to_numpy()

            #vectorized temperature correction arary
            correction = np.where(
                temp < 15,
                1.12 - 0.01 * temp,
                np.where(
                    temp <= 20,
                    1.0,
                    0.63 + 0.02 * temp
                )
            )

            #store as np.array into dictionary for look up
            temperature_lookup[day] = correction.astype(np.float32)
          
        # Location 
        location_file = inputfolder/f'location_share_{country}.csv'
        location_data = pd.read_csv(location_file,  sep=';', decimal=',', encoding='utf-8', header=0, skiprows=[1,2])
        location_data.drop(labels=['Total'] , axis=1, inplace=True)
        location_data.loc[:, 'ACL00 (Labels)'] = location_data['ACL00 (Labels)'].str.replace('From ', '').str.replace('to ', '')
        location_data = location_data.rename(columns={'ACL00 (Labels)':'Starttime',
                                                    'Household and family care activities':'Errands',
                                                    'Leisure social and associative life except TV and video':'Leisure',
                                                    'Work and study': 'Work/Study'})

        location_data.reset_index(drop=True, inplace=True)
        location_mapping = location_data.copy()
        location_mapping.drop(labels=['Starttime'], axis=1,inplace=True)
        specified_locations = list(location_mapping.columns)
        
        

        # Initialize output dictionary
        location_dict = {}

        for idx, row in location_data.iterrows():
            # Parse interval bounds from "Starttime"
            time_range = row['Starttime']
            start_str, end_str = time_range.split()
            start_minute = int(start_str[:2]) * 60 + int(start_str[3:])
            end_minute = int(end_str[:2]) * 60 + int(end_str[3:])
            
            # For each minute in the interval
            for minute in range(start_minute, end_minute + 1):
                location_dict[minute] = {
                    'Work/Study': float(row['Work/Study']),
                    'Errands': float(row['Errands']),
                    'Leisure': float(row['Leisure']),
                    'Home': float(row['Home']),
                }

        
        return read_residual_load, temperature_lookup, location_dict, specified_locations

def load_mobility_data_country_equivalent(country_equivalent):
    d_tot = {}
    d_tot['weekday']  = d_tot_data.loc[country_equivalent, 'weekday']
    d_tot['saturday'] = d_tot_data.loc[country_equivalent, 'weekend']
    d_tot['sunday']   = d_tot_data.loc[country_equivalent, 'weekend']

    d_min = {}

    for day in ['weekday', 'saturday', 'sunday']:    
        d_min[day] = {}
        for travel_type in ['business', 'personal']:
            d_min[day][travel_type] = d_min_data[country_equivalent][travel_type][day]
        d_min[day]['mean']  = round(np.array([d_min[day][k] for k in d_min[day]]).mean())


    for day, travel_type in d_min.items():
        if 'business' in travel_type:
            travel_type['main'] = travel_type.pop('business')
        if 'personal' in travel_type:
            travel_type['free time'] = travel_type.pop('personal')
    
    # Functioning time by trip [min]
    t_func = {}

    for day in ['weekday', 'saturday', 'sunday']:    
        t_func[day] = {}
        for travel_type in ['business', 'personal']:
            t_func[day][travel_type] = t_func_data[country_equivalent][travel_type][day]    
        t_func[day]['mean']  = round(np.array([t_func[day][k] for k in t_func[day]]).mean())

    for day, travel_type in t_func.items():
        if 'business' in travel_type:
            travel_type['main'] = travel_type.pop('business')
        if 'personal' in travel_type:
            travel_type['free time'] = travel_type.pop('personal')


    trips = {}
    for day in ['weekday', 'saturday', 'sunday']:    
        file =  inputfolder /f"trips_by_time_{day}.csv" 
        trips[day] = pd.read_csv(file, header = 0)
        trips[day] = trips[day][country_equivalent]/100

    return d_tot, d_min, t_func, trips

# Functioning windows 
def set_windows(country,trips, window_data = window_data):
    if country in window_data.columns.get_level_values(0):    
        country_window = country
    else: 
        print('\n[WARNING] There are no specific functioning windows defined for the selected country, standard windows will be used. \nEdit the "windows.csv" file to add specific functioning windows.\n')
        country_window = 'Standard'
        
    window = {}

    window['working']   = { 'main':         [[window_data[country_window]['Start']['Working']['Main'][1],       window_data[country_window]['End']['Working']['Main'][1]],  
                                            [window_data[country_window]['Start']['Working']['Main'][2],       window_data[country_window]['End']['Working']['Main'][2]]], 
                            'free time':    [[window_data[country_window]['Start']['Working']['Free time'][1],  window_data[country_window]['End']['Working']['Free time'][1]],   
                                            [window_data[country_window]['Start']['Working']['Free time'][2],  window_data[country_window]['End']['Working']['Free time'][2]], 
                                            [window_data[country_window]['Start']['Working']['Free time'][3],  window_data[country_window]['End']['Working']['Free time'][3]]]}
    window['student']   = { 'main':         [[window_data[country_window]['Start']['Student']['Main'][1],       window_data[country_window]['End']['Student']['Main'][1]],  
                                            [window_data[country_window]['Start']['Student']['Main'][2],       window_data[country_window]['End']['Student']['Main'][2]]],                                     
                            'free time':    [[window_data[country_window]['Start']['Student']['Free time'][1],  window_data[country_window]['End']['Student']['Free time'][1]],    
                                            [window_data[country_window]['Start']['Student']['Free time'][2],  window_data[country_window]['End']['Student']['Free time'][2]],
                                            [window_data[country_window]['Start']['Student']['Free time'][3],  window_data[country_window]['End']['Student']['Free time'][3]]]}
    window['inactive']  = { 'main':         [[window_data[country_window]['Start']['Inactive']['Main'][1],      window_data[country_window]['End']['Inactive']['Main'][1]]], 
                            'free time':    [[window_data[country_window]['Start']['Inactive']['Free time'][1], window_data[country_window]['End']['Inactive']['Free time'][1]],   
                                            [window_data[country_window]['Start']['Inactive']['Free time'][2], window_data[country_window]['End']['Inactive']['Free time'][2]]]}

    #Re-format functioning windows to calculate the Percentage of travels in functioning windows from minutes to hours
    wind_temp = copy.deepcopy(window)
    for key in wind_temp.keys():
        for act in ['main', 'free time']:
            wind_temp[key][act] = [item for sublist in window[key][act] for item in sublist]
            wind_temp[key][act] = [(x / 60) for x in wind_temp[key][act]]


    #Percentage of travels in functioning windows 

    #main and free time is defined according to the functioning windows
    #If the windows are modified, also the perentages should be modified accordingly
    perc_usage = {}

    perc_usage['weekday']  = {'working' :{'main': trips['weekday'].iloc[np.r_[wind_temp['working']['main'][0]:wind_temp['working']['main'][1], wind_temp['working']['main'][2]:wind_temp['working']['main'][3]]].sum()},
                            'student' :{'main': trips['weekday'].iloc[np.r_[wind_temp['student']['main'][0]:wind_temp['student']['main'][1], wind_temp['student']['main'][2]:wind_temp['student']['main'][3]]].sum()}, 
                            'inactive':{'main': trips['weekday'].iloc[np.r_[wind_temp['inactive']['main'][0]:wind_temp['inactive']['main'][1]]].sum()}}
    perc_usage['saturday'] = {'working' :{'main': trips['saturday'].iloc[np.r_[wind_temp['working']['main'][0]:wind_temp['working']['main'][1], wind_temp['working']['main'][2]:wind_temp['working']['main'][3]]].sum()},
                            'student' :{'main': trips['saturday'].iloc[np.r_[wind_temp['student']['main'][0]:wind_temp['student']['main'][1], wind_temp['student']['main'][2]:wind_temp['student']['main'][3]]].sum()}, 
                            'inactive':{'main': trips['saturday'].iloc[np.r_[wind_temp['inactive']['main'][0]:wind_temp['inactive']['main'][1]]].sum()}}
    perc_usage['sunday']   = {'working' :{'main': trips['sunday'].iloc[np.r_[wind_temp['working']['main'][0]:wind_temp['working']['main'][1], wind_temp['working']['main'][2]:wind_temp['working']['main'][3]]].sum()},
                            'student' :{'main': trips['sunday'].iloc[np.r_[wind_temp['student']['main'][0]:wind_temp['student']['main'][1], wind_temp['student']['main'][2]:wind_temp['student']['main'][3]]].sum()}, 
                            'inactive':{'main': trips['sunday'].iloc[np.r_[wind_temp['inactive']['main'][0]:wind_temp['inactive']['main'][1]]].sum()}}

    #Calulate the percentage of travels in functioning windows for free time as complementary to the main time 
    for key in perc_usage.keys():
        for us_type in ['working', 'student', 'inactive']:
            perc_usage[key][us_type]['free time'] = 1 - perc_usage[key][us_type]['main']
    
    return window, perc_usage

#%% Functions for charging module
def infrastructure_probability(location, park_index, infrastructure_per_location_data=infrastructure_per_location_data):
    #calculate the hour of the day
    day_number = (park_index // 1440) #get the day
    index_day_residual = park_index - (day_number*1440)
    hour = index_day_residual // 60

    choices = infrastructure_per_location_data.loc[(location,hour)]
    kw_list = choices.index.tolist()
    prob_list = choices.values.tolist()
    infrastructure_mix = {float(k): v for k, v in zip(kw_list, prob_list)}
    
    #scaled_probability = [round((ele * infr_availability),2) for ele in list(infrastructure_mix.values())]
    
    #this need to about a dataframe or dictionary that can be a look up instead of calling it each time
    if sum(prob_list) > 0:
        return random.choices(
            list(infrastructure_mix.keys()), 
            weights=prob_list
        )[0]
    else:
        return random.choice(list(infrastructure_mix.keys()))
    

def charging_probability_extended(
    SOC, SOC_min, SOC_next_travel,
    alpha_location,
    dwell,     
    beta_dwell=0.5,    
    T_min=60, T_max=300
):
    #normalize dwelling time
    t_dwell = min(1.0, max(0.0, (dwell - T_min) / (T_max - T_min)))

    #total alpha
    alpha_eff = alpha_location * (1 + beta_dwell * t_dwell)

    #SoC dependency
    if SOC < SOC_min + SOC_next_travel:
        p = 1.0
    else:
        x = (SOC - SOC_next_travel) / (1 - SOC_next_travel)
        p = 1 - x**alpha_eff

    return np.clip(p, 0.0, 1.0)
    

def charge_prob(SOC):
    
    k = 15
    per_SOC = 0.5
    
    p = 1-1/(1+np.exp(-k*(SOC-per_SOC)))
       
    return p

def charge_prob_const(SOC):        
    
    p = 1       
    
    return p

def SOC_initial_f(SOC_max, SOC_min):
    
    SOC_i = np.random.rand()*(SOC_max-SOC_min) + SOC_min
    
    return SOC_i

def SOC_initial_f_const(SOC_initial):
    
    SOC_i = SOC_initial
        
    return SOC_i

def charge_check_smart(ind_park_range, charge_range):
    
    b = np.isin(ind_park_range, charge_range, assume_unique = True).any()

    return b

def charge_check_normal(ind_park_range, charge_range):
    
    b = True

    return b

def residual_load(minutes, residual_load, year, country):
    
    if country == 'EL':
        country_tz = 'GR'
    elif country == 'UK':
        country_tz = 'GB'
    else:
        country_tz = country

    minutes = minutes.map(lambda dt: dt.replace(year=year))
    residual_load_temp = pd.DataFrame(residual_load.values)
    
    ind_init = pd.date_range(start= f'{year}-01-01', end=f'{year}-12-31 23:00', freq='min', tz = 'UTC')
    residual_load_temp.set_index(ind_init, inplace = True)
    
    residual_load_temp_tz = residual_load_temp.tz_convert(pytz.country_timezones[country_tz][0])
    residual_load_temp = residual_load_temp_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    residual_load_temp = residual_load_temp[~residual_load_temp.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion
    
    residual_load_temp = residual_load_temp.loc[minutes[0]: minutes[-1]] #filter for the simulated period
    res_load_neg = residual_load_temp[residual_load_temp < 0].fillna(0)
            
    res_load_neg_ind = np.nonzero(res_load_neg.values)[0]
    
    return res_load_neg_ind

def tot_users_calc(User_list):
    # Calculation of the total number of users
    num_users = {}
    for i in range(len(User_list)):
        num_users[User_list[i].user_name] = User_list[i].num_users
        tot_users = sum(num_users.values())
    
    return tot_users

def tot_battery_cap_calc(User_list):
    # Calculation of the total fleet battery capacity
    cap_users = {}
    for Us in User_list:
        cap_users[Us.user_name] = Us.num_users *  Us.App_list[0].Battery_cap
        tot_cap_users = sum(cap_users.values())
    
    return tot_cap_users