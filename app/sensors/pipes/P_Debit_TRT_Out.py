from app.model.sensor import Sensor

def main():
    sensor = Sensor("P_Debit_TRT_Out")
    sensor.connect()

if __name__ == "__main__":
    main()
