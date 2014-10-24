# Charlie Jiang
# 10-22-2014
# SSCP | Optimal concentrator setup times
#
# Compare performance for more concentrators vs. more setup time

import csv
import sys
import numpy as np
import math
from scipy.interpolate import interp1d
from scipy.integrate import quad

# Load Solpos data for the proper day from a csv. Return an ndarray containing this data.
# Rows: data for a given timestamp; columns: data type
#
def loadSolposData(filename):
	with open(filename, 'rb') as f:
		return np.loadtxt(f, delimiter=",",skiprows=1)

# Interpolate the given sample of f_discrete v. time
# Use cubic spline
def getInterpolation(time, f_discrete):
	return interp1d(time, f_discrete, kind='cubic', bounds_error=False, fill_value=0)

# Determine the total energy per unit area (direct normal, ground, W/m^2) we get
# when charging in a given time span (begin - end).
# ti = initial time, minutes from midnight (decimal value)
# tf = final time, min. from midnight
# f = function of direct normal radiation v. time -- f(t) = irrad.
def totalNormalEnergy(ti, tf, f):
	return quad(f, ti, tf, limit=100, full_output=1)[0]

# Return the total energy (W/m^2) from morning/nighttime charging when part of that 
# time before 8am and after 5pm is taken up by assembly.
# time = time (min) for assembly
# sunrise = sunrise time (hrs from midnight)
# sunrset = sunset ""
# f = solpos interpolated function for gndrn vs. hrs from midnight
def energyForSetupTime(time, sunrise, sunset, f):
	morningpower = totalNormalEnergy(sunrise, 8. - time/60., f)
	eveningpower = totalNormalEnergy(17. + time/60., sunset, f)
	return morningpower + eveningpower

# Return a string that turns a time in hours from midnight to "HH:MM:SS"
def hrsToReadable(time):
	(fparthrs, hrs) = math.modf(time)
	minsec = fparthrs * 60
	(fpartsec, min) = math.modf(minsec)
	sec = fpartsec * 60
	
	return "%d:%d:%d" % (hrs, min, sec)

def doTimes():
	print "Loading Solpos data..."
	solposfile = "solposdata.csv"
	if len(sys.argv) > 2:
		solposfile = sys.argv[2]
	solpos = loadSolposData(solposfile) # Solpos data, as ndarray; each element is a time

	print "Interpolating..."
	# Time, gndrn
	f = getInterpolation(solpos[:,0], solpos[:,11])

	# Compute total morning/night charging power for a range of assembly times
	sunrise = solpos[0,0]
	sunset = solpos[-1,0]
	print "\tSunrise (hr from 12am): ", hrsToReadable(sunrise)
	print "\tSunset (hr from 12am): ", hrsToReadable(sunset)

	# Let's compute the power for sunrise - 8am
	print "Computing sunrise to 8am power..."
	morningpow = totalNormalEnergy(sunrise, 8., f)
	print "\tPower (W): ", morningpow

	# And from 5pm - sunset
	print "Computing 5pm to sunset power..."
	eveningpow = totalNormalEnergy(17., sunset, f)
	print "\tPower (W): ", eveningpow


	print "Computing energy for range of setup times..."
	timerange = np.array(range(0,31),dtype=np.int32)
	energyForSetupTimes = [energyForSetupTime(time, sunrise, sunset, f) for time in timerange]

	print "Writing to file..."
	np.savetxt("energyVSetupTime.csv", np.column_stack((timerange, energyForSetupTimes)), \
		fmt=['%g', '%0.2f'], delimiter=",", header="Time(min),Energy(Wh/m^2)")
	return

def doNConcs():
	ELEMENT_LEN_CM = 15.5
	ELEMENT_AREA = ELEMENT_LEN_CM * ELEMENT_LEN_CM
	MAX_N = 65
	
# MAIN
if __name__ == "__main__":
	if len(sys.argv) > 1:
		if sys.argv[1].upper() == "TIMES":
			doTimes()
		elif sys.argv[1].upper() == "NCONCS":
			doNConcs()
		else:
			print "Nothing to be done."
	else:
		print "Nothing to be done."