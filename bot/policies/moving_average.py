from collections import deque
import numpy as np
from policies.policy import Policy

class MovingAveragePolicy(Policy):
    def __init__(self, window_size=5):
        """
        Constructor for the MovingAveragePolicy.

        :param window_size: The number of past market prices to consider for the moving average (default: 5).
        """
        super().__init__()
        self.window_size = window_size
        self.price_history = deque(maxlen=window_size)

    def act(self, state, info):
        """
        Select an action based on the current state and additional info.

        :param state: A dictionary containing market data.
        :param info: A dictionary containing additional information relevant to decision-making.
        :return: A float representing quantity (kW) for the current step.
        """
        market_price = state['Market_Price']
        self.price_history.append(market_price)

        if len(self.price_history) == self.window_size:
            moving_average = np.mean(self.price_history)
            
            if market_price > moving_average:
                quantity = -info['max_discharge_rate']
            else:
                quantity = info['max_charge_rate']
        else:
            quantity = 0

        return quantity