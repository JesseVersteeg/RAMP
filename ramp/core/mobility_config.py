#Configuration class that sets non-static data for EV Appliance

from . import utils_mobility

class MobilityConfig:
    def __init__(self, country: str, year: int):
        
        self.country = country
        self.year = year

        self.country_equivalent = utils_mobility.get_equivalent_country(self.country)
        print(f'loading in data...')

        # load country-equivalent datasets
        (self.d_tot,
         self.d_min,
         self.t_func,
         self.trips) = utils_mobility.load_mobility_data_country_equivalent(self.country_equivalent)

        # load country-specific datasets
        (self.residual_load_data,
         self.temperature,
         self.location_dict,
         self.specified_locations) = utils_mobility.load_mobility_data_country(self.country) 
        
        self.residual_load = utils_mobility.residual_load

        # windows + percentage usage (computed with module-level window_data)
        self.window, self.perc_usage = utils_mobility.set_windows(self.country, self.trips)

        # calendar
        self.calendar = utils_mobility.MobilityCalendar(self.country, self.year)

        self.charge_prob = utils_mobility.charge_prob
        self.charge_prob_const = utils_mobility.charge_prob_const
        self.charge_check_smart = utils_mobility.charge_check_smart
        self.charge_check_normal = utils_mobility.charge_check_normal
        self.infrastructure_probability = utils_mobility.infrastructure_probability
        self.SOC_initial_f = utils_mobility.SOC_initial_f
        self.SOC_initial_f_const = utils_mobility.SOC_initial_f_const
        self.occasional_use = utils_mobility.get_occasional_use()
        self.charging_probability_extended = utils_mobility.charging_probability_extended
        self.random_var_w = utils_mobility.get_random_var_w
        self.infrastructure_availability = utils_mobility.infra_availability_data

        print(f'data loading completed')

    # functions to be called for requesting attribute values
    def get_d_tot(self):
        return self.d_tot

    def get_d_min(self):
        return self.d_min
    
    def get_t_func(self):
        return self.t_func

    def get_windows(self):
        return self.window

    def get_perc_usage(self):
        return self.perc_usage

    def get_residual_load(self):
        return self.residual_load

    def get_temperature(self):
        return self.temperature

    def get_location_dict(self):
        return self.location_dict
    
