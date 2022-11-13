import os, sys

def main():
    print('============================================')
    print('Usage: python data/ConvertCorrectionFiles.py')
    print('============================================')

    rootdir = os.path.abspath(os.getcwd())

    # To apply jet corrections in coffea, the files need a special naming.
    # JEC: .txt -> .jec.txt
    # JER: .txt -> .jr.txt (not implemented yet)
    # Unc: .txt -> .junc.txt

    print('Looking at', rootdir)
    for gSub, gDir, gFile in os.walk(rootdir):
        directories=gDir
        for d in directories:
            dir = rootdir+"/"+d+"/"
            print("Change files in", d)
            print(dir)
            for subdir, dirs, files in os.walk(dir):
                for f in files:
                    print(f)
                    f_new = ""
                    if "Uncertainty" in f and not "junc.txt" in f:
                        f_new = f.replace('.txt', '.junc.txt')
                        os.rename(dir+f, dir+f_new)
                    elif not "Uncertainty" in f and not "jec.txt" in f:
                        f_new = f.replace('.txt', '.jec.txt')
                        os.rename(dir+f, dir+f_new)


main()
