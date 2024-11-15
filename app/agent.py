import argparse
from app.meta.decorators.logging import log_with_attributes
from app.model.chaos_agent import ChaosAgent

def main():
    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--db_host', help='Database host', required=False)
    parser.add_argument('--mqtt_host', help='MQTT host', required=False)
    parser.add_argument('--name', help='Name of the Chaos Agent', required=False)
    args = parser.parse_args()

    print(f"DB_HOST: {args.db_host}") #access using args.name
    db_host=args.db_host if args.db_host else "localhost"

    try:
        chaos_agent = ChaosAgent(db_host=db_host)
        log_with_attributes(f"Chaos Agent has started", level="info")
        while True:
            chaos_agent.fill_untreated_tank_when_input_valve_active()
            chaos_agent.treat_water()
            chaos_agent.fill_treated_tank_when_untreated_output_valve_open()
            chaos_agent.empty_treated_tank()
    except KeyboardInterrupt:
        log_with_attributes("Chaos Agent stopped", level="error")

if __name__ == "__main__":
    main()

    