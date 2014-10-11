
# coding: utf-8

## SSCP | Sunwhale | Charging Configuration Analysis

# In[41]:

get_ipython().magic(u'pylab inline')
import numpy as np
import math
import matplotlib.pyplot as plt

inToM = 0.0254 # Inches -> meters
NPOINTS = 1000 # Number of points to compute in each calculation

HB = 2.2 # Bounding box height
WB = 1.8 # Bounding box width
L = 12*inToM # Est. concentrator element length when fully deployed (lens + cell assembly + focal length + enclosure)
W = 7*inToM # Est. conc. element width when deployed (lens width + enclosure; assume element is square)

def compute_d(wc, hc, theta_deg):
    """
    Compute d (the length of the space available for concentrators) for the given ndarray of angles
    """
    theta_rad = theta_deg*(math.pi/180)
    return WB*np.sin(theta_rad) + HB*np.cos(theta_rad) - ((hc+L)/2)*np.sin(2*theta_rad) - wc

def compute_nrows(d):
    """
    Compute the number of rows of concentrators that can fit for the given ndarray of d
    """
    return np.floor(d/W)

# Get a set of angles over which to compute (Max determined we need to consider 0-30 degrees)
theta = np.linspace(0,30,num=NPOINTS+1)
theta = np.delete(theta,0)


## Fitting concentrators for monocoque

# In[42]:

# Plot d, the space at the top of box available for concentrators (in m)
d_monocoque = np.zeros((1,NPOINTS))
d_monocoque[0] = compute_d(1.8,0.55,theta)
plt.plot(theta,d_monocoque[0])
plt.xlabel(r"$\theta$",fontsize=16)
plt.ylabel("d",fontsize=16)


#### Rows of concentrators vs. angle for monocoque

# In[43]:

# Plot number of rows of concentrators that can fit
nrows_monocoque = np.zeros((1,NPOINTS))
nrows_monocoque[0] = compute_nrows(d_monocoque)
plt.plot(theta,nrows_monocoque[0])
plt.xlabel(r"$\theta$",fontsize=16)
plt.ylabel("# rows",fontsize=16)

# Smallest angle that allows three rows to fit
threeRowsIs = np.where(nrows_monocoque[0] == 3)
minThetaThreeRows = theta[threeRowsIs[0][0]]
print "Smallest angle for three rows =",minThetaThreeRows,"degrees"


### Fitting concentrators for topshell

# In[44]:

# Compute
topshell_widths = linspace(1.5,1.8,4) # Range of possible topshell widths over which to compute
topshell_height = 0.2 # Suppose the topshell curvature translates to a "height" of 0.2 m
d_data = np.zeros((topshell_widths.size, theta.size)) # Empty ndarray to store data for d
nrows_data = np.zeros((topshell_widths.size, theta.size)) # Empty ndarray to store data for # of rows

for i in range(0, topshell_widths.size):
    d_data[i] = compute_d(topshell_widths[i], topshell_height, theta)
nrows_data = compute_nrows(d_data)


# In[45]:

# Append monocoque data for comparison in plots
# Only run this once with the previous cell
topshell_widths = numpy.append(topshell_widths, "Monocoque")
nrows_data = numpy.append(nrows_data,nrows_monocoque,axis=0)
d_data = numpy.append(d_data,d_monocoque,axis=0)


#### Rows of concentrators for various topshell widths

# In[46]:

# Plot nrows vs. topshell_width vs. theta
fig,ax = plt.subplots()
for i in range(0,topshell_widths.size):
    ax.plot(theta, nrows_data[i], label=topshell_widths[i])
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles,labels)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
plt.xlabel(r"$\theta$",fontsize=16)
plt.ylabel("# rows",fontsize=16)
plt.title("Rows of concentrators for various topshell widths, 0-30 degrees",fontsize=16)
print "Topshell 'height' = ",topshell_height


# In[47]:

# What is the maximum topshell width to be able to fit three rows at 0 degrees?
print "Max topshell width for 3 rows at vertical (m) = ", HB-3*W


###  Performance vs. # Concentrators

# In[ ]:

# Number 

