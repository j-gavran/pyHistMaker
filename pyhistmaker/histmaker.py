import numpy as np
from pyhistmaker.histogram import Histogram


class HistMaker:
    def __init__(self, data, n_bins="auto", bin_range=None, density=False, var_names=None):
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
        density: bool, optional
            If True return prob. density.
        var_names: list of str, optional
            Names of histogrammed distributions.

        References
        ----------
        [1] - https://numpy.org/doc/stable/reference/generated/numpy.histogram_bin_edges.html

        """
        self.data = data 
        self.n_bins = n_bins
        self.bin_range = bin_range
        self.density = density
        self.var_names = var_names

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
            combined_sample = np.concatenate(self.data)
        else:
            if len(self.data.shape) == 1:
                self.data = self.data[:, None]
            
            self.data = [self.data]
            combined_sample = self.data[0]

        return combined_sample

    def make(self):
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

        hists_lst = []
        for data in self.data:
            for feature in range(n_features):
                feature_data = data[:, feature]
                bin_edge_data = combined_sample[:, feature]

                hist_bin_range = bin_range[feature] if bin_range else None

                bin_edges = np.histogram_bin_edges(bin_edge_data, bins=self.n_bins, range=hist_bin_range)
                hist = np.histogram(feature_data, bins=bin_edges, range=hist_bin_range, density=self.density)

                h_obj = Histogram(self.var_names[feature] if self.var_names is not None else f"hist_{feature}", hist[1], hist[0])
                hists_lst.append(h_obj)
        
        return hists_lst

    def __call__(self, *args, **kwargs):
        return self.make(*args, **kwargs)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # test case 1
    data = np.random.randn(500, 5)
    h = HistMaker(data)
    hists = h()
    print(hists)
    for h_ in hists:
        h_.plot(lw=2, fill=False)
        plt.show()

    # test case 2
    data1 = np.random.randn(500, 5)
    data2 = np.random.randn(500, 5)
    data = [data1, data2]
    h = HistMaker(data, n_bins=20)
    hists = h()
    print(hists)