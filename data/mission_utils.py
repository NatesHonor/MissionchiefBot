def remove_mission(mission_id, mission_data):
    if mission_id in mission_data:
        del mission_data[mission_id]
        print(f"Deleting mission ID: {mission_id}")
