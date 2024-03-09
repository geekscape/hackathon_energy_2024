import argparse
import os
import random
import pandas as pd
from policies import policy_classes
from environment import BatteryEnv
from datetime import datetime
import numpy as np
import tqdm
import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)['policy']

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def run_trial(battery_environment, policy, start_step, episode_length):
    state, info = battery_environment.reset(start_step=start_step, episode_length=episode_length)
    profits, socs, market_prices, actions = [], [], [], []

    while True:
        action = policy.act(state, info)
        state, info = battery_environment.step((action))

        if state is None:
            break

        profits.append(info['total_profit'])
        socs.append(info['battery_soc'])
        market_prices.append(state['Market_Price'])
        actions.append(action)

    return profits, socs, market_prices, actions

def parse_parameters(params_list):
    params = {}
    for item in params_list:
        key, value = item.split('=')
        params[key] = eval(value)
    return params

def main():
    parser = argparse.ArgumentParser(description='Evaluate a single energy market strategy.')
    parser.add_argument('--trials', type=int, default=100, help='Number of trials to run')
    parser.add_argument('--seed', type=int, default=42, help='Seed for randomness')
    parser.add_argument('--data', type=str, default='bot/train.csv', help='Path to the market data csv file')
    parser.add_argument('--class_name', type=str, help='Policy class name. If not provided, the config.json policy will be used.')
    parser.add_argument('--output_file', type=str, help='File to save all the submission outputs to.', default=None)
    parser.add_argument('--param', action='append', help='Policy parameters as key=value pairs', default=[])
    
    args = parser.parse_args()

    if args.class_name:
        policy_config = {'class_name': args.class_name, 'parameters': parse_parameters(args.param)}
    else:
        policy_config = load_config('bot/config.json')

    policy_class = policy_classes[policy_config['class_name']]
    policy = policy_class(**policy_config.get('parameters', {}))
    battery_environment = BatteryEnv(data=args.data)

    print(f'Running {args.trials} trials with policy {policy_config["class_name"]} and parameters {policy_config.get("parameters", {})}')

    if args.output_file:
        output_file = args.output_file
    else:
        results_dir = 'bot/results'
        os.makedirs(results_dir, exist_ok=True)
        output_file = os.path.join(results_dir, f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{policy_config["class_name"]}.json')

    set_seed(args.seed)

    total_profits = []
    all_trials = []
    start_steps = [0]
    episode_lengths = [len(battery_environment.market_data)]


    for trial in tqdm.tqdm(range(args.trials - 1)):
        set_seed(args.seed + trial)

        start_step = random.randint(0, len(battery_environment.market_data) - 1)
        episode_length = random.randint(1, len(battery_environment.market_data) - start_step)
        episode_lengths.append(episode_length)
        start_steps.append(start_step)
    
    for start_step, episode_length in zip(start_steps, episode_lengths):
        profits, socs, market_prices, actions = run_trial(battery_environment, policy, start_step, episode_length)
        total_profits.extend(profits)

        all_trials.append({
            'actions': actions,
            'profits': profits,
            'socs': socs,
            'market_prices': market_prices,
            'start_step': start_step,
            'episode_length': episode_length
        })

    avg_profit = float(np.mean(total_profits))
    std_profit = float(np.std(total_profits))

    outcome = {
        'class_name': policy_config['class_name'],
        'parameters': policy_config.get('parameters', {}),
        'mean_profit': avg_profit,
        'std_profit': std_profit,
        'num_runs': args.trials,
        'score': avg_profit,
        'trials': all_trials,
        'main_trial_idx': 0    
    }

    print(f'Average profit ($): {avg_profit:.2f} ± {std_profit:.2f}')

    with open(output_file, 'w') as file:
        json.dump(outcome, file, indent=2)

if __name__ == '__main__':
    main()