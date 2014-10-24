// Charlie Jiang
// 10-18-2014
// SSCP | Solar irradiance through day
//
// Test the power hit if we need some time to deploy concentrators from a collapsed
// configuration. We can charge the car in the morning until 8am and in the evening after
// 5pm. Determine the J/m^2 we can get if we take some time in both morning and evening
// to deploy concentrators. E.g., if we take 30 minutes to (dis)assemble concentrators,
// we can only charge from sunrise to 7:30am, and from 5:30pm to sunset, instead of 
// sunrise to 8am and 5pm to sunset. This program will determine the energy difference
// from this.

#include <iostream>
#include <cmath>
#include <fstream>
extern "C" {
	#include "solpos00.h"
}
using namespace std;

// Function definitions
posdata* initSolpos(posdata* pdat);
void getSunBounds(posdata* pdat, float* output);
double getGndrn(const posdata* pdat);
void getHMSFromMin(float time, int &hour, int &min, int &second);
void writePowerVTime(const float* sunbounds, posdata* pdat, ofstream &stream);
void writePowerAtTime(const float time, posdata* pdat, ofstream &stream);
void writeSolposLine(posdata* pdat, double gndrn, ofstream &stream, int header=0);

/*
 * Arguments:
 *  [1] Compute Solpos values? 1 for yes
 *  [2] If [1] is 1, then [2] is a filename to write solpos data to
 */
int main(int argc, char* argv[]) {
	string outname = "solposdata.csv";
	if (argc > 2) outname = argv[2]; // Get filename
		
	struct posdata pd, *pdat;
	pdat = initSolpos(&pd); // Initialize!
	
	float sunbounds [2];
	getSunBounds(pdat, sunbounds);
	
	// Write solpos data
	ofstream stream;
	stream.open(outname);
	writePowerVTime(sunbounds, pdat, stream);
	stream.close();
	
	cout << "DONE!" << endl;
		
}

/* Initialize pdat with specified values and return a pointer to it. */
posdata* initSolpos(posdata* pdat) {
	S_init(pdat); // Initialize for Solpos

	/* Let's use Coober Pedy, AU. Coordinates: 29.0111° S, 134.7556° E. */
	pdat->latitude = -29.0111;
	pdat->longitude = 134.7556;
	pdat->timezone = 10.5; // GMT +10:30
	pdat->year = 2015;
	pdat->daynum = 293; // October 20, 2015;
	pdat->temp = 20.0; // Average temperature (°C) at 9am
	pdat->press = 1013.0; // Default atm. pressure, 1013 millibar
	pdat->interval = 0; // Instantaneous output
	pdat->function = (S_AMASS | S_ETR | S_REFRAC | S_SRSS); // Output parameters to compute
	// Leave panel tilt and shadow band parameters as defaults (we won't need them)

	return pdat;
}

/* Return sunrise and sunset time for the given day, location, etc. stored in pdat. 
 * Values are minutes from midnight. */
void getSunBounds(posdata* pdat, float* output) {
	cout << "GETSUNRISESET: Getting sunrise and sunset times..." << endl;
	
	long errorcodes;

	pdat->hour = 0;
	pdat->minute = 0;
	pdat->second = 1;
	errorcodes = S_solpos(pdat);
	S_decode(errorcodes, pdat); // Look at possible error codes
	
	cout << "\tSunrise: " << pdat->sretr << endl;
	cout << "\tSunset : " << pdat->ssetr << endl;
	
	output[0] = pdat->sretr;
	output[1] = pdat->ssetr;
}

/* Compute the ground irradiance from a given posdata snapshot. */
double getGndrn(const posdata* pdat) {
	return 1.1 * pdat->etrn * pow(0.7, pow(pdat->ampress, 0.678));
}

/* Compute the hour, minute, and second from the given time, which is a double in minutes. */
void getHMSFromMin(float time, int &hour, int &min, int &second) {
	hour = (int)(time / 60);
	min = ((int)time % 60);
	second = (int)(60 * (time - (long)time));
}

/* Write a dataset containing Solpos computed solar position and power
 * for either morning or night, from sunrise to sunset.
 * sunbounds: [0] = sunrise, [1] = sunset, in minutes.
 * pdat: an initialized posdata object containing location, date, and sunrise/sunset data.
 * stream: ofstream to write to.
 */
void writePowerVTime(const float* sunbounds, posdata* pdat, ofstream &stream) {
	cout << "WRITEPOWERVTIME: Writing to file..." << endl;
	long errorcodes;
	
	int hour, minute, second;
	
	// Write header
	writeSolposLine(pdat, 0, stream, 1);

	// Do sunrise
	cout << "\tSunrise: " << sunbounds[0] << endl;
	writePowerAtTime(sunbounds[0], pdat, stream);
		
	// Do every minute between sunrise and sunset
	for (int time=(int)sunbounds[0]+1; time < sunbounds[1]; time++) {
		writePowerAtTime(time, pdat, stream);
	}
	
	// Do sunset
	writePowerAtTime(sunbounds[1], pdat, stream);
	cout << "\tSunset: " << sunbounds[1] << endl;

	
}

/* Compute and write solpos data at the specified time. */
void writePowerAtTime(const float time, posdata *pdat, ofstream &stream) {
	int hour, minute, second;
	long errorcodes;
	getHMSFromMin(time, hour, minute, second);
	pdat->hour = hour;
	pdat->minute = minute;
	pdat->second = second;
	errorcodes = S_solpos(pdat);
	S_decode(errorcodes, pdat);
	double gndrn = getGndrn(pdat);
	writeSolposLine(pdat, gndrn, stream);
	cout << "\tWrote line to file for time " << hour << ":" << minute << ":" << second << endl;
	
}

/* Write a single line from the given position data. 
 * We want time, ampress (adjusted airmass), azim (azimuth angle), elevetr (unrefracted elevation),
 * elevref (refracted elevation angle), etrn (top-of-atm. direct normal irradiance),
 * gndrn (direct normal irradiance at ground, using Wikipedia's estimate of atm. effects).
 * 
 * Header = 1 if writing header line
 */
void writeSolposLine(posdata* pdat, double gndrn, ofstream &stream, int header) {
	// time, hour, minute, second, azim, elevetr, elevref, etrn, ampress, gndrn

	if (header > 0) {
		stream << "Time(hr),Time(min),Time(sec), Hour,Minute,Second,Azim," <<
			"Elevetr,Elevref,Etrn,Ampress,Gndrn" << endl;
	}
	
	else {
		// Compute time from midnight, in hours, minutes, seconds
		double timehr = (pdat->hour + (double)pdat->minute / 60 + (double)pdat->second / 3600);
		double timemin = (60 * pdat->hour + pdat->minute + (double)pdat->second / 60);
		double timesec = (3600 * pdat->hour + 60 * pdat-> minute + pdat->second);
		
		stream << timehr << "," << timemin << "," << timesec << "," << pdat->hour << "," \
			<< pdat->minute << "," << pdat->second << "," \
 			<< pdat->azim << "," << pdat->elevetr << "," << pdat->elevref << "," \
 			<< pdat->etrn << "," << pdat->ampress << "," << gndrn << endl;
	}
	
}



	