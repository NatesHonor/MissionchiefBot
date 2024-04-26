import time
import json
import os

from data.mapping import vehicle_map
from transport_prisoners import transport_all_criminals, transport_remaining_criminals
from scripts.logon import login
from scripts.transport_patients import transport_all_ems_patients
from scripts.vehicle_data import gather_vehicle_data
from scripts.mission_data import gather_mission_data
from scripts.findtotalnumberofmissions import total_number_of_missions
from scripts.dispatch.dispatcher import dispatch_vehicles

vehicle_dispatch_mapping = vehicle_map

print("Logging in...")
driver = login()
print("Login Successful!")

if os.path.exists('data/vehicle_data.json'):
    print("Since vehicle_data.json exists we will just use the existing vehicle data!")
    time.sleep(5)

if not os.path.exists('data/vehicle_data.json'):
    print("Gathering vehicle data...")
    gather_vehicle_data(driver)

if os.path.exists('data/missions_data.json'):
    print("Cleaning missions_data.json...")
    os.remove('data/missions_data.json')

with open('data/vehicle_data.json', 'r') as f:
    vehicle_data = json.load(f)


missions_completed = 0

while True:
    print("Gathering total number of missions...")
    mission_numbers = total_number_of_missions(driver)

    print("Gathering mission data...")
    missions_data = gather_mission_data(driver, mission_numbers)

    with open('data/missions_data.json', 'w') as f:
        json.dump(missions_data, f)

    print("Now we will transport criminals and patients")
    transport_all_ems_patients(driver, 'data/vehicle_data.json')
    transport_all_criminals(driver, 'data/vehicle_data.json')
    transport_remaining_criminals(driver, 'data/vehicle_data.json')

    for m_number, mission_info in missions_data.items():
        try:
            mission_requirements = mission_info['vehicles']
            max_patients = mission_info.get('patients', 0)
            crashed_cars = mission_info.get('crashed_cars', 0)
            prisoners = mission_info.get('prisoners', 0)
            personnel = mission_info.get('personnel')
            print(f"Dispatching vehicles for mission {m_number} with requirements: {mission_requirements}")
            dispatch_vehicles(driver, m_number,
                              'data/vehicle_data.json', mission_requirements, max_patients,
                              vehicle_dispatch_mapping, crashed_cars, 'data/missions_data.json', prisoners)
            missions_completed += 1
        except KeyError as e:
            print(f"Error processing mission {m_number}: {e}")

    print("Completed all basic mission dispatches!")

    print("Now we will transport any requests for Ambulances!")
    transport_all_ems_patients(driver, 'data/vehicle_data.json')
    print("Completed all EMS transports!")
    transport_all_criminals(driver, 'data/vehicle_data.json')
    transport_remaining_criminals(driver, 'data/vehicle_data.json')
    print("Completed all Prisoner transports!")

    print("Assuming the code dispatched all vehicles correctly, it won't go through old missions again!")

    print("Sleeping for 5 minutes...")
    time.sleep(300)
