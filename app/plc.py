from app.model.plc import PLC

def main():
    plc = PLC(name="plc_usr", password="plc_passwd")
    plc.connect()

if __name__ == "__main__":
    main()