import pandas as pd
import warnings
from math import radians, sin, cos, sqrt, atan2

warnings.filterwarnings('ignore')


drivers_df = pd.read_excel('Dataset.xlsx', sheet_name='Driver')
riders_df = pd.read_excel('Dataset.xlsx', sheet_name='Rider')
shifters_df = pd.read_excel('Dataset.xlsx', sheet_name='Shifter')
drivers_df['departure_time'] = pd.to_datetime(drivers_df['departure_time'])
riders_df['departure_time'] = pd.to_datetime(riders_df['departure_time'])
shifters_df['departure_time'] = pd.to_datetime(shifters_df['departure_time'])


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0

    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    distance = R * c
    return distance


def has_matching_departure_time(riders_df):
    matching_indices = []
    for rider_idx, rider_row in riders_df.iterrows():
        rider_time = rider_row['departure_time']
        if ((abs(drivers_df['departure_time'] - rider_time) <= pd.Timedelta(minutes=30)).any() or
            (abs(shifters_df['departure_time'] - rider_time) <= pd.Timedelta(minutes=30)).any()):
            matching_indices.append(rider_idx)
    return riders_df.loc[matching_indices]

def has_matching_departure_time_shifter(shifters_df):
    shifter_indices = []
    for shifter_idx, shifter_row in shifters_df.iterrows():
         shifter_time = shifter_row['departure_time']
         if ((abs(drivers_df['departure_time'] - shifter_time) <= pd.Timedelta(minutes=30)).any() or
            (abs(riders_df['departure_time'] - shifter_time) <= pd.Timedelta(minutes=30)).any() or
            (abs(shifters_df['departure_time'] - shifter_time) <= pd.Timedelta(minutes=30)).any()):
             shifter_indices.append(shifter_idx)
    return shifters_df.loc[shifter_indices]

def has_matching_departure_time_driver(drivers_df):
    driver_indices = []  
    for driver_idx, driver_row in drivers_df.iterrows():  
         driver_time = driver_row['departure_time']
         if ((abs(riders_df['departure_time'] - driver_time) <= pd.Timedelta(minutes=30)).any() or
            (abs(shifters_df['departure_time'] - driver_time) <= pd.Timedelta(minutes=30)).any()):
             driver_indices.append(driver_idx)
    return drivers_df.loc[driver_indices]

def filter_data_and_save():

# Filter riders based on matching departure times
    valid_riders_df = has_matching_departure_time(riders_df)
# Filter shifter based on matching departure times
    valid_shifters_df = has_matching_departure_time_shifter(shifters_df)
# Filter driver based on matching departure times
    valid_drivers_df = has_matching_departure_time_driver(drivers_df)

    def is_within_1km(lat1, lon1, dataframe):
      for idx, row in dataframe.iterrows():
        lat2 = row['Start_lat'] 
        lon2 = row['Start_lon']
        
        if haversine(lat1, lon1, lat2, lon2) <= 1.0:
          return True
    
      return False

    # Filter the driver entries
    valid_driver_indices = []
    for driver_idx, driver_row in valid_drivers_df.iterrows():
        if is_within_1km(driver_row['Start_lat'], driver_row['Start_lon'], valid_riders_df) or is_within_1km(driver_row['Start_lat'], driver_row['Start_lon'], valid_shifters_df):
            valid_driver_indices.append(driver_idx)

    # Filter the rider entries
    valid_rider_indices = []
    for rider_idx, rider_row in valid_riders_df.iterrows():
        if is_within_1km(rider_row['Start_lat'], rider_row['Start_lon'], valid_shifters_df) or is_within_1km(rider_row['Start_lat'], rider_row['Start_lon'], valid_drivers_df):
            valid_rider_indices.append(rider_idx)

    # Filter the shifter entries
    valid_shifter_indices = []
    for shifter_idx, shifter_row in valid_shifters_df.iterrows():
        if is_within_1km(shifter_row['Start_lat'], shifter_row['Start_lon'], valid_drivers_df) or is_within_1km(shifter_row['Start_lat'], shifter_row['Start_lon'], valid_riders_df) or is_within_1km(shifter_row['Start_lat'], shifter_row['Start_lon'], valid_shifters_df):
            valid_shifter_indices.append(shifter_idx)

    # Create DataFrames with the valid indices
    newvalid_drivers_df = valid_drivers_df.loc[valid_driver_indices]
    newvalid_riders_df = valid_riders_df.loc[valid_rider_indices]
    newvalid_shifters_df = valid_shifters_df.loc[valid_shifter_indices]

    # Save the filtered DataFrames to a new Excel file
    with pd.ExcelWriter('UpdatedDataset.xlsx') as writer:
        newvalid_drivers_df.to_excel(writer, sheet_name='Driver', index=False)
        newvalid_riders_df.to_excel(writer, sheet_name='Rider', index=False)
        newvalid_shifters_df.to_excel(writer, sheet_name='Shifter', index=False)

filter_data_and_save()
