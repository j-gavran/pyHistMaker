import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


class Histogram:
    def __init__(self, name, edges, counts):
        self.name = name
        self.edges = edges
        self.hist = self._counstruct_df(name, counts)

    @staticmethod
    def _counstruct_df(name, counts):
        df = pd.DataFrame([counts], columns=[f"bin{i}" for i in range(len(counts))])
        df.insert(0, "name", name)
        return df

    @property
    def counts(self):
        return self.hist.iloc[0].to_numpy()[1:].astype(int)

    def __eq__(self, other):
        return (self.counts == other.counts).all()

    def __sub__(self, other):
        return self.counts - other.counts

    def __add__(self, other):
        return self.counts + other.counts

    def __call__(self, *args, **kwargs):
        return self.hist

    def __repr__(self):
        return f"Histogram(name={self.name}, N={np.sum(self.counts)})"

    def plot(self, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots()

        ax.stairs(self.counts, self.edges, **kwargs)
        ax.set_xlabel(self.name)

        return ax


class HistogramCollectionBase:
    def __init__(self, histograms):
        self.histograms = histograms
        self.hist = self._construct_df(histograms)

    @staticmethod
    def _construct_df(histograms):
        hists = []
        for hist in histograms:
            df = pd.concat([h() for h in hist])
            df.reset_index(drop=True, inplace=True)
            hists.append(df)

        return hists

    def _plot_placement(self, n):
        a = int(np.sqrt(n))
        b = n - a ** 2
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

        if len(axs) == 1:
            return axs[0]
        else:
            return axs

    def __call__(self, *args, **kwargs):
        if len(self.hist) == 1:
            return self.hist[0]
        else:
            return self.hist


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

    def __repr__(self):
        repr_str = ""

        for i, h in enumerate(self.histograms):
            repr_str += f"{i}: {h.__repr__()} \n"

        return repr_str
