import time
import json
import os
import threading

from data.vehicle_mapping import vehicle_map
from data.personnel_mapping import personnel_map

from scripts.logon import login
from scripts.clean import mission_cleaner
from scripts.transport import transport_submit
from scripts.vehicle_data import gather_vehicle_data
from scripts.mission_data import gather_mission_data
from scripts.gather_missions import total_number_of_missions
from scripts.dispatch.dispatcher import dispatch_vehicles

vehicle_dispatch_mapping = vehicle_map
personnel_dispatch_mapping = personnel_map


def transport_loop():
    time.sleep(10)
    transport_driver = login()
    while True:
        print("Transporting prisoners and patients...")
        transport_submit(transport_driver)
        time.sleep(30)


transport_thread = threading.Thread(target=transport_loop)
transport_thread.start()

print("Logging in...")
driver = login()
print("Login Successful!")

if os.path.exists('data/vehicle_data.json'):
    print("Since vehicle_data.json exists we will just use the existing vehicle data!")

if not os.path.exists('data/vehicle_data.json'):
    print("Gathering vehicle data...")
    gather_vehicle_data(driver)

with open('data/vehicle_data.json', 'r') as f:
    vehicle_data = json.load(f)

while True:
    print("Populating vehicle dictionary...")
    with open('data/vehicle_data.json', 'r') as f:
        vehicle_pool = json.load(f)

    print("Gathering total number of missions...")
    mission_numbers = total_number_of_missions(driver)

    print("Gathering mission data...")
    missions_data = gather_mission_data(driver, mission_numbers)

    with open('data/missions_data.json', 'w') as f:
        json.dump(missions_data, f)

    for m_number, mission_info in missions_data.items():
        try:
            mission_requirements = mission_info['vehicles']
            max_patients = mission_info.get('patients', 0)
            crashed_cars = mission_info.get('crashed_cars', 0)
            prisoners = mission_info.get('prisoners', 0)
            print(f"Dispatching vehicles for mission {m_number}")
            dispatch_vehicles(driver, m_number, vehicle_pool, mission_requirements, max_patients,
                              vehicle_dispatch_mapping, crashed_cars, 'data/missions_data.json',
                              prisoners, personnel_dispatch_mapping)

        except KeyError as e:
            print(f"Error processing mission {m_number}: {e}")
    print("Completed all basic mission dispatches!")

    print("Now attempting to clean up missions")
    for m_number in mission_numbers:
        mission_cleaner(driver, m_number)
    print("Sleeping for 3s...")
    time.sleep(3)
