import argparse
import json
from environment import BatteryEnv
from policies import policy_classes
from plotting import plot_results

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_parameters(params_list):
    params = {}
    for item in params_list:
        key, value = item.split('=')
        params[key] = eval(value)
    return params

def run_simulation(env, policy, num_steps):
    state, info = env.reset()
    profits = []
    market_prices = []
    battery_soc = []

    for _ in range(num_steps):
        market_price = state['Market_Price']
        quantity = policy.act(state, info)
        state, info = env.step(quantity)

        if state is None:
            break

        profits.append(info['total_profit'])
        market_prices.append(market_price)
        battery_soc.append(info['battery_soc'])

    return profits, market_prices, battery_soc

def main():
    parser = argparse.ArgumentParser(description='Battery Bidding Simulation')
    parser.add_argument('--config', type=str, default='bot/config.json',
                        help='Path to the configuration file (default: config.json)')
    parser.add_argument('--num_steps', type=int, default=100,
                        help='Number of simulation steps (default: 100)')
    parser.add_argument('--class_name', type=str, help='Policy class name. If provided, overrides the config file.')
    parser.add_argument('--param', action='append', help='Policy parameters as key=value pairs', default=[])
    parser.add_argument('--capacity', type=float, help='Battery capacity (kWh). If provided, overrides the config file.')
    parser.add_argument('--initial_charge', type=float, help='Initial battery charge (kWh). If provided, overrides the config file.')
    args = parser.parse_args()

    # Load the configuration file
    config = load_config(args.config)

    # Override the policy configuration if provided
    if args.class_name:
        policy_config = {'class_name': args.class_name, 'parameters': parse_parameters(args.param)}
    else:
        policy_config = config['policy']

    policy_class = policy_classes[policy_config['class_name']]
    policy = policy_class(**policy_config.get('parameters', {}))

    # Create the battery environment with optional overrides
    env_config = config.get('env', {})
    capacity = args.capacity if args.capacity is not None else env_config.get('capacity', 100)
    initial_charge = args.initial_charge if args.initial_charge is not None else env_config.get('initial_charge', 50)
    battery_env = BatteryEnv(capacity=capacity, initial_charge=initial_charge, data=env_config.get('data', 'bot/train.csv'))

    # Run the simulation
    profits, market_prices, battery_soc = run_simulation(battery_env, policy, args.num_steps)

    print("Simulation completed.")

    # Plot the results
    plot_results(profits, market_prices, battery_soc)

if __name__ == "__main__":
    main()