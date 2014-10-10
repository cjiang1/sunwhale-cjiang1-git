
# coding: utf-8

## SSCP | Sunwhale | Charging Configuration Analysis

# In[99]:

get_ipython().magic(u'pylab inline')
import numpy as np
import math
import matplotlib.pyplot as plt

inToM = 0.0254 # Inches -> meters

def compute_d(wc, hc, theta_deg):
    """
    Compute d (the length of the space available for concentrators) for the given ndarray of angles
    """
    hb = 2.2 # Bounding box height
    wb = 1.8 # Bounding box width
    l = 12*inToM # Est. concentrator element length when fully deployed (lens + cell assembly + focal length + enclosure)
    
    theta_rad = theta_deg*(math.pi/180)
    return wb*np.sin(theta_rad) + hb*np.cos(theta_rad) - ((hc+l)/2)*np.sin(2*theta_rad) - wc

def compute_nrows(d):
    """
    Compute the number of rows of concentrators that can fit for the given ndarray of d
    """
    w = 7*inToM # Est. conc. element width when deployed (lens width + enclosure; assume element is square)
    return np.floor(d/w)

# Get a set of angles over which to compute (Max determined we need to consider 0-30 degrees)
theta = np.linspace(0,30,num=1001)
theta = np.delete(theta,0)


## Fitting concentrators for monocoque

# In[133]:

# Plot d, the space at the top of box available for concentrators (in m)
d = compute_d(1.8,0.55,theta)
plt.plot(theta,d)
plt.xlabel(r"$\theta$",fontsize=16)
plt.ylabel("d",fontsize=16)


# In[152]:

# Plot number of rows of concentrators that can fit
nrows = compute_nrows(d)
plt.plot(theta,nrows)
plt.xlabel(r"$\theta$",fontsize=16)
plt.ylabel("# rows",fontsize=16)

# Smallest angle that allows three rows to fit
threeRowsIs = np.where(nrows == 3)
minThetaThreeRows = theta[threeRowsIs[0][0]]
print "Smallest angle for three rows = ",minThetaThreeRows


### Fitting concentrators for topshell

# In[147]:

# Compute
topshell_widths = linspace(1.5,1.8,4) # Range of possible topshell widths over which to compute
topshell_height = 0.2 # Suppose the topshell curvature translates to a "height" of 0.2 m
d_data = np.zeros((topshell_widths.size, theta.size)) # Empty ndarray to store data for d
nrows_data = np.zeros((topshell_widths.size, theta.size)) # Empty ndarray to store data for # of rows

for i in range(0, topshell_widths.size):
    d_data[i] = compute_d(topshell_widths[i], topshell_height, theta)
nrows_data = compute_nrows(d_data)


# In[151]:

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


# In[ ]:



