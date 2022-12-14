import numpy as np
from .histogram import Histogram, HistogramCollection


class HistMaker:
    def __init__(self, data, n_bins="auto", bin_range=None, density=False, var_names=None, binning_index=None):
        """Class for making histograms from raw data using numpy.

        Parameters
        ----------
        data : list or array
            Data to be histogrammed. If list then [data0, ..., dataN]. Arrays can be 1d (one histogram) or 2d
            (multiple histograms). If a list of data is given then same features will be combined for bin edge calculation.
        n_bins : int, str or array, optional
            Number of bins, see [1]. By default "auto".
        bin_range : list or list of lists, optional
            If list [lower, upper] use for all data else specify [[lower0, upper0], ..., [lowerN, upperN]] for each histogram.
        density : bool, optional
            If True return prob. density.
        var_names : list of str, optional
            Names of histogrammed distributions.
        binning_index : list
            Index of self.data list to use for bin edges.

        References
        ----------
        [1] - https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html

        """
        self.data = data
        self.n_bins = n_bins
        self.bin_range = bin_range
        self.density = density
        self.var_names = var_names
        self.binning_index = binning_index

    def _validate_data_shapes(self):
        """If a list of data is given, make sure that all arrays have the same number of features.

        Raises
        ------
        ValueError
            If shapes do not match.
        """
        shape_0 = self.data[0].shape[1]

        for d in self.data[1:]:
            shape_1 = d.shape[1]
            if shape_0 != shape_1:
                raise ValueError
            else:
                shape_0 = shape_1

        return True

    def _combine_data(self):
        """Combine multiple data in a list input for correct bin edges.

        Note
        ----
        If self.data is an array then redefine it as a list of len 1 that holds the specified array. Also make the 1d
        array a column of size (N, 1).

        Returns
        -------
        np.array
            Concatenated arrays.
        """
        if isinstance(self.data, list):
            self._validate_data_shapes()
            if self.binning_index:
                cat_data = [self.data[i] for i in self.binning_index]
            else:
                cat_data = self.data
            combined_sample = np.concatenate(cat_data)
        else:
            if len(self.data.shape) == 1:
                self.data = self.data[:, None]

            self.data = [self.data]
            combined_sample = self.data[0]

        return combined_sample

    def make(self, **kwargs):
        """Make histograms.

        Returns
        -------
        list
            List of Histogram objects.
        """
        combined_sample = self._combine_data()

        n_features = self.data[0].shape[1]

        if self.bin_range is None:
            bin_range = None
        else:
            if not any(isinstance(el, list) for el in bin_range):
                bin_range = [bin_range] * n_features

        hists_lst = [[] for _ in range(len(self.data))]

        for i, data in enumerate(self.data):
            for feature in range(n_features):
                feature_data = data[:, feature]
                bin_edge_data = combined_sample[:, feature]

                hist_bin_range = bin_range[feature] if bin_range else None

                bin_edges = np.histogram_bin_edges(bin_edge_data, bins=self.n_bins, range=hist_bin_range)
                hist = np.histogram(feature_data, bins=bin_edges, range=hist_bin_range, density=self.density, **kwargs)

                h_obj = Histogram(
                    self.var_names[feature] if self.var_names is not None else f"hist_{feature}", hist[1], hist[0]
                )
                hists_lst[i].append(h_obj)

        if len(hists_lst[0]) > 1:
            return HistogramCollection(hists_lst)
        else:
            return hists_lst[0][0]

    def __call__(self, *args, **kwargs):
        return self.make(*args, **kwargs)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # test case 1 - multiple histograms
    data = np.random.randn(500, 5)
    h = HistMaker(data)
    hists = h()
    print(hists)
    hists.plot()
    plt.show()

    # test case 2 - list of multiple histograms
    sig = np.random.randn(500, 5)
    bkg = np.random.randn(500, 5)
    data = [sig, bkg]
    h = HistMaker(data, n_bins=20)
    hists = h()
    print(hists)
    hists.plot()
    plt.show()

    # test case 2.1 - get histogram by name
    hists_0 = hists["hist_0"]
    print(hists_0)
    ax = hists_0.plot()
    ax.legend(["sig", "bkg"])
    plt.show()

    # test case 3 - single histogram
    data = np.random.randn(500)
    h = HistMaker(data)
    hists = h()
    print(hists)
    hists.plot()
    plt.show()
