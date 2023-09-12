import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import math
import time

start_time_total = time.time()

drivers_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Driver')
riders_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Rider')
shifters_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Shifter')

drivers_df['departure_time'] = pd.to_datetime(drivers_df['departure_time'])
riders_df['departure_time'] = pd.to_datetime(riders_df['departure_time'])
shifters_df['departure_time'] = pd.to_datetime(shifters_df['departure_time'])


# Function to calculate the distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    # Convert coordinates from degrees to radians
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of the Earth in kilometers
    return c * r


def solve(tolerance):
    # Create the model
    model = gp.Model('ridesharing')
    # Variables
    n_drivers = len(drivers_df)
    n_riders = len(riders_df)
    n_shifters = len(shifters_df)

    # Define decision variables
    x = [[model.addVar(vtype=GRB.BINARY, name='x[%i][%i]' % (i, j)) for j in range(n_riders)] for i in range(n_drivers)] #Driver and Rider assignment
    y = [[model.addVar(vtype=GRB.BINARY, name='y[%i][%i]' % (i, j)) for j in range(n_riders)] for i in #Shifter and Rider assignment
         range(n_shifters)]
    z = [model.addVar(vtype=GRB.BINARY, name='z[%i]' % i) for i in range(n_shifters)] #Check if the Shifter is active/assigned
    x_rider = [[model.addVar(vtype=GRB.BINARY, name='x_rider[%i][%i]' % (i, j)) for j in range(n_shifters)] for i in
               range(n_drivers)] #Driver and Shifter ( acting as rider) assignment.
    w = [[model.addVar(vtype=GRB.BINARY, name='w[%i][%i]' % (i, j)) for j in range(n_shifters)] for i in
         range(n_shifters)]  # shifter (acting driver) i has been assigned to shifter (acting rider) j

    # Constraints
    # Each rider is taken by at most one driver or shifter acting as a driver
    for j in range(n_riders):
        model.addConstr(gp.quicksum(x[i][j] for i in range(n_drivers)) +
                        gp.quicksum(y[i][j] for i in range(n_shifters)) <= 1)

    # Each shifter, when acting as a rider, is taken by at most one driver
    for j in range(n_shifters):
        model.addConstr(gp.quicksum(x_rider[i][j] for i in range(n_drivers)) <= 1)

    # Each driver takes riders up to their capacity
    for i in range(n_drivers):
        model.addConstr(gp.quicksum(x[i][j] for j in range(n_riders)) +
                        gp.quicksum(x_rider[i][j] for j in range(n_shifters)) <= drivers_df.loc[i, 'seats'])

    # Each shifter, when acting as a driver, takes riders up to their capacity
    for i in range(n_shifters):
        model.addConstr(gp.quicksum(y[i][j] for j in range(n_riders)) <= shifters_df.loc[i, 'seats'] * z[i])

    # A shifter cannot act as both a driver and a rider at the same time
    for i in range(n_shifters):
        model.addConstr(z[i] + gp.quicksum(x_rider[k][i] for k in range(n_drivers)) <= 1)

    # Constraints for departure times
    for i in range(n_drivers):
        for j in range(n_riders):
            if abs(drivers_df.loc[i, 'departure_time'] - riders_df.loc[j, 'departure_time']) > pd.Timedelta(minutes=30):
                model.addConstr(x[i][j] == 0)

        # Define distances for drivers
        dist_drivers_start = [[haversine(drivers_df.loc[i, 'Start_lon'], drivers_df.loc[i, 'Start_lat'],
                                         riders_df.loc[j, 'Start_lon'], riders_df.loc[j, 'Start_lat'])
                               for j in range(n_riders)] for i in range(n_drivers)]
        dist_drivers_end = [[haversine(drivers_df.loc[i, 'End_lon'], drivers_df.loc[i, 'End_lat'],
                                       riders_df.loc[j, 'End_lon'], riders_df.loc[j, 'End_lat'])
                             for j in range(n_riders)] for i in range(n_drivers)]

    # Constraints for distances
    for i in range(n_drivers):
        for j in range(n_riders):
            model.addConstr(
                x[i][j] <= (1 if dist_drivers_start[i][j] <= tolerance and dist_drivers_end[i][j] <= tolerance else 0))

    # Each driver takes riders considering their constraints for pets, smokers, and disabled
    for i in range(n_drivers):
        for j in range(n_riders):
            if (drivers_df.loc[i, 'Pet'] == 'NO' and riders_df.loc[j, 'Pet'] == 'YES') or \
                    (drivers_df.loc[i, 'Smoker'] == 'NO' and riders_df.loc[j, 'Smoker'] == 'YES') or \
                    (drivers_df.loc[i, 'Disable'] == 'NO' and riders_df.loc[j, 'Disable'] == 'YES') or \
                    (drivers_df.loc[i, 'Pet'] == 'YES' and riders_df.loc[j, 'Pet'] == 'NO') or \
                    (drivers_df.loc[i, 'Smoker'] == 'YES' and riders_df.loc[j, 'Smoker'] == 'NO'):
                model.addConstr(x[i][j] == 0)
            elif (drivers_df.loc[i, 'Pet'] == 'YES' and (
                    riders_df.loc[j, 'Pet'] == 'YES' or riders_df.loc[j, 'Pet'] == 'BOTH')) and \
                    (drivers_df.loc[i, 'Pet'] == 'NO' and riders_df.loc[j, 'Pet'] == 'BOTH') and \
                    (drivers_df.loc[i, 'Smoker'] == 'YES' and (
                            riders_df.loc[j, 'Smoker'] == 'YES' or riders_df.loc[j, 'Smoker'] == 'BOTH')) and \
                    (drivers_df.loc[i, 'Smoker'] == 'NO' and riders_df.loc[j, 'Smoker'] == 'BOTH') and \
                    (drivers_df.loc[i, 'Disable'] == 'YES' and riders_df.loc[j, 'Disable'] == 'YES'):
                model.addConstr(x[i][j] == 1)

    for i in range(n_shifters):
        for j in range(n_riders):
            if abs(shifters_df.loc[i, 'departure_time'] - riders_df.loc[j, 'departure_time']) > pd.Timedelta(
                    minutes=30):
                model.addConstr(y[i][j] == 0)

        dist_shifters_start = [[haversine(shifters_df.loc[i, 'Start_lon'], shifters_df.loc[i, 'Start_lat'],
                                          riders_df.loc[j, 'Start_lon'], riders_df.loc[j, 'Start_lat'])
                                for j in range(n_riders)] for i in range(n_shifters)]
        dist_shifters_end = [[haversine(shifters_df.loc[i, 'End_lon'], shifters_df.loc[i, 'End_lat'],
                                        riders_df.loc[j, 'End_lon'], riders_df.loc[j, 'End_lat'])
                              for j in range(n_riders)] for i in range(n_shifters)]

    for i in range(n_shifters):
        for j in range(n_riders):
            model.addConstr(y[i][j] <= (
                1 if dist_shifters_start[i][j] <= tolerance and dist_shifters_end[i][j] <= tolerance else 0))

    # Each shifter, when acting as a driver, takes riders considering their constraints for pets, smokers, and disabled
    for i in range(n_shifters):
        for j in range(n_riders):
            if (shifters_df.loc[i, 'Pet'] == 'NO' and riders_df.loc[j, 'Pet'] == 'YES') or \
                    (shifters_df.loc[i, 'Smoker'] == 'NO' and riders_df.loc[j, 'Smoker'] == 'YES') or \
                    (shifters_df.loc[i, 'Disable'] == 'NO' and riders_df.loc[j, 'Disable'] == 'YES') or \
                    (shifters_df.loc[i, 'Pet'] == 'YES' and riders_df.loc[j, 'Pet'] == 'NO') or \
                    (shifters_df.loc[i, 'Smoker'] == 'YES' and riders_df.loc[j, 'Smoker'] == 'NO'):
                model.addConstr(y[i][j] == 0)
            elif (shifters_df.loc[i, 'Pet'] == 'YES' and (
                    riders_df.loc[j, 'Pet'] == 'YES' or riders_df.loc[j, 'Pet'] == 'BOTH')) and \
                    (shifters_df.loc[i, 'Pet'] == 'NO' and riders_df.loc[j, 'Pet'] == 'BOTH') and \
                    (shifters_df.loc[i, 'Smoker'] == 'YES' and (
                            riders_df.loc[j, 'Smoker'] == 'YES' or riders_df.loc[j, 'Smoker'] == 'BOTH')) and \
                    (shifters_df.loc[i, 'Smoker'] == 'NO' and riders_df.loc[j, 'Smoker'] == 'BOTH') and \
                    (shifters_df.loc[i, 'Disable'] == 'YES' and riders_df.loc[j, 'Disable'] == 'YES'):
                model.addConstr(y[i][j] == 1)

    # Shifter as rider constraints for driver -driver takes shifter (as a rider)
    for i in range(n_drivers):
        for j in range(n_shifters):
            # If a driver and a shifter have matching preferences
            if (drivers_df.loc[i, 'Pet'] == shifters_df.loc[j, 'Pet'] and
                    drivers_df.loc[i, 'Smoker'] == shifters_df.loc[j, 'Smoker'] and
                    drivers_df.loc[i, 'Disable'] == shifters_df.loc[j, 'Disable'] and
                    abs(drivers_df.loc[i, 'departure_time'] - shifters_df.loc[j, 'departure_time']) <= pd.Timedelta(
                        minutes=30) and
                    haversine(drivers_df.loc[i, 'Start_lon'], drivers_df.loc[i, 'Start_lat'],
                              shifters_df.loc[j, 'Start_lon'], shifters_df.loc[j, 'Start_lat']) <= tolerance and
                    haversine(drivers_df.loc[i, 'End_lon'], drivers_df.loc[i, 'End_lat'],
                              shifters_df.loc[j, 'End_lon'], shifters_df.loc[j, 'End_lat']) <= tolerance):
                # The shifter can be a rider of this driver
                model.addConstr(x_rider[i][j] == 1)
            else:
                # The shifter cannot be a rider of this driver
                model.addConstr(x_rider[i][j] == 0)

    # Each shifter-driver can take shifter-riders up to their capacity
    for i in range(n_shifters):
        model.addConstr(sum(w[i][j] for j in range(n_shifters) if i != j) <= shifters_df.loc[i, 'seats'])

    # Each shifter-rider is taken by at most one shifter-driver
    for j in range(n_shifters):
        model.addConstr(sum(w[i][j] for i in range(n_shifters) if i != j) <= 1)

    # A shifter cannot act as both a driver and a rider at the same time
    for i in range(n_shifters):
        model.addConstr(sum(w[i][j] for j in range(n_shifters) if i != j) +
                        sum(w[j][i] for j in range(n_shifters) if i != j) <= 1)

    # Shifter-driver takes shifter-rider if preferences match and within distance and time constraints
    for i in range(n_shifters):
        for j in range(n_shifters):
            if i != j:
                # If a shifter-driver and a shifter-rider have matching preferences
                if (shifters_df.loc[i, 'Pet'] == shifters_df.loc[j, 'Pet'] and
                        shifters_df.loc[i, 'Smoker'] == shifters_df.loc[j, 'Smoker'] and
                        shifters_df.loc[i, 'Disable'] == shifters_df.loc[j, 'Disable'] and
                        abs(shifters_df.loc[i, 'departure_time'] - shifters_df.loc[
                            j, 'departure_time']) <= pd.Timedelta(minutes=30) and
                        haversine(shifters_df.loc[i, 'Start_lon'], shifters_df.loc[i, 'Start_lat'],
                                  shifters_df.loc[j, 'Start_lon'], shifters_df.loc[j, 'Start_lat']) <= tolerance and
                        haversine(shifters_df.loc[i, 'End_lon'], shifters_df.loc[i, 'End_lat'],
                                  shifters_df.loc[j, 'End_lon'], shifters_df.loc[j, 'End_lat']) <= tolerance):
                    pass  # Do nothing as the assignment is feasible
                else:
                    # The shifter-rider cannot be taken by this shifter-driver
                    model.addConstr(w[i][j] == 0)

        #objective
    model.setObjective(gp.quicksum(x[i][j] for i in range(n_drivers) for j in range(n_riders)) +
                       gp.quicksum(y[i][j] for i in range(n_shifters) for j in range(n_riders)) +
                       gp.quicksum(w[i][j] for i in range(n_shifters) for j in range(n_shifters)) +
                       gp.quicksum(x_rider[i][j] for i in range(n_drivers) for j in range(n_shifters)), GRB.MAXIMIZE)

    start_time = time.time()

    # Solve the problem
    model.optimize()

    end_time = time.time()

    # Print the solution
    if model.status == GRB.OPTIMAL or model.status == GRB.FEASIBLE:
        print(
            "Optimal solution found!" if model.status == GRB.OPTIMAL else "Feasible solution found (not necessarily optimal).")
        print("Objective value:", model.objVal)
        match_count = 0
        # Print driver-rider assignments
        for i in range(n_drivers):
            for j in range(n_riders):
                if x[i][j].x > 0:
                    match_count += 1
                    print('Driver', drivers_df.loc[i, 'id'], 'takes rider', riders_df.loc[j, 'id'])
        # Print shifter-driver-rider assignments
        for i in range(n_shifters):
            for j in range(n_riders):
                if y[i][j].x > 0:
                    match_count += 1
                    print('Shifter', shifters_df.loc[i, 'id'], 'acts as a driver and takes rider',
                          riders_df.loc[j, 'id'])
        # Print driver-shifter-rider assignments
        for i in range(n_drivers):
            for j in range(n_shifters):
                if x_rider[i][j].x > 0:
                    match_count += 1
                    print('Driver', drivers_df.loc[i, 'id'], 'takes shifter', shifters_df.loc[j, 'id'],
                          'acting as a rider')
        # Print shifter-driver-shifter-rider assignments
        for i in range(n_shifters):
            for j in range(n_shifters):
                if i != j and w[i][j].x > 0:
                    match_count += 1
                    print('Shifter', shifters_df.loc[i, 'id'], 'acts as a driver and takes shifter',
                          shifters_df.loc[j, 'id'], 'who is acting as a rider')
    else:
        print('No solution found.')

    end_time_total = time.time()
    solver_time = round(end_time - start_time, 2)
    total_time = round(end_time_total - start_time_total, 2)
    print('Match count:', match_count)
    print('Solution time:', solver_time, 'seconds')
    print('Total execution time:', total_time, 'seconds')


solve(tolerance=1)