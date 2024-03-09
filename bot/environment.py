"""
This file contains the core functionality for the battery simulation environment and its interaction with the NEM.
It provides a realistic representation of the NEM's operations and the battery's role within it.
Contestants will use this environment to develop and test their bidding strategies.

Units used in this file:
- Power: kilowatts (kW)
- Energy: kilowatt-hours (kWh)
- Time: minutes (min)
- Price: dollars per kilowatt-hour ($/kWh)
"""

import pandas as pd
import numpy as np
from collections import deque
from typing import Tuple

class Battery:
    """
    A simple model of a battery with charging and discharging capabilities.
    """
    def __init__(self, capacity: float, charge_rate: float, discharge_rate: float, 
                 initial_charge: float, efficiency: float = 0.9):
        """
        Initialize the battery with the given parameters.

        :param capacity: Maximum energy capacity of the battery in kWh.
        :param charge_rate: Maximum charging rate in kW.
        :param discharge_rate: Maximum discharging rate in kW.
        :param initial_charge: Initial state of charge of the battery in kWh.
        :param efficiency: Charging and discharging efficiency of the battery (default: 0.9).
        """
        self.capacity = capacity
        self.initial_charge = initial_charge
        self.charge_rate = charge_rate
        self.discharge_rate = discharge_rate
        self.efficiency = efficiency
        self.state_of_charge = min(self.initial_charge, self.capacity)

    def reset(self):
        """Reset the battery to its initial state of charge."""
        self.state_of_charge = min(self.initial_charge, self.capacity)

    def charge(self, power: float, duration: float) -> float:
        """
        Charge the battery with a specified power over a duration.

        :param power: Power in kW to charge the battery.
        :param duration: Duration in minutes for which the battery is charged.
        :return: Energy added to the battery in kWh.
        """
        power = min(power, self.charge_rate)
        energy_add_order = power * (duration / 60) * self.efficiency  # Convert power (kW) to energy (kWh)
        energy_added = min(energy_add_order, self.capacity - self.state_of_charge)
        self.state_of_charge = min(self.state_of_charge + energy_add_order, self.capacity)
        return energy_added

    def discharge(self, power: float, duration: float) -> float:
        """
        Discharge the battery with a specified power over a duration.

        :param power: Power in kW to discharge the battery.
        :param duration: Duration in minutes for which the battery is discharged.
        :return: Energy removed from the battery in kWh.
        """
        power = min(power, self.discharge_rate)
        energy_remove_order = power * (duration / 60) / self.efficiency  # Convert power (kW) to energy (kWh)
        energy_removed = min(energy_remove_order, self.state_of_charge)
        self.state_of_charge = max(self.state_of_charge - energy_remove_order, 0)
        return energy_removed

    def get_state_of_charge(self) -> float:
        """
        Return the current state of charge of the battery.

        :return: State of charge in kWh.
        """
        return self.state_of_charge


class BatteryEnv:
    """
    Environment for simulating battery operation in the National Electricity Market (NEM) context.
    """
    def __init__(self, capacity: float = 100, charge_rate: float = 50, discharge_rate: float = 50,
                 initial_charge: float = 50, data: str = 'train.csv'):
        """
        Initialize the battery environment with the given parameters.

        :param capacity: Maximum energy capacity of the battery in kWh (default: 100).
        :param charge_rate: Maximum charging rate in kW (default: 50).
        :param discharge_rate: Maximum discharging rate in kW (default: 50).
        :param initial_charge: Initial state of charge of the battery in kWh (default: 50).
        :param data: Path to the CSV file containing market data (default: 'train.csv').
        """
        self.battery = Battery(capacity, charge_rate, discharge_rate, initial_charge)
        self.market_data = pd.read_csv(data)
        self.dispatch_prices = deque(maxlen=6)  # Store the last 6 dispatch prices for spot price calculation
        self.total_profit = 0
        self.current_step = 0
        self.episode_length = len(self.market_data)

    def reset(self, start_step: int = 0, episode_length: int = None, initial_soc: float = None) -> Tuple[pd.Series, dict]:
        """
        Reset the environment with specified starting step, episode length, and initial state of charge.

        :param start_step: Starting step for the episode (default: 0).
        :param episode_length: Length of the episode in steps (default: None, which means using the full data).
        :param initial_soc: Initial state of charge of the battery in kWh (default: None, which means using the default initial charge).
        :return: A tuple containing the initial market data and information dictionary.
        """
        self.current_step = start_step
        self.total_profit = 0
        self.episode_length = episode_length if episode_length else len(self.market_data) - start_step
        initial_soc = initial_soc if initial_soc is not None else self.battery.initial_charge
        self.battery.state_of_charge = min(initial_soc, self.battery.capacity)
        self.dispatch_prices.clear()
        return self.market_data.iloc[self.current_step], self.get_info()

    def step(self, quantity: float) -> Tuple[pd.Series, dict]:
        """
        Perform a single step in the environment based on the given action.

        :param action: A tuple containing the bid price ($/kWh) and quantity (kW) for the current step.
        :return: A tuple containing the next market data and information dictionary, or (None, None) if the episode is done.
        """
        if self.current_step >= len(self.market_data) - 1:
            return None, None
        dispatch_price = self.market_data.iloc[self.current_step]['Market_Price']
        self.dispatch_prices.append(dispatch_price)
        spot_price = np.mean(self.dispatch_prices)
        profit_delta = self.process_action(quantity, spot_price)
        self.current_step += 1
        market_data = self.market_data.iloc[self.current_step]
        return market_data, self.get_info(profit_delta)

    def process_action(self, quantity: float, spot_price: float) -> float:
        """
        Process the action taken by the agent and return the profit delta.

        :param action: A tuple containing the bid price ($/kWh) and quantity (kW) for the current step.
        :param spot_price: The current spot price in $/kWh.
        :return: The profit delta in dollars.
        """
        duration = 5  # Duration of each dispatch interval in minutes
        if quantity > 0:
            energy_added = self.battery.charge(quantity, duration)
            return -energy_added * (duration / 60) * spot_price  # Convert energy (kWh) to cost ($)
        elif quantity < 0:
            energy_removed = self.battery.discharge(-quantity, duration)
            return energy_removed * (duration / 60) * spot_price  # Convert energy (kWh) to revenue ($)
        return 0

    def get_info(self, profit_delta: float = 0) -> dict:
        """
        Return a dictionary containing relevant information for the agent.

        :param profit_delta: The change in profit from the last action (default: 0).
        :return: A dictionary containing information about the current state of the environment.
        """
        self.total_profit += profit_delta
        remaining_steps = len(self.market_data) - self.current_step - 1
        return {
            'total_profit': self.total_profit,
            'profit_delta': profit_delta,
            'battery_soc': self.battery.get_state_of_charge(),
            'max_charge_rate': self.battery.charge_rate,
            'max_discharge_rate': self.battery.discharge_rate,
            'remaining_steps': remaining_steps
        }
    
if __name__ == "__main__":
    # Example usage of the BatteryEnv class
    battery_env = BatteryEnv(capacity=100, charge_rate=50, discharge_rate=50, initial_charge=50, data='train.csv')

    # Reset the environment
    state, info = battery_env.reset()
    print(f"Initial state: {state}")
    print(f"Initial info: {info}")

    # Run a simple simulation for 10 steps
    for _ in range(10):
        # Get the current market price
        market_price = state['Market_Price']

        # Define a simple bidding strategy (bid at 90% of the market price with a quantity of 10 kW)
        quantity = 10

        # Take a step in the environment
        state, info = battery_env.step(quantity)

        if state is None:
            break

        # Print the results
        print(f"Step: {battery_env.current_step}")
        print(f"Market Price: {market_price:.2f} $/kWh")
        print(f"Quantity: {quantity:.2f} kW")
        print(f"Profit Delta: {info['profit_delta']:.2f} $")
        print(f"Total Profit: {info['total_profit']:.2f} $")
        print(f"Battery SOC: {info['battery_soc']:.2f} kWh")
        print("---")

    print("Simulation completed.")