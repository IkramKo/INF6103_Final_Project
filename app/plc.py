import argparse
from app.model.plc import PLC

def main():

    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--db_host', help='Database host', required=False)
    parser.add_argument('--mqtt_host', help='MQTT host', required=False)
    parser.add_argument('--name', help='Name of the PLC', required=True)
    args = parser.parse_args()

    print(f"DB_HOST: {args.db_host}") #access using args.name
    print(f"MQTT_HOST: {args.mqtt_host}")
    print(f"NAME: {args.name}")

    db_host=args.db_host if args.db_host else "localhost"
    mqtt_host=args.mqtt_host if args.mqtt_host else "localhost"

    plc = PLC(name=args.name, password="plc_passwd", broker_address=mqtt_host, db_host=db_host)
    plc.connect()

if __name__ == "__main__":
    main()