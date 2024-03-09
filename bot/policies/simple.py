from policies.policy import Policy

class SimplePolicy(Policy):
    def __init__(self, quantity=10):
        self.quantity = quantity

    def act(self, state, info):
        return self.quantity