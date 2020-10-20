########################################################################################################################
########################################################################################################################

##################################################
# Project 4: Driving a Tool from Python          #
# by Aniket N Prabhu                             #
# references: "run_hspice.py" by Steven Millman  #
##################################################

########################################################################################################################
import subprocess
import numpy as np
import shutil
########################################################################################################################

nodes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']  # These are nodes between inverters.
                                                                                    # considering 10 inverters
tphl = []  # making an array to store the values of tplh (time to propagate from low to high).
tphlmin = 2e-9  # initializing the minimum tphl value.
optf = 2  # initializing optimum fan value.
optN = 1  # initializing optimum number of stages/inverters.

########################################################################################################################

# sp is the file. Defining fan in a range of 1 to 10.
for fan in range(1, 10):
    for N in range(1, 14, 2):  # taking max number of inverters in the chain to be 13 and adding them in steps of 2
                               # so that the chain still "inverts"
        shutil.copy2("InvChHead.sp", "InvChain1.sp")  # InChHead.sp is the header file containing constants.
                                                      # shutil duplicates this header as InvChain1.sp
                                                      # unlike shutil.copy, shutil.copy2 also preserves file metadata
                                                      # (size, type, creator, etc.)
        sp = open("InvChain1.sp", "a+")  # append mode: adds lines after the existing lines instead of starting from the
                                         # first line. "a+" will create a file if it doesn't already exist.
        sp.write(".param fan = %d \n" % fan)  # %d is a numeric/decimal value placeholder.
                                          # \r is carriage return (returns cursor to beginning of the same line).
                                          # \n creates a new line.
        for inv in range(1, N):  # for every separate inverter.
            sp.write("Xinv%d %c %c inv M=fan**%d \n" % (inv, nodes[inv-1], nodes[inv], inv-1))
            # instantiating inverters, Xinv<constant> being the instance name and inv being the subcircuit name.
            # %c is a character placeholder
            # this will select the previous node and the current node starting from n0.
        sp.write("Xinv%d %c %c inv M=fan**%d \n" % (N, nodes[N - 1], 'z', N - 1))  # z is the final node.
        sp.write(".end")  # needed to end a spice file.
        sp.close()
        proc = subprocess.Popen(["hspice", "InvChain1.sp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # This will make "hspice" open and operate on "InvChain1.sp.
        output, err = proc.communicate()  # capturing stdout and stderr.
        data = np.recfromcsv("InvChain1.mt0.csv", comments="$", skip_header=3)  # for reading delay from the output
                                                                                # file. Comments would start with "$".
                                                                                # top 3 lines of header would be skipped
                                                                                # as we only need to retrieve the tphl
                                                                                # from the mt0.csv file, which is in
                                                                                # the 5th line.
        # print(type(data["tphl_inv"]))
        tphl.append(data["tphl_inv"])  # retrieving value from the "tphl_inv" column.
        if data["tphl_inv"] < tphlmin:
            tphlmin = data["tphl_inv"]
            optf = fan
            optN = N
        print("\r\nFan = %d; \nNumber of stages = %d; \nDelay=%s" % (fan, N, data["tphl_inv"]))
        # %s is a string placeholder
print("\nOptimum fan = %d; \nOptimum number of stages = %d; \nOptimum delay = %s"
      % (optf, optN, tphlmin))

########################################################################################################################
########################################################################################################################
