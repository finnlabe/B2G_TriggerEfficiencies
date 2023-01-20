import numpy as np
import uproot
from scipy.stats import beta
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
import hist
import boost_histogram as bh
plt.style.use(hep.style.CMS)

def binom_int(num, den, confint=0.68):
    quant = (1 - confint)/ 2.
    low = beta.ppf(quant, num, den - num + 1)
    high = beta.ppf(1 - quant, num + 1, den - num)
    return (np.nan_to_num(low), np.where(np.isnan(high), 1, high))

def style_label_automatically(label):

    # this method will use the implemented variable names and automatically return some proper latex x-axis
    # everything that is not understood will be just passed through unchanged

    object = ""
    variable = ""
    index = ""

    # known variables
    if "pt" in label: variable = "p_{T}"
    elif "eta" in label: variable = "\eta"
    elif "mSD" in label: variable = "m_{SD}"
    elif "nPV" in label: variable = "N(PV)"

    if "leading" in label: index = "_{0}"

    if "AK4" in label: object = "\mathrm{jet}^{AK4}"
    if "AK8" in label: object = "\mathrm{jet}^{AK8}"

    if not (object == "" and variable == "" and index == ""):
        returnstring = "$" + variable
        if object:
            returnstring += "(" + object + index + ")"
        return returnstring + "$"
    else: return label



def plotEfficiency(hist_before, hist_after, label=None, ax=None):

    np.seterr(invalid='ignore')
    
    # first, transforming to "hist" class for potential rebinning...
    hist_hist_before = hist_before.to_hist()
    hist_hist_after = hist_after.to_hist()

    # then transforming to nunmpy for plotting
    hist_data_before, hist_bins = hist_hist_before.to_numpy()
    hist_data_after, hist_bins = hist_hist_after.to_numpy()

    # calculating efficiency
    efficiency = np.nan_to_num(hist_data_after/hist_data_before)

    # getting error band
    band_low, band_high = binom_int(hist_data_after, hist_data_before)
    error_low = efficiency - band_low
    error_high = band_high - efficiency

    # removing large errors in empty bins
    error_low[error_low == 1] = 0
    error_high[error_high == 1] = 0

    # stacking errors
    error = np.concatenate((error_low.reshape(error_low.shape[0], 1), error_high.reshape(error_high.shape[0], 1)), axis=1)
    
    hep.histplot(efficiency, hist_bins, yerr=error.T, label=label, ax=ax)


def plotDistribution(hist, label=None, ax=None):

    # first, transforming to "hist" class for potential rebinning...
    hist_hist = hist.to_hist()

    # then transforming to nunmpy for plotting
    hist_data, hist_bins = hist_hist.to_numpy()

    # drawing
    hep.histplot(hist_data, hist_bins, label=label, ax=ax)