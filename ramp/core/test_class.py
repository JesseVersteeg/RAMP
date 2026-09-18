#test class

class TestClass():
    def __init__(
            self,
            country = None,
            year = 2023

    ):
        
        self.country = country
        self.year = year
        if self.country is not None:
            from ramp.core.mobility_config import MobilityConfig
            self.mobility = MobilityConfig(self.country, self.year)
        
    def print_test(self):
        return print(self.mobility.calendar.get_day_type_mobility('2025-12-08'))
        #self.user.usecase.mobility.calendar.get_day_type_mobility(date)

    def residual_load_data_test(self):
        return print(self.mobility.occasional_use)#('free time','weekday'))
    
    def window_test(self):
        return print(self.mobility.window)

tc = TestClass('NL')
tc.window_test()