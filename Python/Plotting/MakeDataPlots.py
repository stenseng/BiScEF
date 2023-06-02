import os
import sys
import h5py    
import numpy as np   
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from itertools import compress

# NB: This script assumes that the file contains data from one day (or less)

def plot_timeseries_simple(constFilter, constStr):
	fig, axs = plt.subplots(2)
	plotWasMade = False

	if 'Phi60s1' in f.keys():
		hasValue = f['Phi60s1'][()] > 0
		if 'Unit' in f['Phi60s1'].attrs.keys():
			unitStr = f['Phi60s1'].attrs['Unit']
		else:
			unitStr = '?'
		axs[0].plot(list(compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)), list(compress(f['Phi60s1'][()], constFilter & hasValue)), '.')
		axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
		axs[0].xaxis.set_major_locator(mdates.HourLocator())
		axs[0].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
		axs[0].set_ylim([0, 1])
		axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
		axs[0].set_title('Phase Scintillation, ' + recCode + ', ' + constStr + ', ' + dateStr)
		axs[0].grid()
		plotWasMade = True

	if 'Phi60s2' in f.keys():
		hasValue = f['Phi60s2'][()] > 0
		if 'Unit' in f['Phi60s2'].attrs.keys():
			unitStr = f['Phi60s2'].attrs['Unit']
		else:
			unitStr = '?'
		axs[1].plot(list(compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)), list(compress(f['Phi60s2'][()], constFilter & hasValue)), '.')
		axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
		axs[1].xaxis.set_major_locator(mdates.HourLocator())
		axs[1].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
		axs[1].set_ylim([0, 1])
		axs[1].set_xlabel('UTC hour-of-day')
		axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
		axs[1].grid()
		plotWasMade = True

	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_PhaseScint' + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)





# Input from command line:
import argparse
parser = argparse.ArgumentParser(description="BiScEF data plotter",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog="NB: This script assumes that the file contains data from one day (or less)")
parser.add_argument("--GPS", action="store_true", help="Make plots for GPS")
parser.add_argument("--GLONASS", action="store_true", help="Make plots for GLONASS")
parser.add_argument("--Galileo", action="store_true", help="Make plots for Galileo")
parser.add_argument("--BeiDou", action="store_true", help="Make plots for BeiDou")
parser.add_argument("--SBAS", action="store_true", help="Make plots for SBAS")
parser.add_argument("--plot_ts_simple", action="store_true", help="Plot scintillation indices as simple time series")
parser.add_argument("--plot_ts_box", action="store_true", help="Plot scintillation indices as box-and-whiskers time series")
parser.add_argument("filename", help="Filename of input data file")
args = parser.parse_args()
config = vars(args)
# FOR DEBUGGING: print(config)
# FOR DEBUGGING: sys.exit("testing")

# Derived from command line input
datapath = os.path.dirname(config['filename'])
basename = os.path.basename(config['filename'])
fnamestem = os.path.splitext(basename)[0]

# Open file
print("Now reading " + config['filename'])
f = h5py.File(config['filename'], 'r')
if not f:
	sys.exit("Failed to open \"" + config['filename'] + "\"")

# Get info
recCode = f.attrs['ReceiverCode']
dateStr = datetime.strftime(datetime.utcfromtimestamp(min(f['UNIXTime'])), "%Y-%m-%d")

# Convert UNIX time array to list of UTC datetimes
dt_utcdatetimes = [datetime.utcfromtimestamp(x) for x in f['UNIXTime'][()]]

# Construct boolean arrays for sorting/filtering
isGPS     = (f['SVID'][()] >   0) & (f['SVID'][()] <  33)
isGLONASS = (f['SVID'][()] >  37) & (f['SVID'][()] <  63)
isGalileo = (f['SVID'][()] >  70) & (f['SVID'][()] < 107)
isSBAS    = ((f['SVID'][()] > 119) & (f['SVID'][()] < 141)) | ((f['SVID'][()] > 197) & (f['SVID'][()] < 216))
isBeiDou  = ((f['SVID'][()] > 140) & (f['SVID'][()] < 181)) | ((f['SVID'][()] > 222) & (f['SVID'][()] < 246))

# Make plot - Simple scatter plot time series
if(config['plot_ts_simple']):
	if(config['GPS']):
		plot_timeseries_simple(isGPS, "GPS")
	if(config['GLONASS']):
		plot_timeseries_simple(isGLONASS, "GLONASS")
	if(config['Galileo']):
		plot_timeseries_simple(isGalileo, "Galileo")
	if(config['BeiDou']):
		plot_timeseries_simple(isBeiDou, "BeiDou")
	if(config['SBAS']):
		plot_timeseries_simple(isSBAS, "SBAS")



# Make plot - Box-and-whiskers time series

hours = range(0, 24)
fig, axs = plt.subplots(2)
plotWasMade = False
if 'Phi60s1' in f.keys():
	hasValue = f['Phi60s1'][()] > 0
	dHourlyPhi60s1 = []
	for hour in hours:
		tr = [x.hour == hour for x in dt_utcdatetimes]
		dHourlyPhi60s1.append(list(compress(f['Phi60s1'][()], isGPS & tr & hasValue)))
	if 'Unit' in f['Phi60s1'].attrs.keys():
		unitStr = f['Phi60s1'].attrs['Unit']
	else:
		unitStr = '?'
	axs[0].boxplot(dHourlyPhi60s1, positions=hours)
	axs[0].set_ylim([0, 1])
	axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
	axs[0].set_title('Phase Scintillation, ' + recCode + ', GPS, ' + dateStr)
	axs[0].grid()
	plotWasMade = True

if 'Phi60s2' in f.keys():
	hasValue = f['Phi60s2'][()] > 0
	dHourlyPhi60s2 = []
	for hour in hours:
		tr = [x.hour == hour for x in dt_utcdatetimes]
		dHourlyPhi60s2.append(list(compress(f['Phi60s2'][()], isGPS & tr & hasValue)))
	if 'Unit' in f['Phi60s2'].attrs.keys():
		unitStr = f['Phi60s2'].attrs['Unit']
	else:
		unitStr = '?'
	axs[1].boxplot(dHourlyPhi60s2, positions=hours)
	axs[1].set_ylim([0, 1])
	axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
	axs[1].set_xlabel('UTC hour-of-day')
	axs[1].grid()
	plotWasMade = True

if plotWasMade:
	plt.savefig(datapath + '/' + fnamestem + '_PhaseScintBoxPlot' + '_GPS' + '.png', dpi=300)



# Make plot - Skyplot (TODO)

if 'Phi60s1' in f.keys():
	hasValue = f['Phi60s1'][()] > 0

	theta = list(compress(f['Azimuth'][()] * np.pi / 180, isGPS & hasValue))
	r = list(compress(90 - f['Elevation'][()], isGPS & hasValue))
	colors = list(compress(f['Phi60s1'][()], isGPS & hasValue))
	area = list(compress(1 + f['Phi60s1'][()] * 30, isGPS & hasValue))

	fig = plt.figure()
	ax = fig.add_subplot(projection='polar')
	ax.set_theta_zero_location("N")
	im = ax.scatter(theta, r, c=colors, s=area, cmap=plt.cm.jet, alpha=0.75)
	im.set_clim([0, 1])
	ax.set_rlim([0, 90])
	ax.set_yticks(range(0, 91, 30))
	ax.set_yticklabels(['90$^{\circ}$', '60$^{\circ}$', '30$^{\circ}$', '0$^{\circ}$'])
	ax.set_title('Phase Scintillation, ' + recCode + ', GPS, ' + dateStr)
	cb = fig.colorbar(im, ax=ax)
	cb.set_label(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')

	plt.savefig(datapath + '/' + fnamestem + '_' + 'Phi60s1' + '_' + 'SkyPlot' + '_GPS' + '.png', dpi=300)


# Make plot - Dots on map (TODO)
# 'Longitude', 'Latitude'


# TODO - Other constellations

# TODO - CN0 plots
# 'AvgCN0s1', 'AvgCN0s2', 'AvgCN0s3'

# TODO - S4 plots
#'S4s1', 'S4s2', 'S4s3', 

# TODO - Spectral parameters plots
#'Ts1', 'Ts2', 'Ts3', 
#'phighs1', 'plows1', 'pmids1', 'ps1', 'ps2', 'ps3'

# TODO - TEC plots
# 'TECtow'
# 'TECtow_uncal'

# TODO - ROTI plots
#'ROTI1Hz', 'ROTIFullHz', 




