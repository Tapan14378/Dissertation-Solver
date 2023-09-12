import pandas as pd
import random
import math
from datetime import datetime, timedelta

# # Load the postcode data from the CSV file
postcode_data = pd.read_csv('Reading postcode.csv')
# Load the new postcode data within radius
postcode_datanew = pd.read_csv('radius.csv')

def generate_dataset(num_entries):
    writer = pd.ExcelWriter('synthetic_datasetnew20.xlsx', engine='xlsxwriter')
    
    num_near_same_time = int(num_entries * 0.50)
    num_different_time = num_entries - num_near_same_time
    
    near_same_times = []
    for i in range(num_near_same_time):
        base_departure_time = datetime(2023, 5, 8, random.randint(12, 12), random.randint(0, 59), 0)
        offset = timedelta(minutes=random.randint(-30, 30))
        near_same_times.append(base_departure_time + offset)
    
    random.shuffle(near_same_times)
    
    pet_values_near_same = 'YES'
    smoker_values_near_same = 'YES'
    disable_values_near_same = 'NO'
    
    for tab_name in ['Driver', 'Rider', 'Shifter']:
        df = pd.DataFrame(columns=['id', 'type', 'route_start', 'Start_lat', 'Start_lon', 'route_end', 'End_lat', 'End_lon', 'departure_time', 'seats', 'Pet', 'Smoker', 'Disable'])

        for i in range(num_near_same_time):
            departure_time = near_same_times[i]

            # Select a start and end index from the list of possible indices in the near postcode data
            start_index = random.randint(0, len(postcode_datanew) - 1)
            end_index = random.randint(0, len(postcode_datanew) - 1)

            seats = random.randint(2, 6) if tab_name in ['Driver', 'Shifter'] else None

            row = {
                'id': f'{tab_name[0]}{i}',
                'type': tab_name.lower(),
                'route_start': postcode_datanew['Postcode'][start_index],
                'Start_lat': postcode_datanew['Latitude'][start_index],
                'Start_lon': postcode_datanew['Longitude'][start_index],
                'route_end': postcode_datanew['Postcode'][end_index],
                'End_lat': postcode_datanew['Latitude'][end_index],
                'End_lon': postcode_datanew['Longitude'][end_index],
                'departure_time': departure_time.strftime('%Y-%m-%d %H:%M:%S'),
                'seats': seats,
                'Pet': pet_values_near_same,
                'Smoker': smoker_values_near_same,
                'Disable': disable_values_near_same
            }
            df = df.append(row, ignore_index=True)

        for i in range(num_different_time):
            departure_time = datetime(2023, 5, 8, random.randint(0, 23), random.randint(0, 59), 0)
            
            # Generate random indices for postcode data
            start_index = random.randint(0, len(postcode_data) - 1)
            end_index = random.randint(0, len(postcode_data) - 1)
            
            # Generate random number of seats (only for the Driver and Shifter tabs)
            seats = random.randint(2, 6) if tab_name in ['Driver', 'Shifter'] else None
            
            # Generate random values for Pet, Smoker, and Disable columns
            pet_values = ['YES', 'NO']
            smoker_values = ['YES', 'NO']
            disable_values = ['YES', 'NO']
            
            # Generate an entry for the current tab with random preferences
            row = {
                'id': f'{tab_name[0]}{i + num_near_same_time}',
                'type': tab_name.lower(),
                'route_start': postcode_data['Postcode'][start_index],
                'Start_lat': postcode_data['Latitude'][start_index],
                'Start_lon': postcode_data['Longitude'][start_index],
                'route_end': postcode_data['Postcode'][end_index],
                'End_lat': postcode_data['Latitude'][end_index],
                'End_lon': postcode_data['Longitude'][end_index],
                'departure_time': departure_time.strftime('%Y-%m-%d %H:%M:%S'),
                'seats': seats,
                'Pet': random.choice(pet_values + ['BOTH']) if tab_name == 'Rider' else random.choice(pet_values),
                'Smoker': random.choice(smoker_values + ['BOTH']) if tab_name == 'Rider' else random.choice(smoker_values),
                'Disable': random.choice(disable_values)
            }
            df = df.append(row, ignore_index=True)

        # Save the dataframe to the current tab in the Excel file
        df.to_excel(writer, sheet_name=tab_name, index=False)
    
    # Save and close the Excel writer object
    writer.save()

# Set the number of entries you want in the dataset
num_entries = 20

# Generate the dataset
generate_dataset(num_entries)
