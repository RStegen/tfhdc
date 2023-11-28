# tfhdc
Tin Foil Head Density Calculator

This is a demonstration project with the goal to create a standard framework for typical raster based geographical models.
At the current stage there isn't any scientific background, just techniques applied in a way that would be used to scientific models.

It's currently in it's alpha stage. Means things work fine but there is A LOT to add. 
The preprocessor requires an internet connection, as it is currently set to get data from openstreetmaps via the osmnx library. 
In later stages temporal data is intended to be added, but that's not yet implemented. The required techniques are the same as for the usage of the features taken from openstreetmaps.

Also it is necessary to set up a dask scheduler and dask workers for the parallelization to run. Otherwise it can only be used non parallel,
which tends to not be suitable on larger datasets due to greater than memory issues. 
Script snippets how to do it can be seen in the dask_starting.txt file. Remember to copy the ip of the scheduler. 

A conda environment suited to execute the program is added as the environment.yml
Change the first line "name" and the last line "prefix" for your individual environment name and path settings. 
Once modified conda will be able to create the environment using:
	conda env create -f ./environment.yml
	(Note, that you need to be in the conda base environment for that.)

The tfhdc can either be executed via a script (or other calls) using the tfhdc_main_run.py 
Or via command line, giving the path to the input.yml and, if used, the ip address of the dask scheduler.
example: 
	python ./tfhdc_run.py ./input.yml <ip>