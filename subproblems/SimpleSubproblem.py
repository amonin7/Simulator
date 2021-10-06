class SimpleSubProblem:

    def __init__(self, depth, weight, cost):
        self.depth = depth
        self.weight = weight
        self.cost = cost

    def __str__(self) -> str:
        return str(
            {
                "level": self.depth,
                "profit": self.weight,
                "bound": self.cost,
                "weight": self.depth
            }
        )

    def __repr__(self) -> str:
        return str(
            {
                "level": self.depth,
                "profit": self.weight,
                "bound": self.cost,
                "weight": self.depth
            }
        )
