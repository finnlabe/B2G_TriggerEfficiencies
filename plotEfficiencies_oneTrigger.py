import sys

import numpy as np
import uproot
from scipy.stats import beta
import matplotlib
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.ROOT)

# suppressing error from division of 0 by 0 (is handled in code)
np.seterr(invalid='ignore')

prefixes = ["", "mSD35__"]
variables = ["leading AK8 pt", "leading AK8 eta", "leading AK8 mSD", "AK8 HT"]
trigger = "AK8PFJet400_TrimMass30"

# needed for error bars on efficiencies
def binom_int(num, den, confint=0.68):
    quant = (1 - confint)/ 2.
    low = beta.ppf(quant, num, den - num + 1)
    high = beta.ppf(1 - quant, num + 1, den - num)
    return (np.nan_to_num(low), np.where(np.isnan(high), 1, high))

def plotHistogram(hist, label=None, ax=None):

    hist_data, hist_bins = hist.to_numpy()
    hep.histplot(hist_data, hist_bins, ax=ax, label=label)

def plotEfficiency(hist_before, hist_after, label=None, ax=None):
    
    hist_data_before, hist_bins = hist_before.to_numpy()
    hist_data_after, hist_bins = hist_after.to_numpy()

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

for prefix in prefixes:
    for variable in variables:

        fig, ax = plt.subplots()

        for fileo in sys.argv:

            file = str(fileo)

            if ".py" in file: continue
            with uproot.open(file) as f_in:

                plotEfficiency(f_in[prefix + variable.replace(" ", "_") + "__before"], f_in[prefix + variable.replace(" ", "_") + "__" + trigger], label=file.replace("output_","").replace(".root",""), ax=ax)

                plt.ylabel("efficiency")
                plt.xlabel(variable)
                plt.legend()

                fig.savefig(trigger + "__effi__" + prefix + variable.replace(" ", "_") + ".png", format="png")
