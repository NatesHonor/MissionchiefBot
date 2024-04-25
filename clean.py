import os


def main():
    print("Hey there! To clean up some project files first explain what you want to do!")
    print("Would you like to:")
    print("1. Register new vehicles?")
    print("2. Delete Current Mission Data?")
    print("3. Wipe all data and start from scratch?")

    choice = input("Enter the number of your choice: ")

    if choice == '1':
        print("You've chosen to register new vehicles.")
        if os.path.exists('vehicle_data.json'):
            os.remove('vehicle_data.json')
            print("Current vehicle data deleted.")
    elif choice == '2':
        if os.path.exists('missions_data.json'):
            os.remove('missions_data.json')
            print("Current mission data deleted.")
        else:
            print("Mission data file does not exist.")
    elif choice == '3':
        if os.path.exists('missions_data.json'):
            os.remove('missions_data.json')
        if os.path.exists('vehicle_data.json'):
            os.remove('vehicle_data.json')
        print("All data wiped. You can start from scratch now.")
    else:
        print("Invalid choice. Please run the script again and select a valid option.")


if __name__ == "__main__":
    main()
