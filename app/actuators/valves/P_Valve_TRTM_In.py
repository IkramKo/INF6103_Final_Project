from app.model.actuator import Actuator

def main():
    actuator = Actuator("P_Valve_TRTM_In")
    actuator.connect()

if __name__ == "__main__":
    main()