%% CHARLIE JIANG
% SSCP | Sunwhale
% Run WSC route with Luminos altered for various concentrator/array charging
% configurations and plot the performance impacts, benchmarked against actual Luminos.

clc; clear; close all;
cd('Z://sscp//sunbad//strategy//LuminosModels')

% Night/morning array standing is equivalent to 1.5 hours at full array output (via Max)
arrayStandingEquivalence = 1.5;

% --Initialize--
route = initRoute();
luminos = initCar();

% --Arzon concentrator specs--
arzonLensArea = 155*155; % in mm^2
arzonLensThickness = 3.4; % mm
arzonLensDensity = 1.18/1000; % in g/mm^3
arzonLensMass = arzonLensArea*arzonLensThickness*arzonLensDensity; % in grams

% Mass = lens + cell/heat sink (0.51 lbs as given by Arzon) + carbon fiber enclosure (all the way around, 2mmm thick) + 1kg of other enclosure stuff
arzonMass = (arzonLensMass + 0.51*453 + 500 + 1000) / 1000; % in kg

arzonEfficiency = 0.31;
arzonPower = arzonLensArea * 1e-6 * 1000 * arzonEfficiency; % in W at STC (1000W/m^2)

%% -- Luminos baseline --
luminosSpeed = solveForOptimalSpeed(luminos, route, 1);
luminosResults = runRoute(luminos, route, luminosSpeed, 1);
luminosTime = luminosResults.hoursToComplete;

%% -- Now solve for different charging configurations --

% Initialize arrays for plotting
x_nConc = zeros(1,20);
y_percentShaded = zeros(1,20);
z_deltaSpeed = zeros(1,20);

%% Iterate over number of concentrators
i = 1;

for nConc = 15:25:115
    % Iterate over percent of array shaded (by concentrators)
    for percentShaded = 0:13.75:41.25
        x_nConc(i) = nConc;
	y_percentShaded(i) = percentShaded;
	
	thisCar = luminos;
	thisCar.mass = luminos.mass + nConc * arzonMass;
	thisCar.arrayPeak = thisCar.arrayPeak * 0.997; % Sacrifice one cell
	thisCar.arrayStandEnergy = arrayStandingEquivalence * (thisCar.arrayPeak * (1 - percentShaded/100) + nConc * arzonPower);

	thisCarSpeed = solveForOptimalSpeed(thisCar, route, 1);
	thisCarResults = runRoute(thisCar, route, thisCarSpeed, 1);
	thisCarTime = thisCarResults.hoursToComplete;
	z_deltaSpeed(i) = thisCarSpeed - luminosSpeed;

	i = i + 1;
    end
end

%% -- Plot scatter --

figure
scatter3(x_nConc, y_percentShaded, z_deltaSpeed)
title('Speed gains vs. charging configuration')
xlabel('# of concentrators')
ylabel('Percent shaded')
zlabel('Delta speed w.r.t Luminos')

%% -- Plot surface --

x_nConc_surf = 15:25:115;
y_shaded_surf = 0:13.75:41.25;
z_deltaSpeed_surf = reshape(z_deltaSpeed,[4,5])

figure
surf(x_nConc_surf, y_shaded_surf, z_deltaSpeed_surf)
title('Speed gain vs. charging config (surface plot)')
xlabel('# concentrators')
ylabel('Percent shaded')
zlabel('Delta speed (w.r.t Luminos)')



