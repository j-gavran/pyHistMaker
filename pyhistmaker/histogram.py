import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt


@dataclass
class Histogram:
    name: str
    edges: np.array
    counts: np.array

    def __eq__(self, other):
        return (self.counts == other.counts).all()

    def __sub__(self, other):
        return self.counts - other.counts

    def __add__(self, other):
        return self.counts + other.counts

    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        
        ax.stairs(self.counts, self.edges, **kwargs)
        ax.set_xlabel(self.name)

        return ax