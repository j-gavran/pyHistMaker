import numpy as np
from pyhistmaker.histogram import Histogram



class HistMaker:
    def __init__(self, data, n_bins="auto", bin_range=None, density=False, var_names=None):
        """Class for making histograms from raw data using numpy.

        Parameters
        ----------
        data : list or array
            Data to be histogrammed. Array can be 1d (one histogram) or 2d (multiple histograms).
        n_bins : int, str or array
            Number of bins, see np.histogram docs for other options.
        bin_range : list or list of lists, optional
            If list [lower, upper] use for all data in array else specify [[lower0, upper0], ..., [lowerN, upperN]].
        density: bool, optional
            If True return prob. density.
        var_names: list of str, optional
            Names of distributions in histograms.
        """
        self.data = data 
        self.n_bins = n_bins
        self.bin_range = bin_range
        self.density = density
        self.var_names = var_names

    def _validate_data_shapes(self):
        shape_0 = self.data[0].shape[1]

        for d in self.data[1:]:
            shape_1 = d.shape[1]
            if shape_0 != shape_1:
                raise ValueError
            else:
                shape_0 = shape_1
        return

    def _combine_data(self):
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
        combined_sample = self._combine_data()

        n_features = self.data[0].shape[1]

        if self.bin_range is None:
            bin_range = None
        else:
            if not any(isinstance(el, list) for el in bin_range):
                bin_range = [bin_range] * n_features

        hists_lst = []
        for feature in range(n_features):
            hist_data = combined_sample[:, feature]
            hist_bin_range = bin_range[feature] if bin_range else None

            bin_edges = np.histogram_bin_edges(hist_data, bins=self.n_bins, range=hist_bin_range)
            hist = np.histogram(hist_data, bins=bin_edges, range=hist_bin_range, density=self.density)
            hists_lst.append(Histogram(self.var_names[feature] if self.var_names is not None else f"hist_{feature}", hist[1], hist[0]))
        
        return hists_lst

    def __call__(self, *args, **kwargs):
        return self.make(*args, **kwargs)


if __name__ == "__main__":
    data = np.random.rand(5, 5)
    
    h = HistMaker(data)

    hists = h()

    print(hists)