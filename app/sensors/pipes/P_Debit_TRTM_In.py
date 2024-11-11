from app.model.sensor import Sensor

def main():
    sensor = Sensor("P_Debit_TRTM_In")
    sensor.connect()

if __name__ == "__main__":
    main()
