import uproot
import pandas as pd
from .histogram import Histogram, HistogramCollection


class UprootReader:
    def __init__(self, file_path, **kwargs):
        """Wrapper for uproot.open.

        https://uproot.readthedocs.io/en/latest/uproot.reading.ReadOnlyDirectory.html

        Parameters
        ----------
        file_path : str
            Name of root file and directory.
        """
        self.file_path = file_path
        self.ReadOnlyDirectory = self._get_ReadOnlyDirectory(**kwargs)

    def _get_ReadOnlyDirectory(self, **kwargs):
        """https://uproot.readthedocs.io/en/latest/uproot.reading.open.html"""
        ReadOnlyDirectory = uproot.open(self.file_path, **kwargs)
        return ReadOnlyDirectory

    def classnames(self):
        return self.ReadOnlyDirectory.classnames()

    def hist_to_numpy(self, name):
        counts, edges = self.ReadOnlyDirectory[name].to_numpy()
        return counts, edges

    def to_histogram(self, name, rsplit=False):
        counts, edges = self.hist_to_numpy(name)

        if rsplit:
            name = name.rsplit('/', 1)[-1][:-2]

        h = Histogram(name, edges, counts)
        return h

    def to_histogram_collection(self):
        classnames = self.ReadOnlyDirectory.classnames()

        hist_collection = []
        for i, (k, v) in enumerate(classnames.items()):
            
            if v == "TDirectory":
                if i > 0:
                    hist_collection.append(hists)
                hists = []
            else:
                h = self.to_histogram(k, rsplit=True)
                hists.append(h)
        
        hist_collection.append(hists)
        return HistogramCollection(hist_collection)

    def close(self):
        self.ReadOnlyDirectory.close()


class UprootWriter:
    def __init__(self, file_path, update=False, **kwargs):
        """Wrapper for uproot.recreate and uproot.update.

        Note
        ----
        Use close method after done with writting.

        Parameters
        ----------
        file_path : str
            Name of root file and directory.
        update : bool, optional
            If .root file already exists, by default False.
        """
        self.file_path = file_path
        self.update = update
        self.WritableDirectory = self._get_WritableDirectory(**kwargs)
    
    def _get_WritableDirectory(self, **kwargs):
        """
        [1] - https://uproot.readthedocs.io/en/latest/basic.html#writing-objects-to-a-file
        [2] - https://uproot.readthedocs.io/en/latest/uproot.writing.writable.update.html

        """
        if self.update:
            WritableDirectory = uproot.update(self.file_path, **kwargs)
        else:
            WritableDirectory = uproot.recreate(self.file_path, **kwargs)
        
        return WritableDirectory

    def write_df(self, df, name):
        self.WritableDirectory[name] = df

    def write_array(self, arr, columns):
        df = pd.DataFrame(arr, columns=columns)
        self.write_df(df)

    def write_histogram(self, hist_obj, name):
        self.WritableDirectory[name] = (hist_obj.counts, hist_obj.edges)

    def write_histogram_collection(self, histograms, name=""):
        for hist_obj in histograms:
            self.write_histogram(hist_obj, name + hist_obj.name)

    def close(self):
        self.WritableDirectory.close()
