from app.model.sensor import Sensor

def main():
    sensor = Sensor("T_Dissolved_Oxygen_TRTM")
    sensor.connect()

if __name__ == "__main__":
    main()
