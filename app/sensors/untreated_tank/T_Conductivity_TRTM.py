from app.model.sensor import Sensor

def main():
    sensor = Sensor("T_Conductivity_TRTM")
    sensor.connect()

if __name__ == "__main__":
    main()