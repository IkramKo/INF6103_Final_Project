from app.model.sensor import Sensor

def main():
    sensor = Sensor("T_Dissolved_Oxygen_TRT")
    sensor.connect()

if __name__ == "__main__":
    main()
