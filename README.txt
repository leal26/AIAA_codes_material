# README #
This directory contains 'Codes' and 'Data' pertinent to the paper 'Effects of atmospheric profiles on the perceived loudness of low-boom supersonic vehicles' sumbitted to the Science Journal in 09/27/2019.


# Codes #
The Codes directory contains all the necessary codes to plot the results in Fig 2 and 3. Each subdirectory is named after the intended task that can be accomplished by running the 'main.py' file (other files are libraries or data used by the main file).
Because the software sBoom from NASA is 'Export Controlled', it is not provided in this supplementary material. Therefore PLdB will not be calculated unless the software is requested to NASA.
	- Matlab code to ‘Retrieve NOAA GFS data’
	- Python code to ‘Retrieve radiosonde data’
	- Python code to ‘Retrieve US Census population’
	- Python code to ‘Calculate PLdB from GFS’
	- Python code to ‘Calculate PLdB from radiosonde’
	- Python code to ‘Calculate exposed population’


# Data#
The Data directory contains the atmospheric and population information necessary for the sonic boom evaluations as well as the calculated values.
In this directory, all the information is provided as '.xlsx' files. The original data was stored in pickle files, .p, and are stored in the 'Codes' folder to allow the user to utilize the provided codes.
The files stored here are:
	- Data S1: loudness predictions for 2018 summer solstice UTC - 00:00
	- Data S2: loudness predictions for 2018 summer solstice UTC - 12:00
	- Data S3: loudness predictions for 2018 winter solstice UTC - 00:00
	- Data S4: loudness predictions for 2018 winter solstice UTC - 12:00
	- Data S5: atmospheric conditions at Dallas during 2018
	- Data S6: atmospheric conditions at Denver during 2018
	- Data S7: loudness predictions at Dallas during 2018
	- Data S8: loudness predictions at Denver during 2018
	- Data S9: population/loudness per county from US Census Data (2009-2017) 

	
For further questions, please contact Pedro Leal at leal26@tamu.edu

Pedro Leal
