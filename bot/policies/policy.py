from abc import ABC, abstractmethod

class Policy(ABC):
    def __init__(self, **kwargs):
        """
        Constructor for the Policy class. It can take flexible parameters.
        Contestants are free to maintain internal state and use any auxiliary data or information
        within this class. Policies will be evaluated using market data from late April to early May 2024.
        """
        super().__init__()

    @abstractmethod
    def act(self, state, info):
        """
        Select an action based on the current state and additional info.

        State: A dictionary containing real-time market data. Example keys:
            - 'Market_Price' (float, $/kWh): Current price in the energy market.
            - 'Temperature' (float, °C): Current temperature.
            - 'Cloud_Cover' (float, %): Current cloud cover percentage.
            - 'Energy_Demand' (float, kW): Current energy demand.

        Info: A dictionary containing additional information relevant to the policy. Example keys:
            - 'total_profit' (float, $): Cumulative profit so far.
            - 'profit_delta' (float, $): Change in profit from the last action.
            - 'battery_soc' (float, kWh): Current state of charge of the battery.
            - 'remaining_steps' (int): Number of steps remaining in the simulation.
            - 'max_charge_rate' (float, kW): Maximum rate at which the battery can be charged.
            - 'max_discharge_rate' (float, kW): Maximum rate at which the battery can be discharged.

        Action: A tuple containing the bid price and quantity for the current step.
            - Bid Price (float, $/kWh): The price at which you are willing to buy or sell energy.
            - Quantity (float, kW): The amount of energy to buy (positive) or sell (negative).

        :param state: A dictionary containing market data.
        :param info: A dictionary containing additional information relevant to decision-making.
        :return: A float representing quantity (kW) to charge/discharge for the current step.
        """
        pass

# Contestant Instructions:
# - Implement your policy by extending the Policy class.
# - Use the 'act' method to make decisions based on the state and info dictionaries.
# - Your policy will be evaluated on market data from late April to early May 2024.