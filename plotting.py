import argparse
from plotting_helpers import *

# generic plotting function
# -i expects one or more root files
# -o defined which kind of plots are created, and sets any other option needed for these
#    options are: oneTrigger, oneFile
# -t triggers defines which triggers are plotted (requires one or more)
# -v variables to be plotted (one or more)

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', required=True, nargs='+')
parser.add_argument('-o', '--options', required=True, nargs='+')
parser.add_argument('-t', '--triggers', required=True, nargs='+')
parser.add_argument('-v', '--variables', required=True, nargs='+')

args = parser.parse_args()

# getting potential mSD prefix from options
if "mSD35" in args.options: prefix = "mSD35__"
else: prefix = ""

if "oneTrigger" in args.options:

    print("Creating plots for a single trigger.")

    for trigger in args.triggers:

        # onen plot per variavble
        for variable in args.variables:

            fig, ax = plt.subplots()

            for file in args.input:

                with uproot.open(file) as f_in:

                    # autodetermine label from file name
                    label = file.replace("output_","").replace(".root","")
                    path_parts = len(label.split("/"))
                    if( path_parts > 1 ): label = label.split("/")[path_parts-1]

                    plotEfficiency(f_in[prefix + variable + "__before"], f_in[prefix + variable + "__" + trigger], label=label, ax=ax)

                    plt.ylabel("efficiency")
                    plt.xlabel(variable)
                    plt.legend()

                    # add some text explaining the cuts
                    text_in_plot = r"$\mathrm{leading~AK8}~p_{T} > 200~\mathrm{GeV}$"
                    if "mSD35" in prefix: text_in_plot += "\n$\mathrm{leading~AK8}~m_{SD} > 35~\mathrm{GeV}$"
                    plt.text(ax.get_xlim()[1]*0.45, 0.2, text_in_plot, fontsize=18)

                    fig.savefig(trigger + "__effi__" + prefix + variable + ".png", format="png")


elif "oneFile" in  args.options:

    for file in args.input:

        with uproot.open(file) as f_in:

            for variable in args.variables:

                fig, ax = plt.subplots()

                for trigger in args.triggers: plotEfficiency(f_in[prefix + variable + "__before"], f_in[prefix + variable + "__" + trigger], label=trigger, ax=ax)

                plt.ylabel("efficiency")
                plt.xlabel(variable)
                plt.legend()

                # add some text explaining the cuts
                text_in_plot = r"$\mathrm{leading~AK8}~p_{T} > 200~\mathrm{GeV}$"
                if "mSD35" in prefix: text_in_plot += "\n$\mathrm{leading~AK8}~m_{SD} > 35~\mathrm{GeV}$"
                plt.text(ax.get_xlim()[1]*0.45, 0.5, text_in_plot, fontsize=18)

                # autodetermine label from file name
                label = file.replace("output_","").replace(".root","")
                path_parts = len(label.split("/"))
                if( path_parts > 1 ): label = label.split("/")[path_parts-1]

                fig.savefig(label + "__effi__" + prefix + variable + ".png", format="png")