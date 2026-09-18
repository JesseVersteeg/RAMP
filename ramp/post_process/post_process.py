import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os.path
import numpy as np


BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Post-processing
"""
Just some additional code lines to calculate useful indicators and generate plots
"""


def Profile_formatting(stoch_profiles):
    Profile_avg = np.zeros(1440)
    for pr in stoch_profiles:
        Profile_avg = Profile_avg + pr
    Profile_avg = Profile_avg / len(stoch_profiles)

    Profile_kW = []
    for kW in stoch_profiles:
        Profile_kW.append(kW / 1000)

    Profile_series = np.array([])
    for iii in stoch_profiles:
        Profile_series = np.append(Profile_series, iii)

    return (Profile_avg, Profile_kW, Profile_series)


def Profile_cloud_plot(stoch_profiles, stoch_profiles_avg):
    # x = np.arange(0,1440,5)
    plt.figure(figsize=(10, 5))
    for n in stoch_profiles:
        plt.plot(np.arange(1440), n, "#b0c4de")
        plt.xlabel("Time (hours)")
        plt.ylabel("Power (W)")
        plt.ylim(ymin=0)
        # plt.ylim(ymax=5000)
        plt.margins(x=0)
        plt.margins(y=0)
    plt.plot(np.arange(1440), stoch_profiles_avg, "#4169e1")
    plt.xticks(
        [0, 240, 480, (60 * 12), (60 * 16), (60 * 20), (60 * 24)],
        [0, 4, 8, 12, 16, 20, 24],
    )
    # plt.savefig('profiles.eps', format='eps', dpi=1000)
    plt.show()


def Profile_series_plot(stoch_profiles_series):
    # x = np.arange(0,1440,5)
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(len(stoch_profiles_series)), stoch_profiles_series, "#4169e1")
    plt.xlabel('Time (minutes)')
    plt.ylabel("Power (W)")
    plt.ylim(ymin=0)
    #plt.ylim(ymax=14000)
    plt.margins(x=0)
    plt.margins(y=0)
    # plt.xticks([0,240,480,(60*12),(60*16),(60*20),(60*24)],[0,4,8,12,16,20,24])
    # plt.savefig('profiles.eps', format='eps', dpi=1000)
    plt.show()

#temporary function to shave off the dummy days that are used to for warm-up and cooldown time of the model
def Charging_series_dummy_days(stoch_profiles_series, days):
    dummy_days = 2
    dummy_minutes = dummy_days * 1440
    stoch_profiles_capped = stoch_profiles_series[dummy_minutes:-dummy_minutes]

    # start_plot = days[2].strftime('%Y-%m-%d 00:00')
    # time_index = pd.date_range(start=start_plot, periods=len(stoch_profiles_capped), freq='min')
    # plt.figure(figsize=(10, 5))
    # plt.plot(time_index, stoch_profiles_capped, "green")
    
    # plt.xticks(rotation=90)
    # plt.ylabel('Power [kW]', fontsize = 10)
    # plt.title("Charging Demand Profile", fontsize = 10)
    # plt.tight_layout()
    # plt.grid(False)
    # plt.show()
    return stoch_profiles_capped

def Charging_cloud_plot(stoch_profiles):
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)

    reshaped_charging = stoch_profiles.reshape((len(stoch_profiles) // 1440, 1440))
    Charge_avg = np.mean(reshaped_charging, axis=0)

    x = np.arange(1440)  # x-axis in minutes

    # Plot individual profiles
    for profile in reshaped_charging:
        ax.plot(x, profile, color="#c6e1cd", linewidth=1, alpha=0.5)

    # Plot average profile
    ax.plot(x, Charge_avg, color="#20792d", linewidth=2)

    # Format axes
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Power (kW)")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0, right=1440)

    # Set x-axis ticks at every 4 hours
    ax.set_xticks([0, 240, 480, 720, 960, 1200, 1440])
    ax.set_xticklabels([0, 4, 8, 12, 16, 20, 24])

    plt.tight_layout()
    plt.show()

def plot_traveling_share(travel_share, days):
    """
    Parameters
    ----------
    travel_share : np.ndarray
        Array of length days*1440 containing the share of EVs traveling
        at every minute (0-1).

    days : pd.DatetimeIndex
        Simulation days.
    """

    # convert to percentage
    travel_percentage = travel_share * 100

    plt.figure(figsize=(12, 6))

    plt.plot(
        np.arange(len(travel_percentage)),
        travel_percentage,
        linewidth=1,
        color='orange'
    )

    # day ticks
    xticks = np.arange(0, len(travel_percentage), 1440)
    plt.xticks(xticks, days.strftime('%d-%m'))

    plt.grid(axis='x', linestyle='--')
    plt.grid(alpha=0.3)

    plt.title('Usage Profile')
    plt.xlabel('Day')
    plt.ylabel('Traveling vehicles [% of total users]')

    plt.tight_layout()
    plt.show()


def Location_mobility_stacked(location_profiles, days):

    LOCATION_ORDER = [
        "Home",
        "Work/Study",
        "Errands",
        "Leisure",
        "traveling"
    ]

    total_minutes = location_profiles.shape[0]

    location_counts = np.stack([np.sum(location_profiles == loc_id, axis=1)for loc_id in range(len(LOCATION_ORDER))],axis=1)
    location_counts = (location_counts /location_counts.sum(axis=1, keepdims=True))

    plt.figure(figsize=(12, 6))

    plt.stackplot(
        np.arange(total_minutes),
        location_counts.T,
        labels=LOCATION_ORDER
    )

    xticks = np.arange(0, total_minutes, 1440)
    plt.xticks(xticks, days.strftime('%d-%m'))

    plt.grid(axis='x', linestyle='--')

    plt.title("Vehicle Location Over Time")
    plt.xlabel("Days")
    plt.ylabel("Share [-]")

    plt.legend(
        title="Location",
        bbox_to_anchor=(1.05, 1),
        loc='upper left'
    )

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import numpy as np

def plot_locational_load_stacked(locational_load, days=None):

    locations = list(locational_load.keys())

    profiles = np.vstack([
        locational_load[loc]
        for loc in locations
    ])

    T = profiles.shape[1]

    plt.figure(figsize=(12, 6))

    plt.stackplot(
        np.arange(T),
        profiles,
        labels=locations
    )

    if days is not None:
        xticks = np.arange(0, T, 1440)
        plt.xticks(xticks, days.strftime('%d-%m'))

    plt.grid(axis='x', linestyle='--')
    plt.xlabel("Time")
    plt.ylabel("Charging Power [kW]")
    plt.title("Locational Charging Demand")
    plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    plt.show()

def location_curves_non_stacked(loc_df):#, days):
    location_counts = loc_df.apply(lambda row: row.value_counts(), axis=1).fillna(0)
    location_counts = location_counts.drop(labels='traveling', axis=1)

    # Step 2: Convert counts to percentages
    percentage_df = location_counts.div(loc_df.shape[1], axis=0) * 100

    # Step 3: Plot the percentage per location over time
    plt.figure(figsize=(14, 6))
    for location in percentage_df.columns:
        plt.plot(percentage_df.index, percentage_df[location], label=location, linewidth=0.8)

    plt.ylabel('Percentage of Vehicles (%)')
    plt.xlabel('Time (minutes)')
    plt.title('Percentage of Vehicles at Each Location Over Time')
    plt.legend(title='Location')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

#temporary metric function
def Car_trips_distribution(counter):
    distribution_trips = {}
    for day, Counter in counter.items():
        total = sum(counter[day].values())
        distribution_trips[day]= {k: round((v/total)*100) for k,v in Counter.items()}
    
    #individual days
    key_trip = []
    value_trip = []
    for counter_dict in distribution_trips.values():
        if 0 in counter_dict.keys():
            del counter_dict[0]
        counter_sorted = sorted(counter_dict.items()) 
        x,y = zip(*counter_sorted)
        key_trip.append(x)
        value_trip.append(y)

    #mean
    travel_keys_mean = {}
    counts_mean = {}

    for day_dict in distribution_trips.values():
        for k, v in day_dict.items():
            travel_keys_mean[k] = travel_keys_mean.get(k, 0) + v
            counts_mean[k] = counts_mean.get(k, 0) + 1

    means = {k: round(travel_keys_mean[k] / counts_mean[k]) for k in travel_keys_mean}
    means_sorted = dict(sorted(means.items()))
    if 0 in means_sorted.keys():
        del means_sorted[0]
    
    plt.figure(figsize=(10, 5))
    
    for x,y in zip(key_trip,value_trip):
        plt.scatter(x,y, color='grey')
    plt.scatter(means_sorted.keys(), means_sorted.values(), color='red')
    plt.xlabel('Amount of travels per day')
    plt.ylabel('Percentage (%)')
    plt.title('Mean of amount of travels per day')
    plt.xticks(list(means_sorted.keys()))
    plt.tight_layout()
    plt.grid(True)
    plt.show()
# Export individual profiles
"""
for i in range (len(Profile)):
    np.save('p0%d.npy' % (i), Profile[i])
"""

# Export Profiles
def export_stacked_data_to_csv(
    locational_profiles,
    reference_array=None,
    filename='individual_location_profiles'
):

    df = pd.DataFrame(locational_profiles)

    if reference_array is not None:
        df['Reference_Total'] = reference_array

    path_to_write = os.path.join(
        BASE_PATH,
        "results",
        f'output_file_{os.path.split(filename)[-1].replace(".", "_")}.csv',
    )

    df.to_csv(path_to_write, index=False)

def export_series(stoch_profiles_series, j=None, fname=None, ofname=None):
    series_frame = pd.DataFrame(stoch_profiles_series)
    path_to_write = None
    if ofname is not None:
        path_to_write = ofname
    else:
        if j is not None:
            path_to_write = os.path.join(
                BASE_PATH, "results", "output_file_%d.csv" % (j)
            )
        if fname is not None:
            path_to_write = os.path.join(
                BASE_PATH,
                "results",
                f'output_file_{os.path.split(fname)[-1].replace(".", "_")}.csv',
            )

    if path_to_write is not None:
        print(f"Writing RAMP results to {path_to_write}")
        series_frame.to_csv(path_to_write)
    else:
        print("No path to a file was provided to write the results")


def old_post_process(Profiles_list, fname, ofname):
    # Post-processes the results and generates plots
    Profiles_avg, Profiles_list_kW, Profiles_series = Profile_formatting(Profiles_list)
    Profile_series_plot(Profiles_series)  # by default, profiles are plotted as a series

    export_series(Profiles_series, None, fname, ofname)

    if (
        len(Profiles_list) > 1
    ):  # if more than one daily profile is generated, also cloud plots are shown
        Profile_cloud_plot(Profiles_list, Profiles_avg)


valid_units = ("kW", "W", "MW", "GW", "TW")


class Plot:
    """
    The Plot class will provide useful functionalities for analyzing and visualizing the results of one or multiple ramp simulations.

    The Plot class will store ramp simulation into a pd.DataFrame with timeseries index, representign the timeline of the simulation and the columns representing the simulated cases.
    A Plot class can be initialized using a pd.DataFrame, or from a csv, or xlsx file.

    Parameters
    ----------
    DataFrame : pd.DataFrame
        the Plot object data storing the simulation cases
    freq : pd.offsets
        the frequency of the data based on the DataFrame index
    index : Index
        Index to use for resulting frame timeseries.
    columns : Index or list-like
        Column labels to use for resulting frame when representing the simulation cases
    """

    @classmethod
    def from_file(self, file, sheet_name=0, sep=",", index=None):
        """initializing a Plot object from a file results

        Parameters
        ----------
        file : str
            path to the file of the results
        sheet_name : int,str, optional
            sheet_name of the result in case an excel file is passed, by default 0
        sep : str, optional
            separator in case a csv file is passed, by default ","
        index: pd.DatetimeIndex, optional
            if df index is not pd.DatetimeIndex, an DatetimeIndex object can be passed to change the index

        Returns
        -------
        Plot
            A Plot object
        """

        if file.endswith(".csv"):
            df = pd.read_csv(
                file, sheet_name=sheet_name, index_col=0, header=0, sep=sep
            )

        elif file.endswith(".xlsx"):
            df = pd.read_excel(file, sheet_name=sheet_name, index_col=0, header=0)

        else:
            raise ValueError(
                "unkwnon format specified for the file. Only .csv or .xlsx formats are allowed."
            )

        return Plot(df, index)

    def __init__(self, df, index=None):
        """initializes a Plot object using a pd.DataFrame

        Parameters
        ----------
        df : pd.DataFrame
            a pd.DataFrame with pd.DatetimeIndex

        index: pd.DatetimeIndex, optional
            if df index is not pd.DatetimeIndex, an DatetimeIndex object can be passed to change the index
        """
        if index is not None:
            df = df.copy()
            df.index = index

        self.DataFrame = df

    @property
    def freq(self):
        """return the frequency of the pd.DatetimeIndex"""
        return self.df.index.freq

    @property
    def columns(self):
        """returns a list of columns (cases) of the Plot dataframe

        Returns
        -------
        list
            list of cases
        """
        return self.df.columns.tolist()

    @columns.setter
    def columns(self, var):
        self.df.columns = var

    @property
    def index(self):
        return self.df.index

    def resample(self, freq, rule, conversion=1, inplace=False):
        """returns a resampled version of the data

        Parameters
        ----------
        freq : str
            pd.DataFrame.resample frequency, for example: "1h" for hourly resampling, "1w" for weekly data. Refer to https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
        rule : str
            resampling rule. acceptable values are 'sum', 'mean', 'nearest', ...
        conversion : int, optional
            if resampling needs a conversion, can be done through this argument. The value of the data will be divided by 'conversion', by default 1
        inplace : bool, optional
            if True, implements the changes inplace otherwise, returns the resampled data as a new object, by default False

        Returns
        -------
        Plot, None
            Plot object if inplace=False otherwise returns None
        """
        df = self.df.copy()

        df = df / conversion
        df = getattr(df.resample(freq), rule)()

        if inplace:
            self.df = df

        else:
            return Plot(df)

    def line(self, columns=None, engine="matplotlib", **kwargs):
        """creating a like plot

        Parameters
        ----------
        columns : str,list, optional
            columns (cases of the data to plot), by default None that takes all the columns
        engine : str, optional
            engine of the plot, by default "matplotlib"
        **kwargs : optional
            matplotlib or plotly **kwargs

        Returns
        -------
        a matplotlib or plotly graph

        """
        engine = self._check_engine(engine)

        if columns is None:
            df = self.df
        else:
            df = self.df[columns]

        if engine == "plotly":
            fig = px.line(df)
            fig.update_layout(**kwargs)

            return fig

        elif engine == "matplotlib":
            ax = df.plot(kind="line", **kwargs)

            return ax

    def shadow(
        self,
        main_column=None,
        columns="all",
        average=True,
        engine="matplotlib",
        **kwargs,
    ):
        """creating a shadow plot

        Parameters
        ----------
        main_column : str, optional
            the main column in the data to consider with darker color, by default None
        columns : list, optional
            columns to consider as the shadow plots, by default "all" to take all the columns
        average : bool, optional
            if True, will take the average profile as the dark line, by default True
        engine : str, optional
            engine of the plot, by default "matplotlib"
        **kwargs : optional
            matplotlib or plotly **kwargs

        Returns
        -------
        a matplotlib or plotly graph
        """
        engine = self._check_engine(engine)

        if main_column is None and average == False:
            raise ValueError(
                "one of columns should be passed as the main_column when the average = False"
            )

        elif main_column is not None and average == True:
            raise ValueError("main_column cannot be given when average = True")

        elif main_column is not None and average == False:
            df_main = (self.df.copy()[main_column]).to_frame(main_column)

        else:
            df_main = (self.mean()).df["Mean"].to_frame("Average")

        if columns.lower() == "all":
            columns = self.columns

        df_other = self.df.copy()[columns]

        if isinstance(df_other, pd.Series):
            df_other = df_other.to_frame(columns)

        if engine == "matplotlib":
            fig = plt.figure(**kwargs)
            ax = fig.add_subplot(1, 1, 1)

            ax.plot(
                df_main.index, df_main.values, color="black", label=df_main.columns[0]
            )

            ax.plot(df_other.index, df_other.values, alpha=0.3, color="black")

            ax.legend()

            return fig, ax

        elif engine == "plotly":
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df_main.index,
                    y=df_main.values.ravel(),
                    mode="lines",
                    name=df_main.columns[0],
                    line=dict(color="rgb(0,0,0)"),
                )
            )

            for col, vals in df_other.items():
                fig.add_trace(
                    go.Scatter(
                        x=vals.index,
                        y=vals.values.ravel(),
                        mode="lines",
                        showlegend=False,
                        line=dict(color="rgba(0,0,0,0.15)"),
                    )
                )

            fig.update_layout(**kwargs)

            return fig

    def area(self, columns=None, engine="matplotlib", **kwargs):
        """an area plot

        Parameters
        ----------
        columns : str,list, optional
            columns (cases of the data to plot), by default None that takes all the columns
        engine : str, optional
            engine of the plot, by default "matplotlib"
        **kwargs : optional
            matplotlib or plotly **kwargs

        Returns
        -------
        a matplotlib or plotly graph
        """
        engine = self._check_engine(engine)

        if columns is None:
            df = self.df
        else:
            df = self.df[columns]

        if engine == "matplotlib":
            return df.plot(kind="area", **kwargs)

        elif engine == "plotly":
            fig = px.area(df)
            fig.update_layout(**kwargs)

            return fig

    def load_duration_curve(self, column, engine="matplotlib", **kwargs):
        """plots the load duration curve

        Parameters
        ----------
        column : str
            the column to draw the load duration curve
        engine : str, optional
            engine of the plot, by default "matplotlib"
        **kwargs : optional
            matplotlib or plotly **kwargs

        Returns
        -------
        a matplotlib or plotly graph
        """
        engine = self._check_engine(engine)

        df = self.df[[column]]

        df = df.sort_values(by=column, ascending=False)
        df.index = [i for i in range(1, len(df.index) + 1)]

        if engine == "plotly":
            fig = px.line(df)
            fig.update_layout(**kwargs)

            return fig

        elif engine == "matplotlib":
            ax = df.plot(kind="line", **kwargs)

            return ax

    def error(self, base_column, validated_data):
        """returns the error

        Parameters
        ----------
        base_column : str
            simulation column
        validated_data : str
            validation column

        Returns
        -------
        pd.DataFrame
            error in each time slice
        """

        er = (
            (self.df[base_column] - self.df[validated_data])
            / self.df[validated_data].values
            * 100
        )
        er = er.fillna(0)

        return er

    @property
    def peak(self):
        """a dict with all peak hours for each column of the pd.DataFrame

        Returns
        -------
        dict
            keys are the columns of the data and values are the pd.Series representing the value and the time of the peak hours
        """

        output = {}

        for col, vals in self.df.items():
            max = vals.loc[vals == vals.max()]

            output[col] = max

        return output

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return self.DataFrame.head(10).to_string() + "\n ......"

    @property
    def DataFrame(self):
        """returns the data of the Plot object"""
        return self.df

    @DataFrame.setter
    def DataFrame(self, var):
        self._validate_df(var, check_index=False)

        self.df = var

    def add_column(self, var):
        """adds new column to the data

        Parameters
        ----------
        var : pd.DataFrame
            a pd.DataFrame with similar index to the main dataset
        """
        if isinstance(var, Plot):
            var = var.DataFrame

        self._validate_df(var)

        self.df[var.columns] = var.values

    def __getitem__(self, key):
        if isinstance(key, str):
            key = [key]

        return Plot(self.DataFrame[key])

    def loc(self, index=slice(None), columns=slice(None)):
        """loc method to filter the data

        Parameters
        ----------
        index : str,list,tuple, optional
            pd.DataFrame.loc index filtering input, by default slice(None)
        columns : str,list,tuple, optional
            pd.DataFrame.loc columns filtering input, by default slice(None)

        Returns
        -------
        Plot
            a Plot object using the index and columns filters
        """

        return Plot(self.DataFrame.loc[index, columns])

    def iloc(self, index=slice(None), columns=slice(None)):
        """iloc method to filter the data based on position index

        Parameters
        ----------
        index : int,list,tuple, optional
            pd.DataFrame.iloc index filtering input, by default slice(None)
        columns : int,list,tuple, optional
            pd.DataFrame.iloc columns filtering input, by default slice(None)

        Returns
        -------
        Plot
            a Plot object using the index and columns filters
        """

        return Plot(self.DataFrame.iloc[index, columns])

    def head(self, var):
        """returns the top var numbers of data

        Parameters
        ----------
        var : int
            numbers of rows of the data to show

        Returns
        -------
        Plot
            a Plot object with the numbers of rows specified
        """
        return Plot(self.DataFrame.head(var))

    def plot(self, **kwargs):
        """returns a pd.DataFrame.plot object

        Returns
        -------
        matplotlib.axes._axes.Axes
        """
        return self.DataFrame.plot(**kwargs)

    def _validate_df(self, other, check_index=True):
        if not isinstance(other, pd.DataFrame):
            raise ValueError("only pd.DataFrame object is allowed")

        if not (isinstance, other.index, pd.DatetimeIndex):
            raise ValueError("a valid dataframe shoud has only a pd.DatatimeIndex")
        if check_index:
            if not self.index.equals(other.index):
                raise ValueError(
                    "the new column should have identical index with the existing DataFrame"
                )

    def to_excel(self, path):
        """saves the data into excel

        Parameters
        ----------
        path : str
            path to save the file
        """

        with pd.ExcelWriter(path) as file:
            self.DataFrame.to_excel(file)

    def to_csv(self, path, sep=","):
        """saves the data into csv

        Parameters
        ----------
        path : str
            path to save the file
        sep : str,optional
            csv separator
        """
        self.DataFrame.to_csv(path, sep=sep)

    def mean(self):
        """returns the mean of the columns

        Returns
        -------
        Plot
            average of columns for each timestep
        """
        return Plot(self.DataFrame.mean(1).to_frame("Mean"))

    def sum(self):
        """returns the sum of the columns

        Returns
        -------
        Plot
            sum of columns for each timestep
        """
        return Plot(self.DataFrame.sum(1).to_frame("Sum"))

    def copy(self):
        """returns a copy of the existing object"""
        return Plot(self.df.copy())

    def _check_engine(self, engine):
        if engine.lower() == "matplotlib":
            return "matplotlib"

        elif engine.lower() == "plotly":
            return "plotly"

        raise ValueError(
            f"{engine} is not a valid plot engine. Only 'Plotly' and 'matplotlib are valid.'"
        )
