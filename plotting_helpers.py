import numpy as np
from scipy.stats import beta
import matplotlib.pyplot as plt
import mplhep as hep
import boost_histogram as bh
plt.style.use(hep.style.CMS)

def binom_int(num, den, confint=0.68):
    quant = (1 - confint)/ 2.
    low = beta.ppf(quant, num, den - num + 1)
    high = beta.ppf(1 - quant, num + 1, den - num)
    return (np.nan_to_num(low), np.where(np.isnan(high), 1, high))


def getColor(lineIndex, mode="auto"):

    manual_colors = [
        "TODO"
    ]

    if mode == "manual": return manual_colors[lineIndex]
    else: return "C" + str(lineIndex)

def style_label_automatically(label, forPublic = True):

    # this method will use the implemented variable names and automatically return some proper latex x-axis
    # everything that is not understood will be just passed through unchanged

    # some names are hard-coded
    # these will be used if forPublic is true

    hard_coded_names = {
        "leading_AK8_pt" : "Leading offline AK8 jet $p_{T}$ [GeV]",
        "second_AK8_pt" : "Second offline AK8 jet $p_{T}$ [GeV]",
        "AK8_HT" : "Offline AK8 jet $H_{T}$ [GeV]",
        "nPV" : "Number of primary vertices",
        "leading_AK8_eta" : "Leading offline AK8 jet $\eta$",
        "leading_AK8_mSD" : "Soft drop mass of leading offline AK8 jet [GeV]",
        "mjj" : "Invariant mass of leading two offline AK8 jets [GeV]",
    }

    if forPublic and label in hard_coded_names: return hard_coded_names[label]

    object = ""
    variable = ""
    index = ""

    # known variables
    if "pt" in label: variable = "p_{T}"
    elif "eta" in label: variable = "\eta"
    elif "mSD" in label: variable = "m_{SD}"
    elif "nPV" in label: variable = "N(PV)"
    elif "HT" in label: variable = "H_{T}"

    if "leading" in label: index = "_{0}"

    if "AK4" in label: object = "\mathrm{jet}^{AK4}"
    if "AK8" in label: object = "\mathrm{jet}^{AK8}"

    if not (object == "" and variable == "" and index == ""):
        returnstring = "$" + variable
        if object:
            returnstring += "(" + object + index + ")"
        return returnstring + "$"
    else: return label



def plotEfficiency(hist_before, hist_after, label=None, ax=None, color=None):

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

    #hep.histplot(efficiency, hist_bins, yerr=error.T, label=label, ax=ax, color=color)
    hep.histplot(efficiency, hist_bins, yerr=error.T, label=label, ax=ax, histtype="errorbar", xerr=True, marker=".", markersize=9, elinewidth=1, color=color)


def plotDistribution(hist, label=None, ax=None):

    # first, transforming to "hist" class for potential rebinning...
    hist_hist = hist.to_hist()

    # then transforming to nunmpy for plotting
    hist_data, hist_bins = hist_hist.to_numpy()

    # drawing
    hep.histplot(hist_data, hist_bins, label=label, ax=ax)


def drawLabel(label = ""):

    # the com option is broken, so we'll need to use rlabel manually

    if "22" in label and "full" in label:
        rlabel = r"$34.3$ $\mathrm{fb}^{-1}$, 2022 ($13.6$ $\mathrm{TeV}$)"    
    else: rlabel = None

    hep.cms.label("Preliminary", data=True, rlabel=rlabel)

def styleNamesAutomatically(name):

    known_names = {
        "postHCAL_22" : "post-HCAL update",
        "preHCAL_22" : "pre-HCAL update",
        "total" : "OR of these triggers",
        "AK8PFJet500" : "Jet with $p_{T}$ > 500 GeV",
        "AK8PFJet420_MassSD30" : "Jet with $p_{T}$ > 420 GeV\nand mass > 30 GeV",
        "AK8DiPFJet270_270_MassSD30" : "Two jets with $p_{T}$ > 270 GeV\nand mass > 30 GeV",
        "PFHT1050" : "$H_T$ > 1050 GeV",
    }

    if name in known_names: return known_names[name]
    else: return name
