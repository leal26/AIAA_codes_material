# -*- coding: utf-8 -*-
"""A perceived loudness (PLdB) calculator.

PyLdB implements Stevens' Mark VII procedure for the calculation of the
perceived loudness of a pressure signature.

Routine Listings
-----------------
PerceivedLoudness(time, pressure[, pad_f, pad_r, len_window])
Main routine. Calculates and displays perceived loudness in PLdB.

_window(dataset, len_window)     Applies a Hanning window to a dataset.

_padding(x_var, y_var, f_pad, r_pad)     Applies zero padding to the front and
                                         rear of a dataset with lengths of
                                         f_pad and r_pad respectively.
_power_spectrum(time, pressure)      Performs an FFT on the pressure signature
                                     and generates a one-sided power spectrum.

_power_interp(freq, power, N)     Interpolates power data to match frequency
                                  band boundaries.

_sound_pressure_levels(freq, power, n_bins)     Calculates the sound pressure
                                                level of each frequency band.

_equivalent_loudness(L, n_bins)     Calculates equivalent loudness values.

_loud_limits_400(f_central, lower_limit, upper_limit, loudness, X)
Chooses an appropriate equivalent loudness transformation according to dB
limits given in Stevens' methodology.

_calc_total_loudness(L_eq)    Uses table values to look up and interpolate a
                              summation factor and value in sones to calculate
                              a total loudness value in sones for a signature.

See Also
--------
numpy.interp : Linear interpolation for lists
numpy.hanning : Calculates a Hanning window given a number of points
numpy.pad : Zero-pads a list
numpy.fft.fft : Fast Fourier transform (FFT) routine
numpy.fft.fftfreq : Generates frequency range for FFT
numpy.argsort : Returns indices to sort an array
numpy.nonzero : Returns non-zero elements in an array subject to conditions
scipy.integrate.trapz : Performs trapezoidal numerical integration

Notes
------
The pyldb module utilizes the Mark VII procedure for the calculation of
perceived loudness created by Stevens. The procedure works by first importing
time and pressure data which is windowed and zero-padded prior to performing
a frequency analysis via an FFT. From the frequency analysis, a one-sided
power spectrum is created, which allows for the calculation of the energy
contained in one-third octave frequency bands for the pressure signature. The
energy is found by integrating the power spectrum using a trapezoidal rule.
This energy can be transformed into a sound pressure level measured in decibels
for each of the frequency bands. The sound pressure levels are then converted
to an equivalent loudness value using equal-sone contours generated by Stevens.
Using data tabulated by Stevens, a total loudness in units of sones is
calculated, which is then transformed into perceived loudness using a power law
developed by Stevens.

References
-----------
Stevens, S., “Perceived level of noise by Mark VII and decibels (E),”
The Journal of the Acoustical Society of America, Vol. 51,No. 2B, 1972,
pp. 575–601.

Jackson, G., and Leventhall, H., “Calculation of the perceived level of noise
(PLdB) using Stevens’ method (Mark VII),” Applied Acoustics, Vol. 6, No. 1,
1973, pp. 23–34.

Shepherd, K. P., and Sullivan, B. M., “A loudness calculation procedure
applied to shaped sonic booms,” 1991.

Johnson, D., and Robinson, D., “Procedure for calculating the loudness of
sonic bangs,” Acta Acustica united with Acustica, Vol. 21, No. 6, 1969,
pp. 307–318.

Example
--------
import pyldb
import numpy as np

time = np.arange(0,4*np.pi,0.01) # Any time array in miliseconds
pressure = 0.04*np.cos(time) # Any pressure array in lbs/ft^2 (psf)

PLdB = pyldb.perceivedloudness(time, pressure, pad_front=5, pad_rear=5,
                               len_window=1000)
print(PLdB)

"""

import numpy as np
import scipy.integrate as integrate
import os


def perceivedloudness(time, pressure,
                      pad_front=1, pad_rear=1,
                      len_window=800, print_results=False):
    r"""Calculates the perceived loudness using time and pressure values in
    miliseconds and lb/ft^2 (psf) respectively.

    This function encapsulates all of the calculation steps to return a
    perceived loudness value given two arrays for time and pressure. The
    pressure signature is first windowed using a Hanning window to ensure
    a complete cycle can be formed for use in a fast Fourier transform (FFT).
    Next, the time and pressure arrays are zero-padded to increase the
    resolution of the FFT output.

    Using the windowed and zero-padded pressure and time arrays, a one-sided
    power spectrum is produced. The energy in the power spectrum can then be
    calculated using a trapezoidal rule numerical integration algorithm.
    The energy is then used to find a sound pressure level in decibels for
    one-third octave frequency bands (stored as global constants).

    Stevens' Mark VII algorithm then transforms the sound pressure levels for
    each of the frequency bands into an equivalent loudness value with a 3150
    Hz reference frequency. The equivalent loudness values are then used with a
    table for conversion from decibels to sones (stored as a global constant).
    A summation parameter is likewise found using tabulated data from Stevens.
    Finally, a summation rule is used to find the total loudness, which is
    used alongside a power-rule to calculate the perceived loudness in PLdB.

    Parameters
    ----------
    time : array_like
        An array containing a time signature to be used in the calculation of
        the perceived loudness. This array should be sampled at a constant
        frequency. It should have the same number of points and the same
        spacing as the `pressure` parameter.
    pressure : array_like
        An array containing a pressure signature to be used in the calculation
        of the perceived loudness. This array should be sampled at a constant
        frequency. It should have the same number of points and the same
        spacing as the `time` parameter.
    pad_front : int, optional
        Defaults to 1. This parameter specifies the length of the zero-padding
        that will be applied to the font of the `time` and `pressure` arrays.
        For example, if `pad_front`=10, the length of the array of zeros added
        to the front of the `time` and `pressure` arrays will be equal to 10x
        the length of the `time` and `pressure` arrays.
    pad_rear : int, optional
        Defaults to 1. This parameter specifies the length of the zero-padding
        that will be applied to the font of the `time` and `pressure` arrays.
        For example, if `pad_front`=10, the length of the array of zeros added
        to the front of the `time` and `pressure` arrays will be equal to 10x
        the length of the `time` and `pressure` arrays.
    len_window : int, optional
        Defaults to 800 points. This parameter specifies the number of points
        over which the Hanning window will be applied on both the front and the
        rear of the signal. In other words, the front 800 points of the
        'pressure' array will be windowed with the first 800 points of a 1600
        point Hanning window, and the last 800 points of the `pressure` array
        will be windowed with the last 800 points of a 1600 point Hanning
        window.
    print_results : bool, optional
        Defaults to False. This parameter acts as a flag to output several
        meaningful results from the analysis performed by PyLdB. The results
        printed include the padded and windowed signature passed into the
        loudness calculator as well as the power spectrum of the signature, and
        the sound pressure level, equivalent loudness, and sone values
        associated with each frequency band. These results are placed in a
        directory called `PyLdB_Results` and are useful for analysis of the
        signature.

    Returns
    -------
    pldb : float
        Value for perceived loudness in units of PLdB.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> import pyldb
    >>> import numpy as np
    >>> time = np.linspace(0,100,num=10000) # Any time array in miliseconds
    >>> pressure = np.linspace(0,100,num=10000) # Any pressure array in psf
    >>> PLdB = pyldb.perceivedloudness(time, pressure, pad_front=4,pad_rear=4,
                                       len_window=1000)
    >>> print PLdB
    """
    # Initialize variables
    n_bins = len(BAND_CENTERS)
    frontpad = len(pressure)*pad_front
    rearpad = len(pressure)*pad_rear

    # Begin main PLdB calculation method
    pressure_window = _window(pressure, len_window)
    time_pad, pressure_pad = _padding(time, pressure_window, frontpad, rearpad)
    freq, power = _power_spectrum(time_pad, pressure_pad)
    energy, loudness = _sound_pressure_levels(freq, power, n_bins)
    L_eq = _equivalent_loudness(loudness, n_bins)
    total_loudness, sones = _calc_total_loudness(L_eq)
    pldb = 32.0 + 9.0*np.log2(total_loudness)

    # Prints relevant results from the loudness analysis
    if print_results:
        directory = './PyLdB_Results'
        if not os.path.exists(directory):
            os.makedirs(directory)
        np.savetxt(directory + '/final_sig',
                   np.array([time_pad, pressure_pad]).T)
        np.savetxt(directory + '/power_spec',
                   np.array([freq, power]).T)
        np.savetxt(directory + '/sound_pressure_levels',
                   np.array([BAND_CENTERS, loudness]).T)
        np.savetxt(directory + '/equivalent_loudness',
                   np.array([BAND_CENTERS, L_eq]).T)
        np.savetxt(directory + '/sones',
                   np.array([BAND_CENTERS, sones]).T)
    return pldb


def import_sig(filename, header_lines=0, delimiter=None):
    r"""Imports time and pressure data from a file provided by the user.

    Any file type that is compatible with numpy's genfromtxt method can be used
    with this function. The time data should be contained in the left-most
    column of the file, and the pressure data should be contained in the right-
    most column. Header lines should be skipped using the `header_lines`
    parameter.

    Parameters
    ----------
    filename : string
        Contains the name of the file from which the time and pressure data
        will be imported.
    header_lines : int, optional
        Specifies how many lines containing header information should be
        skipped when reading the file data.

    Returns
    -------
    time : array_like
        Array containing the time data imported from the file.
    pressure : array_like
        Array containing the pressure data imported from the file.

    Examples
    --------
    >>> import pyldb
    >>> time, pressure = pyldb.import_sig("Testsig.sig", header_lines=3)
    """
    data = np.genfromtxt(filename, skip_header=header_lines,
                         delimiter=delimiter)
    time = data[:, 0]
    pressure = data[:, 1]
    return time, pressure


def _window(dataset, len_window):
    win = np.hanning(len_window*2)
    windowed_data = np.copy(dataset)
    windowed_data[:len_window] *= win[:len_window]
    windowed_data[-len_window:] *= win[len_window:]
    return windowed_data


def _padding(x_var, y_var, f_pad, r_pad):
    pad_y = np.pad(y_var, (f_pad, r_pad), 'constant')
    frontpad = f_pad*(x_var[1] - x_var[0])
    rearpad = x_var[-1] + r_pad*(x_var[1] - x_var[0]) + frontpad
    frontx = np.linspace(x_var[0], frontpad, num=f_pad, endpoint=True)
    rearx = np.linspace(x_var[-1]+frontpad, rearpad, num=r_pad,
                        endpoint=True)
    padded_length = len(x_var) + len(frontx) + len(rearx)
    pad_x = np.zeros(padded_length)
    shifted_x = x_var[:] + frontpad
    pad_x[:len(frontx)] = frontx
    pad_x[len(frontx):len(frontx)+len(x_var)] = shifted_x
    pad_x[len(frontx)+len(x_var):] = rearx
    return pad_x, pad_y


def _power_spectrum(time, pressure):
    # The units for time are in milliseconds, and the units for pressure
    # are lbs/ft^2 (psf).
    N = len(pressure)
    dt = ((time[-1]-time[0])/N)*(10**-3)  # ms -> s
    FFT = np.fft.fft(pressure)
    freq = np.fft.fftfreq(N)/dt
    Power = (np.abs(FFT)**2)*(dt**2)
    freqOne, PowerOne = _power_interp(freq, Power, N)
    return freqOne, PowerOne


def _power_interp(freq, power, N):
    # Convert double sided Power Spectrum to single sided
    freq_one_side = np.copy(freq[0:N//2])
    power[1:N//2] = 2.*power[1:N//2]
    power_one_side = np.copy(power[0:N//2])

    # Interpolate values corresponding to band limits
    interp_freq = np.append(BAND_LOWER_LIMITS, BAND_UPPER_LIMITS[-1])
    interp_power = np.interp(interp_freq, freq_one_side, power_one_side)
    original_pow_freq = np.array([freq_one_side, power_one_side])
    interp_pow_freq = np.array([interp_freq, interp_power])
    full_pow_freq = np.concatenate((original_pow_freq, interp_pow_freq),
                                   axis=1)
    full_pow_freq_sort = np.argsort(full_pow_freq[0])
    freq_one = full_pow_freq[0, full_pow_freq_sort]
    power_one = full_pow_freq[1, full_pow_freq_sort]
    return freq_one, power_one


def _sound_pressure_levels(freq, power, n_bins):
    po = (2.900755e-9)*144  # psi -> psf
    t_crit = 0.07
    energy = np.zeros(n_bins)
    for j in range(n_bins):
        i_section = np.nonzero((BAND_LOWER_LIMITS[j] <= freq)
                               & (freq <= BAND_UPPER_LIMITS[j]))[0]
        if len(i_section) != 0:
            power_section = power[i_section]
            frequency_section = freq[i_section]
            energy[j] = integrate.trapz(power_section, x=frequency_section)
    energy /= t_crit
    loudness = 10*np.log10(energy/(po**2)) - 3
    return energy, loudness


def _equivalent_loudness(L, n_bins):
    L_eq = np.zeros(n_bins)
    for i in range(n_bins):
        if i > 39:
            L_eq[i] = L[i] + 4.*(39. - i)
        if 35 <= i <= 39:
            L_eq[i] = L[i]
        if 32 <= i <= 34:
            L_eq[i] = L[i] - 2.*(35. - i)
        if 26 < i <= 31:
            L_eq[i] = L[i] - 8.0
        if 20 <= i <= 26:
            if i == 26:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           76.0, 121.0, L[i], 0.0)
            if i == 25:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           77.5, 122.5, L[i], 1.5)
            if i == 24:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           79.0, 124.0, L[i], 3.0)
            if i == 23:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           80.5, 125.5, L[i], 4.5)
            if i == 22:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           82.0, 127.0, L[i], 6.0)
            if i == 21:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           83.5, 128.5, L[i], 7.5)
            if i == 20:
                L_eq[i] = _loud_limits_400(BAND_CENTERS[i],
                                           85.0, 130.0, L[i], 9.0)
        if i <= 19:
            numerator = ((160.0 - L[i])*np.log10(80.0))
            denominator = np.log10(BAND_CENTERS[i])
            L_eq_B = 160.0 - numerator/denominator
            L_eq[i] = _loud_limits_400(80.0, 86.5, 131.5, L_eq_B, 10.5)
    return L_eq


def _loud_limits_400(f_central, lower_limit, upper_limit, loudness, X):
    if loudness <= lower_limit:
        A = 115.0 - ((115.0-loudness)*np.log10(400.0))/np.log10(f_central)
        L_eq = A - 8.0
    if lower_limit < loudness <= upper_limit:
        L_eq = loudness - X - 8.0
    if loudness > upper_limit:
        A = 160.0 - ((160.0 - loudness)*np.log10(400.0))/np.log10(f_central)
        L_eq = A - 8.0
    return L_eq


def _calc_total_loudness(L_eq):
    sones = np.interp(L_eq, L_EQ_RANGE, SONES_L, left=0.0, right=SONES_L[-1])
    sum_f_max = np.interp(sones.max(), SONES_F, SUMMATION_FACTORS,
                          left=0.0, right=SUMMATION_FACTORS[-1])
    total_loudness = sones.max() + sum_f_max*(sum(sones) - sones.max())
    return total_loudness, sones


L_EQ_RANGE = np.arange(1, 141, 1)
SONES_L = [0.078, 0.087, 0.097, 0.107, 0.118,
           0.129, 0.141, 0.153, 0.166, 0.181,
           0.196, 0.212, 0.230, 0.248, 0.269,
           0.290, 0.314, 0.339, 0.367, 0.396,
           0.428, 0.463, 0.500, 0.540, 0.583,
           0.630, 0.680, 0.735, 0.794, 0.857,
           0.926, 1.000, 1.080, 1.170, 1.260,
           1.360, 1.470, 1.590, 1.710, 1.850,
           2.000, 2.160, 2.330, 2.520, 2.720,
           2.940, 3.180, 3.430, 3.700, 4.000,
           4.320, 4.670, 5.040, 5.440, 5.880,
           6.350, 6.860, 7.410, 8.000, 8.640,
           9.330, 10.10, 10.90, 11.80, 12.70,
           13.70, 14.80, 16.00, 17.30, 18.70,
           20.20, 21.80, 23.50, 25.40, 27.40,
           29.60, 32.00, 34.60, 37.30, 40.30,
           43.50, 47.00, 50.80, 54.90, 59.30,
           64.00, 69.10, 74.70, 80.60, 87.10,
           94.10, 102.0, 110.0, 119.0, 128.0,
           138.0, 149.0, 161.0, 174.0, 188.0,
           203.0, 219.0, 237.0, 256.0, 276.0,
           299.0, 323.0, 348.0, 376.0, 406.0,
           439.0, 474.0, 512.0, 553.0, 597.0,
           645.0, 697.0, 752.0, 813.0, 878.0,
           948.0, 1024., 1106., 1194., 1290.,
           1393., 1505., 1625., 1756., 1896.,
           2048., 2212., 2389., 2580., 2787.,
           3010., 3251., 3511., 3792., 4096.]
SONES_F = np.copy(SONES_L[9:104])
SUMMATION_FACTORS = [0.100, 0.122, 0.140, 0.158, 0.174,
                     0.187, 0.200, 0.212, 0.222, 0.232,
                     0.241, 0.250, 0.259, 0.267, 0.274,
                     0.281, 0.287, 0.293, 0.298, 0.303,
                     0.308, 0.312, 0.316, 0.319, 0.320,
                     0.322, 0.322, 0.320, 0.319, 0.317,
                     0.314, 0.311, 0.308, 0.304, 0.300,
                     0.296, 0.292, 0.288, 0.284, 0.279,
                     0.275, 0.270, 0.266, 0.262, 0.258,
                     0.253, 0.248, 0.244, 0.240, 0.235,
                     0.230, 0.226, 0.222, 0.217, 0.212,
                     0.208, 0.204, 0.200, 0.197, 0.195,
                     0.194, 0.193, 0.192, 0.191, 0.190,
                     0.190, 0.190, 0.190, 0.190, 0.190,
                     0.191, 0.191, 0.192, 0.193, 0.194,
                     0.195, 0.197, 0.199, 0.201, 0.203,
                     0.205, 0.208, 0.210, 0.212, 0.215,
                     0.217, 0.219, 0.221, 0.223, 0.224,
                     0.225, 0.226, 0.227, 0.227, 0.227]
BAND_CENTERS = [1.0000001, 1.25, 1.6, 2.0, 2.5, 3.15,
                4., 5., 6.3, 8., 10.,
                12.5, 16., 20., 25., 31.5,
                40., 50., 63., 80., 100.,
                125., 160., 200., 250., 315.,
                400., 500., 630., 800., 1000.,
                1250., 1600., 2000., 2500., 3150.,
                4000., 5000., 6300., 8000., 10000.,
                12500.]
BAND_LOWER_LIMITS = [0.89, 1.12, 1.41, 1.78, 2.24, 2.82,
                     3.55, 4.47, 5.62, 7.08, 8.91,
                     11.2, 14.1, 17.8, 22.4, 28.2,
                     35.5, 44.7, 56.2, 70.8, 89.1,
                     112., 141., 178., 224., 282.,
                     355., 447., 562., 708., 891.,
                     1120., 1410., 1780., 2240., 2820.,
                     3550., 4470., 5620., 7080., 8910.,
                     11200.]
BAND_UPPER_LIMITS = [1.12, 1.41, 1.78, 2.24, 2.82,
                     3.55, 4.47, 5.62, 7.08, 8.91,
                     11.2, 14.1, 17.8, 22.4, 28.2,
                     35.5, 44.7, 56.2, 70.8, 89.1,
                     112., 141., 178., 224., 282.,
                     355., 447., 562., 708., 891.,
                     1120., 1410., 1780., 2240., 2820.,
                     3550., 4470., 5620., 7080., 8910.,
                     11200., 14100.]
