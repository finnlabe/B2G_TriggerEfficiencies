import argparse
import uproot
from plotting_helpers import *

# generic plotting function
# -i expects one or more root files
# -o defined which kind of plots are created, and sets any other option needed for these
#    options are: oneTrigger, oneFile
#    additional options are: mSD35, pure
# -t triggers defines which triggers are plotted (requires one or more)
# -v variables to be plotted (one or more)

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', required=True, nargs='+')
parser.add_argument('-o', '--options', required=True, nargs='+')
parser.add_argument('-t', '--triggers', required=True, nargs='+')
parser.add_argument('-v', '--variables', required=True, nargs='+')
parser.add_argument('--outputFolder', default="plots") # we have a default directory here!

args = parser.parse_args()

# getting potential mSD prefix from options
if "mSD35" in args.options: prefix = "mSD35__"
else: prefix = ""

if "pure" in args.options: postfix = "__pure"
else: postfix = ""

plotCount = 0
lineCount = 0

# defining a plot output folder

if "oneTrigger" in args.options:

    print("Creating efficiency plots with single trigger setting.")

    for trigger in args.triggers:

        print("Plotting trigger " + trigger)

        # onen plot per variavble
        for variable in args.variables:

            fig, ax = plt.subplots()

            for file in args.input:

                print("Plotting file " + file)

                with uproot.open(file) as f_in:

                    # autodetermine label from file name
                    label = file.replace("output_","").replace(".root","")
                    path_parts = len(label.split("/"))
                    if( path_parts > 1 ): label = label.split("/")[path_parts-1]

                    plotEfficiency(f_in[prefix + variable + "__before"], f_in[prefix + variable + "__" + trigger + postfix], label=styleNamesAutomatically(label), ax=ax, color=getColor(lineCount))
                    lineCount += 1

            plt.ylabel("Efficiency")
            plt.xlabel(style_label_automatically(variable), usetex=True)

            plt.legend(loc = "lower right")

            # add some text explaining the cuts
            text_in_plot = r"$\bf{" + trigger.replace("_", "\_") + "}$"
            text_in_plot += "\n$\mathrm{AK8}~p_{T} > 200~\mathrm{GeV}$"
            if "mSD35" in prefix: text_in_plot += "\n$\mathrm{AK8}~m_{SD} > 35~\mathrm{GeV}$"
            plt.text(ax.get_xlim()[1]*0.45, 0.2, text_in_plot, fontsize=18)

            plt.legend(loc = "lower right", title=styleNamesAutomatically(trigger), prop={'size': 16}, title_fontsize=20)
            
            drawLabel("yourlabelhere")
            fig.savefig(args.outputFolder + "/" + trigger + postfix + "__effi__" + prefix + variable + ".png", format="png")
            fig.savefig(args.outputFolder + "/" + trigger + postfix + "__effi__" + prefix + variable + ".pdf", format="pdf")
            plotCount += 1
            lineCount = 0


elif "oneFile" in args.options:

    print("Creating plots for a single file.")

    for file in args.input:

        print("Plotting file " + file)

        with uproot.open(file) as f_in:

            for variable in args.variables:

                fig, ax = plt.subplots()

                for trigger in args.triggers:
                    print("Plotting trigger " + trigger)
                    color = getColor(lineCount)
                    if trigger == "total": color = "black"
                    plotEfficiency(f_in[prefix + variable + "__before"], f_in[prefix + variable + "__" + trigger + postfix], label=styleNamesAutomatically(trigger), ax=ax, color=color)
                    lineCount += 1

                plt.ylabel("Efficiency")
                plt.xlabel(style_label_automatically(variable), usetex=True)

                if "eta" in variable: plt.legend(loc = "upper right")
                elif "nPV" in variable: plt.legend(loc = "upper left")
                else: plt.legend(loc = "lower right", prop={'size': 16})

                # add some text explaining the cuts
                text_in_plot = r"$\mathrm{AK8}~p_{T} > 200~\mathrm{GeV}$"
                if "mSD35" in prefix: text_in_plot += "\n$\mathrm{AK8}~m_{SD} > 35~\mathrm{GeV}$"
                plt.text(ax.get_xlim()[1]*0.45, 0.5, text_in_plot, fontsize=18)

                # autodetermine label from file name
                label = file.replace("output_","").replace(".root","")
                path_parts = len(label.split("/"))
                if( path_parts > 1 ): label = label.split("/")[path_parts-1]

                drawLabel(label)
                fig.savefig(args.outputFolder + "/" + label + postfix + "__effi__" + prefix + variable + ".png", format="png")
                fig.savefig(args.outputFolder + "/" + label + postfix + "__effi__" + prefix + variable + ".pdf", format="pdf")
                plotCount += 1
                lineCount = 0

print("Done plotting!")
print("Created " + str(plotCount) + " plots in " + args.outputFolder + "/.")
