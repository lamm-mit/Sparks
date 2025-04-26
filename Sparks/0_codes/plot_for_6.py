import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data = np.genfromtxt("./collect_results/smd_resu.dat")
print(data.shape)
# data: step, x,y,z,SMD_Fx,SMD_Fy,SMD_Fz,SMD_Fn

# create figure and axis objects with subplots()
fig = plt.figure(figsize=(12,8),dpi=200)
fig, ax0 = plt.subplots()
# make a plot
ax0.plot(data[:,1],
        data[:,7],
        color="red", 
        marker=".")
# set x-axis label
ax0.set_xlabel("x (Angstrom)", fontsize = 14)
# set y-axis label
ax0.set_ylabel("Fn (pN)",
              color="red",
              fontsize=14)
plt.savefig("./collect_results/SMDHist_x_Fn.jpg")

# ++++++++++++++++++++++++++++++++++++++++++++++++
# add a smoothed one
from scipy.ndimage.filters import uniform_filter1d

kernel_size_uni = 200
d_2 = uniform_filter1d(data[:,1],  size=kernel_size_uni, mode='nearest')
f_2 = uniform_filter1d(data[:,7],  size=kernel_size_uni, mode='nearest')

fig = plt.figure(figsize=(12,8),dpi=200)
fig, ax0 = plt.subplots()
# make a plot
ax0.plot(data[:,1],
        data[:,7],
        color="blue", 
        marker=".")
# make a plot
ax0.plot(d_2,
        f_2,
        color="red", 
        marker=".")
# set x-axis label
ax0.set_xlabel("x (Angstrom)", fontsize = 14)
# set y-axis label
ax0.set_ylabel("Fn (pN)",
              color="red",
              fontsize=14)
plt.savefig("./collect_results/SMDHist_x_Fn_smoothed.jpg")

data_smooth=np.hstack((np.reshape(d_2, (-1,1)), np.reshape(f_2, (-1,1))))

df = pd.DataFrame(data_smooth, columns=['x', 'F'])

df.to_csv('./collect_results/x_Fn_smoothed.csv', index=False)

