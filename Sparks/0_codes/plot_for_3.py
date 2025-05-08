import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt("./collect_results/TOTAL.dat")

# data meaning
# step, TOTAL, TEMP, PRESSURE
# 1 step = 0.002 ps
# before that, 10000 minimization
t_per_step = 0.002
steps_min = 10000

print(data.shape)
# plot the results

# create figure and axis objects with subplots()
fig,ax = plt.subplots()
# make a plot
ax.plot( (data[:,0]-steps_min)*t_per_step,
        data[:,1],
        color="red", 
        marker="o")
# set x-axis label
# ax.set_xlabel("step", fontsize = 14)
ax.set_xlabel("Time (ps)", fontsize = 14)

# set y-axis label
ax.set_ylabel("Total potential energy",
              color="red",
              fontsize=14)
fig.savefig("./collect_results/EqHist_PotEne.jpg")
# ax.close()

fig,ax = plt.subplots()
# make a plot
ax.plot( (data[:,0]-steps_min)*t_per_step,
        data[:,2],
        color="red", 
        marker="o")
# set x-axis label
# ax.set_xlabel("step", fontsize = 14)
ax.set_xlabel("Time (ps)", fontsize = 14)

# set y-axis label
ax.set_ylabel("Temp (K)",
              color="red",
              fontsize=14)
# ---------------------------------------------------------------
# comment out if no pressure is collected
# ---------------------------------------------------------------
# # twin object for two different y-axis on the sample plot
# ax2=ax.twinx()
# # make a plot with different y-axis using second axis object
# ax2.plot( (data[:,0]-steps_min)*t_per_step, 
#          data[:,3],
#          color="blue",
#          marker="o")
# ax2.set_ylabel("Pressure (bar)",color="blue",fontsize=14)
# -----------------------------------------------------------------
# plt.show()
# save the plot as a file
fig.savefig("./collect_results/EqHist_Temp_Pressure.jpg",
            format='jpeg',
            dpi=100,
            bbox_inches='tight')


# use dcd file for the rmsd.dat plot 
data = np.genfromtxt("./collect_results/TestProt_chain_0_after_psf_AlongX_NPT_rmsd.dat")

# create figure and axis objects with subplots()
# one dcd step=1ps
t_dcd_step = 1.

fig,ax = plt.subplots()
# make a plot
ax.plot((data[:,0]-0)*t_dcd_step,
        data[:,1],
        color="red", 
        marker="o")
# set x-axis label
# ax.set_xlabel("dcd step", fontsize = 14)
ax.set_xlabel("Time (ps)", fontsize = 14)
# set y-axis label
ax.set_ylabel("RMSD (angstrom)",
              color="red",
              fontsize=14)
fig.savefig("./collect_results/EqHist_RMSD.jpg")


