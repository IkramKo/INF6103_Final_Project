from app.model.actuator import Actuator

def main():
    actuator = Actuator("P_Valve_TRT_Out")
    actuator.connect()

if __name__ == "__main__":
    main()