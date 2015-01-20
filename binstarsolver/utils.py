"""Utilities for calculating physical quantities from observed quantities.

Docstrings are adapted from `numpy` convention:
https://github.com/numpy/numpy/blob/master/doc/example.py

"""

from __future__ import absolute_import, division, print_function
import sys
import numpy as np
import scipy.optimize as sci_opt
import scipy.constants as sci_con
import astropy.constants as ast_con
import matplotlib.pyplot as plt


def calc_flux_intg_rel_g_from_light(light_oc, light_ref=1.0):
    """Calculate integrated flux of the greater sized star relative to the total integrated flux.
    
    Parameters
    ----------
    light_oc : float
        Light level during occultation (primary eclipse). Light level is the average of the flat region at the bottom
        of one of the eclipse minima. The event is a total eclipse of the star with the smaller radius.
    light_ref : {1.0}, float, optional
        Reference for light levels outside of eclipse. Typically total system light is normalized to 1.0.
        
    Returns
    -------
    flux_intg_rel_g : float
        Integrated flux of greater-sized star as a fraction of total integrated flux.
    
    Notes
    -----
    flux_intg_rel_g = light_oc / light_ref
    From equation 7.2 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    flux_intg_rel_g = light_oc / light_ref
    return flux_intg_rel_g


def calc_flux_intg_rel_s_from_light(light_oc, light_ref=1.0):
    """Calculate integrated flux of the smaller sized star relative to the total integrated flux.

    Parameters
    ----------
    light_oc : float
        Light level during occultation (primary eclipse). Light level is the average of the flat region at the bottom
        of one of the eclipse minima. The event is a total eclipse of the star with the smaller radius.
    light_ref : {1.0}, float, optional
        Reference for light levels outside of eclipse. Typically total system light is normalized to 1.0.
    
    Returns
    -------
    flux_intg_rel_s : float
        Integrated flux of greater-sized star as a fraction of total integrated flux.
    
    Notes
    -----
    flux_intg_rel_s = (light_ref - light_oc) / light_ref
    From equation 7.2 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    flux_intg_rel_s = (light_ref - light_oc) / light_ref
    return flux_intg_rel_s


def calc_phase_orb_from_time_period(time_event, period, time_mideclipse=0.0):
    """Calculate orbital phase angle in radians for an event relative
    to mid-eclipse, given period.
    
    Parameters
    ----------
    time_event : float
        Time of event. Units are seconds.
    period : float
        Period of eclipse. Units are seconds.
    time_mideclipse : {0.0}, float, optional
        Mid-eclipse time. Units are seconds. Typically `time_event`
        is relative to `time_mideclipse` such that `time_mideclipse` == 0.0.
        
    Returns
    -------
    phase_orb : float
        Orbital phase angle in radians for `time_event`.
    
    Notes
    ------
    phase_orb = 2*pi*(t - t0) / period
    where t = `time_event`, t0 = `time_mideclipse`
    From equation 7.3 in section 7.3 of [1]_.

    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    phase_orb = 2.0 * np.pi * (time_event - time_mideclipse) / period
    return phase_orb


def calc_sep_proj_from_incl_phase(incl, phase_orb):
    """Calculate the projected separation of the two star centers in units of the
    star-star separation distance. Assumes orbit is circular about the system center of mass.
    
    Parameters
    ----------
    incl : float
        Orbital inclination. Angle between line of sight and the axis of the orbit. Unit is radians.
    phase_orb : float
        Orbital phase angle of event in radians.
    
    Returns
    -------
    sep_proj : float
        Separation of the two star centers projected onto the tangent plane of the sky.
        Unit is orbit radius.
    
    Notes
    -----
    sep_proj^2 = cos^2(incl) + sin^2(phase_orb)*sin^2(incl)
    From equation 7.3 in section 7.3 of [1]_.

    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    sep_proj = np.sqrt((np.cos(incl)**2.0) + (np.sin(phase_orb)**2.0)*(np.sin(incl)**2.0))
    return sep_proj


def calc_radii_ratio_from_light(light_oc, light_tr, light_ref=1.0):
    """Calculate ratio of radii of smaller-sized star to greater-sized star from light levels 
    during occultation and transit. Assumes L \propto r^2, no limb darkening.
    
    Parameters
    ----------
    light_oc : float
        Light level during occultation (primary eclipse). Light level is the average
        of the flat region at the bottom of one of the eclipse minima. The event is
        a total eclipse of the star with the smaller radius.
    light_tr : float
        Light level during transit (secondary eclipse). Light level is the average
        of the rounded region at the bottom of one of the eclipse minima. The event is
        an annular eclipse of the star with the larger radius.
    light_ref : {1.0}, float, optional
        Reference for light levels outside of eclipse. Typically total system light is normalized to 1.0.
        
    Returns
    -------
    radii_ratio_lt : float
        Ratio of radii of smaller-sized star to greater-sized star calculated from light levels
        during occultation and transit.
        radii_ratio = radius_s / radius_g  where radius_s,radius_g are radii of smaller-,greater-sized stars.

    Notes
    -----
    radii_ratio = radius_s / radius_g
    radii_ratio = sqrt((light_ref - light_tr) / light_oc)
    From equation 7.8 in section 7.3 of [1]_.

    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    radii_ratio_lt = np.sqrt((light_ref - light_tr) / light_oc)
    return radii_ratio_lt


def calc_radius_sep_g_from_sep(sep_proj_ext, sep_proj_int):
    """Calculate radius of greater-sized star from projections of star separations
    at external and internal tangencies.
    
    Parameters
    ----------
    sep_proj_ext : float
        Projected separation of star centers at external tangencies
        (e.g. begin ingress, end egress). Unit is star-star separation distance.
    sep_proj_int : float
        Projected separation of star centers at internal tangencies
        (e.g. end ingress, begin egress). Unit is star-star separation distance.
    
    Returns
    -------
    radius_sep_g : float
        Radius of greater-sized star. Unit is star-star separation distance.
    
    Notes
    -----
    radii_ratio = radius_sep_s / radius_sep_g
    sep_proj_ext = radius_sep_g * (1 + radii_ratio)
    sep_proj_int = radius_sep_g * (1 - radii_ratio)
    => sep_proj_ext + sep_proj_int = 2 * radius_sep_g
    From equations 7.8, 7.9, 7.10 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    radius_sep_g = (sep_proj_ext + sep_proj_int) / 2.0
    return radius_sep_g


def calc_radius_sep_s_from_sep(sep_proj_ext, sep_proj_int):
    """Calculate radius of smaller-sized star from projections of star separations
    at external and internal tangencies.
    
    Parameters
    ----------
    sep_proj_ext : float
        Projected separation of star centers at external tangencies
        (e.g. begin ingress, end egress). Unit is star-star separation distance.
    sep_proj_int : float
        Projected separation of star centers at internal tangencies
        (e.g. end ingress, begin egress). Unit is star-star separation distance.
    
    Returns
    -------
    radius_sep_s : float
        Radius of smaller-sized star. Unit is star-star separation distance.
    
    Notes
    -----
    radii_ratio = radius_sep_s / radius_sep_g
    sep_proj_ext = radius_sep_g * (1 + radii_ratio)
    sep_proj_int = radius_sep_g * (1 - radii_ratio)
    => sep_proj_ext - sep_proj_int = 2 * radius_sep_g * radii_ratio = 2 * radius_sep_s
    From equations 7.8, 7.9, 7.10 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    radius_sep_s = (sep_proj_ext - sep_proj_int) / 2.0
    return radius_sep_s


def calc_radii_ratio_from_rads(radius_sep_s, radius_sep_g):
    """Calculate ratio of radii of smaller-sized star to greater-sized star.
    
    Parameters
    ----------
    radius_sep_s : float
        Radius of smaller-sized star. Unit is star-star separation distance.
    radius_sep_g : float
        Radius of greater-sized star. Unit is star-star separation distance.
    
    Returns
    -------
    radii_ratio_rad : float
        Ratio of radii of smaller-sized star to greater-sized star calculated from star radii.
    
    Notes
    -----
    radii_ratio = radius_sep_s / radius_sep_g
    From equations 7.8 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry
    
    """
    radii_ratio_rad = radius_sep_s / radius_sep_g
    return radii_ratio_rad


def calc_incl_from_radii_ratios_phase_incl(radii_ratio_lt, phase_orb_ext, phase_orb_int,
                                           incl_init=np.deg2rad(85.0), show_plot=False):
    """Calculate inclination angle by minimizing difference of ratios of stellar radii as calulated
    from light levels and lightcurve events (tangencies) for various values of inclination.
    
    Parameters
    ----------
    radii_ratio_lt : float
        Ratio of radii of smaller-sized star to greater-sized star
        calculated from light levels during occultation and transit.
        radii_ratio = radius_s / radius_g  where radius_s,radius_g are radii of smaller-,greater-sized stars.
    phase_orb_ext : float
        Orbital phase angle at external tangencies (e.g. begin ingress, end egress). Unit is radians.
    phase_orb_int : float
        Orbital phase angle at internal tangencies (e.g. end ingress, begin egress). Unit is radians.
    incl_init : {numpy.deg2rad(85.0)}, float, optional
        Initial guess for inclination angle in radians for minimization procedure of differences in radii ratios.
        Radii ratio difference has a local maximum for `incl` = numpy.deg2rad(90).
    show_plot : {True}, bool, optional
        Create and show diagnostic plots of difference in independent radii_ratio values vs inclination angle.
        Use to check solution in case initial guess for inclination angle caused convergence to wrong solution
        for inclination angle.
    
    Returns
    -------
    incl : float
        Orbital inclination. Angle between line of sight and the axis of the orbit. Unit is radians.
    
    See Also
    --------
    calc_sep_proj_from_incl_phase, calc_radius_sep_s_from_sep, calc_radius_sep_g_from_sep, calc_radii_ratio_from_rads
    
    Notes
    ----
    Compares two independent ways of calculating radii_ratio in order to infer inclination angle.
    Equations from section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Budding, 2007, Introduction to Astronomical Photometry

    """
    # Make radii_ratio_rad and all dependencies functions of inclination.
    sep_proj_ext = lambda incl: calc_sep_proj_from_incl_phase(incl=incl, phase_orb=phase_orb_ext)
    sep_proj_int = lambda incl: calc_sep_proj_from_incl_phase(incl=incl, phase_orb=phase_orb_int)
    radius_sep_s = lambda incl: calc_radius_sep_s_from_sep(sep_proj_ext=sep_proj_ext(incl=incl),
                                          sep_proj_int=sep_proj_int(incl=incl))
    radius_sep_g = lambda incl: calc_radius_sep_g_from_sep(sep_proj_ext=sep_proj_ext(incl=incl),
                                          sep_proj_int=sep_proj_int(incl=incl))
    radii_ratio_rad = lambda incl: calc_radii_ratio_from_rads(radius_sep_s=radius_sep_s(incl=incl),
                                                              radius_sep_g=radius_sep_g(incl=incl))
    # Minimize difference between independent radii_ratio values.
    diff_radii_ratios = lambda incl: abs(radii_ratio_lt - radii_ratio_rad(incl=incl))
    result = sci_opt.minimize(fun=diff_radii_ratios, x0=incl_init)
    incl = result['x'][0]
    # Create and show diagnostic plot.
    if show_plot:
        incls_out = np.deg2rad(np.linspace(0, 90, num=1000))
        diff_radii_ratios_out = map(diff_radii_ratios, incls_out)
        plt.plot(np.rad2deg(incls_out), diff_radii_ratios_out)
        plt.title("Difference between independent radii ratio values\n" +
                  "vs inclination angle (zoomed out view)")
        plt.ylabel("abs(radii_ratio_lt - radii_ratio_rad(incl))")
        plt.xlabel("inclination angle (degrees)")
        plt.show()
        incls_in = np.deg2rad(np.linspace(np.rad2deg(incl) - 1.0, np.rad2deg(incl) + 1.0, num=1000))
        diff_radii_ratios_in = map(diff_radii_ratios, incls_in)
        plt.plot(np.rad2deg(incls_in), diff_radii_ratios_in)
        plt.title("Difference between independent radii ratio values\n" +
                  "vs inclination angle (zoomed in view)")
        plt.ylabel("abs(radii_ratio_lt - radii_ratio_rad(incl))")
        plt.xlabel("inclination angle (degrees)")
        plt.show()
    # Test that radii_ratio values can be matched.
    if diff_radii_ratios(incl) < 1e-3:
        print("INFO: Inclination yields self-consistent solution for model.")
    else:
        # Note: Printing to stderr will delay output if called from within a loop.
        print(("WARNING: Inclination does not yield self-consistent solution for model.\n" +
               "    Input parameters cannot be fit by model:\n" +
               "    radii_ratio_lt  = {rrl}\n" +
               "    phase_orb_ext    = {poe}\n" +
               "    phase_orb_int    = {poi}\n" +
               "    incl_init        = {ii}").format(rrl=radii_ratio_lt,
                                                     poe=phase_orb_ext,
                                                     poi=phase_orb_int,
                                                     ii=incl_init))
    return incl


def calc_semimaj_axis_from_period_velr_incl(period, velr, incl):
    """Calculate semi-major axis of a star's orbit from observed period, radial velocity,
    and orbital inclination. Assumes no orbital eccentricity.
    
    Parameters
    ----------
    period : float
        Period of eclipse. Unit is seconds.
    velr : float
        Observed radial velocity of star. Unit is m/s.
    incl : float
        Orbital inclination. Angle between line of sight and the axis of the orbit. Unit is radians.

    Returns
    -------
    axis : float
        Semi-major axis of star's orbit. Unit is meters.
    
    Notes
    -----
    v = 2*pi*a / P, where v is orbital velocity, a is semi-major axis, P is orbital period.
    v = vr / sin(i), where vr is observed radial orbital velocity, i is orbital inclination.
    => a = (P / (2*pi)) * (vr / sin(i))
    From section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics
    
    """
    axis = (period / (2.0*np.pi)) * (velr / np.sin(incl))
    return axis


def calc_sep_from_semimaj_axes(axis_1, axis_2):
    """Calculate separation distance between binary stars from semi-major axes.
    Assumes circular orbits.
    
    Parameters
    ----------
    axis_1 : float
        Semi-major axis of star 1's orbit. Unit is meters.
    axis_2 : float
        Semi-major axis of star 2's orbit. Unit is meters.
    
    Returns
    -------
    sep : float
        Separation distance between stars. Unit is meters.
        
    Notes
    -----
    From section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics
    
    """
    sep = axis_1 + axis_2
    return sep


def calc_radius_from_radius_sep(radius_sep, sep):
    """Calculate the radius of a star converting from units of star-star separation distance
    to meters.
    
    Parameters
    ----------
    radius_sep : float
        Radius of star. Units are star-star separation distance.
    sep : float
        Separation distance between stars. Units are meters.
        
    Returns
    -------
    radius : float
        Radius of star. Units are meters.
    
    Notes
    -----
    radius = radius_sep * sep
    
    """
    radius = radius_sep * sep
    return radius


def calc_radius_from_velrs():
    pass
# TODO: Resume here 1/17/2015. Add method from p191, eqns 7.8, 7.9, Carroll
# for calculating radius assuming radius is ~90 deg. Method does not agree with inclination solver.
# Add disclaimer for inclination solver, radius from lt method that radius from lt may not work
#    for stars off of main sequence.
# Compare:
#   radii ratios with ~90deg assumption
#   radii ratios from lt
#   radii ratios from timings
# Check that calculated luminosity ratios match

def calc_mass_ratio_from_velrs(velr_1, velr_2):
    """Calculate ratio of stellar masses from observed radial velocities.
    Assumes circular orbit.
    
    Parameters
    ----------
    velr_1 : float
        Observed radial velocity of star 1. Unit is m/s.
    velr_2 : float
        Observed radial velocity of star 2. Unit is m/s.
    
    Returns
    -------
    mass_ratio : float
        Ratio of stellar masses for stars 1 and 2 as mass1 / mass2. Unitless.
        
    Notes
    -----
    m1 / m2 = a2 / a1, where a is semi-major axis of low-eccentricty orbit.
    v = 2*pi*a / P, where v is orbital velocity, P is orbital period.
    v = vr / sin(i), where vr is observed radial orbital velocity, i is orbital inclination.
    => m1 / m2 = v2r / v1r
    From equation 7.5 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics

    """
    mass_ratio = velr_2 / velr_1
    return mass_ratio


def calc_mass_sum_from_period_velrs_incl(period, velr_1, velr_2, incl):
    """Calculate the sum of stellar masses from observed period, radial velocities,
    and orbital inclination. Assumes orbital excentricity << 1.
    
    Parameters
    ----------
    period : float
        Period of eclipse. Unit is seconds.
    velr_1 : float
        Observed radial velocity of star 1. Unit is m/s.
    v2r : float
        Observed radial velocity of star 2. Unit is m/s.
    incl : float
        Orbital inclination. Angle between line of sight and the axis of the orbit. Unit is radians.

    Returns
    -------
    mass_sum : float
        Sum of stellar masses for stars 1 and 2. Unit is kg.
    
    Notes
    -----
    a = (P/(2*pi)) * (v1 + v2), where a is semi-major axis of low-eccentricity orbit,
        P is orbital period, v is orbital velocity.
    P**2 = ((4*pi**2) / (G*(m1 + m2))) * a**3, where G is gravitational constant,
    m is stellar mass. Kepler's Third Law.
    v = vr / sin(i), where vr is observed radial orbital velocity, i is orbital inclination.
    => m1 + m2 = P/(2*pi*G) * ((v1r + v2r) / sin(i))**3    
    From equation 7.6 in section 7.3 of [1]_.
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics
    
    """
    mass_sum = (period / (2.0*np.pi*sci_con.G)) * ((velr_1 + velr_2) / np.sin(incl))**3.0
    return mass_sum


def calc_masses_from_ratio_sum(mass_ratio, mass_sum):
    """Calculate the individual stellar masses from their sum and ratio.
    
    Parameters
    ----------
    mass_ratio : float
        Ratio of stellar masses for stars 1 and 2 as mass1 / mass2. Unitless.
    mass_sum : float
        Sum of stellar masses for stars 1 and 2. Unit is kg.
    
    Returns
    -------
    mass_1 : float
        Mass of star 1. Unit is kg.
    mass_2 : float
        Mass of star 2. Unit is kg.
    
    Notes
    -----
    m1 + m2 = mass_sum
    m1 / m2 = mass_ratio
    => m1 = mass_ratio*m2
       m1 + m2 = m2*(mass_ratio + 1) = mass_sum
       m2 = mass_sum / (mass_ratio + 1)
    Masses are returned as a tuple: (m1, m2)

    """
    mass_2 = mass_sum / (mass_ratio + 1.0)
    mass_1 = mass_ratio * mass_2
    return (mass_1, mass_2)


def calc_flux_rad_ratio_from_light(light_oc, light_tr, light_ref=1.0):
    """Calculate ratio of the radiative fluxes of the smaller star to greater star
    from their light levels  during occultation and transit.
    Assumes L \propto r^2, no limb darkening.
    
    Parameters
    ----------
    light_oc : float
        Light level during occultation (primary eclipse). Light level is the average
        of the flat region at the bottom of one of the eclipse minima. The event is
        a total eclipse of the star with the smaller radius.
    light_tr : float
        Light level during transit (secondary eclipse). Light level is the average
        of the rounded region at the bottom of one of the eclipse minima. The event is
        an annular eclipse of the star with the larger radius.
    light_ref : {1.0}, float, optional
        Reference for light levels outside of eclipse. Typically total system light is normalized to 1.0.
        
    Returns
    -------
    flux_rad_ratio : float
        Ratio of radiative fluxes of smaller star to greater star.
        flux_rad_ratio = flux_rad_s / flux_rad_g

    Notes
    -----
    flux_rad_ratio = flux_rad_s / flux_rad_g
    flux_rad_ratio = (light_ref - light_oc) / (light_ref - light_tr)
    From equation 7.10 in section 7.3 of [1]_
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics
    
    """
    flux_rad_ratio = (light_ref - light_oc) / (light_ref - light_tr)
    return flux_rad_ratio


def calc_teff_ratio_from_flux_rad_ratio(flux_rad_ratio):
    """Calculate ratio of the effective temperatures of the smaller star to greater star
    from the ratios of the radiative fluxes.
    
    Parameters
    ----------
    flux_rad_ratio : float
        Ratio of radiative fluxes of smaller star to greater star.
        flux_rad_ratio = flux_rad_s / flux_rad_g
        
    Returns
    -------
    teff_ratio : float
        Ratio of effective temperatures of smaller star to greater star.
        teff_ratio = teff_s / teff_g

    Notes
    -----
    teff_ratio = teff_s / teff_g
    teff_ratio = flux_rad_ratio**0.25 = (flux_rad_s / flux_rad_g)**0.25
    From equation 7.10, 7.11 in section 7.3 of [1]_
    
    References
    ----------
    .. [1] Carroll and Ostlie, 2007, An Introduction to Modern Astrophysics
    
    """
    teff_ratio = flux_rad_ratio**0.25
    return teff_ratio