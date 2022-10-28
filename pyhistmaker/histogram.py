import numpy as np
from dataclasses import dataclass
import matplotlib.pyplot as plt
from typing import List


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

    def __repr__(self):
        return f"Histogram(name={self.name}, N={np.sum(self.counts)})"

    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()
        
        ax.stairs(self.counts, self.edges, **kwargs)
        ax.set_xlabel(self.name)

        return ax


@dataclass
class HistogramCollectionBase:
    histograms: List[Histogram]

    def _plot_placement(self, n):
        a = int(np.sqrt(n))
        b = n - a**2
        if b != 0:
            c = a + 1
        else:
            c = a
        sizes = (c, a)
        return sizes

    def plot(self, axs=None, sizes=None, figsize=None, **kwargs):
        n = len(self.histograms[0])
        if axs is None:
            if sizes is None:
                sizes = self._plot_placement(n)

            fig, axs = plt.subplots(*sizes, figsize=figsize)

        try:
            axs = axs.flatten()
        except AttributeError:
            axs = [axs]

        for row in self.histograms:
            for hist, ax in zip(row, axs):
                hist.plot(ax, **kwargs)

        return axs
    

@dataclass
class HistogramCollection(HistogramCollectionBase):

    def __getitem__(self, item):
        assert type(item) is str
        var_hists = []

        for hists in self.histograms:
            for hist in hists:
                if hist.name == item:
                    var_hists.append(hist)
        
        if len(var_hists) == 0:
            raise ValueError

        return HistogramCollectionBase([[var] for var in var_hists])
