from filter_funcs import *
import matplotlib.pyplot as plt
from antares_devkit.models import BaseFilter
from antares_devkit.models import DevKitLocus
from astropy.time import Time
import math
from astropy.coordinates import Angle, SkyCoord
import astropy.units as u
import itertools
import pdb
from astropy.io import fits

plot_lc('ANT2020eb22e')
plt.show()