from app.model.actuator import Actuator

def main():
    name = "P_Valve_RTRTM"
    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--db_host', help='Database host', required=False) #required=True make it mandatory
    args = parser.parse_args()

    print(f"DB_HOST: {args.db_host}") #access using args.name

    actuator = Actuator(name, db_host=args.db_host if args.db_host else "localhost")
    actuator.connect()

if __name__ == "__main__":
    main()