import subprocess
import json_utils
import photon_spectra
import numpy as np
import os
import shutil
from . import configfile


def plenoscope_propagator(
    corsika_run_path,
    output_path,
    light_field_geometry_path,
    merlict_plenoscope_propagator_config_path,
    random_seed,
    photon_origins,
    stdout_path,
    stderr_path,
    merlict_plenoscope_propagator_path=None,
):
    """
    Calls the merlict Cherenkov-plenoscope propagation
    and saves the stdout and stderr

    Parameters
    ----------
    corsika_run_path : str
        Path to CORSIKA primary mod's Cherenkov outout in EventTape format.
    output_path : str
        Path to output directory
    light_field_geometry_path : str
        Path to instrument's light-field calibration.
    merlict_plenoscope_propagator_config_path : path
        Path to the config file which controls the night-sky-background
        flux and the photo-detection efficiency of the instrument.
    random_seed : int
        Seed for merlict.
    photon_origins : bool
        If True, merlict will also output the origin of the photons.
    stdout_path : str
        Path to write merlict's stdout to.
    stderr_path : str
        Path to write merlict's stderr to.
    merlict_plenoscope_propagator_path : str (default: None)
        Path to the merlict executable.
        If None, the path is looked up in the user's configfile.

    Returns
    -------
    merlict's return code : int
    """
    if merlict_plenoscope_propagator_path is None:
        merlict_plenoscope_propagator_path = configfile.read()[
            "merlict-plenoscope-propagation"
        ]

    with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
        call = [
            merlict_plenoscope_propagator_path,
            "-l",
            light_field_geometry_path,
            "-c",
            merlict_plenoscope_propagator_config_path,
            "-i",
            corsika_run_path,
            "-o",
            output_path,
            "-r",
            "{:d}".format(random_seed),
        ]
        if photon_origins:
            call.append("--all_truth")
        mct_rc = subprocess.call(call, stdout=out, stderr=err)
    return mct_rc


def plenoscope_propagator_raw_photons(
    input_path,
    output_path,
    light_field_geometry_path,
    merlict_plenoscope_propagator_config_path,
    random_seed=0,
    merlict_plenoscope_raw_photon_propagation_path=None,
):
    """
    Calls the merlict Cherenkov-plenoscope propagation for raw photons
    and saves the stdout and stderr

    Parameters
    ----------
    input_path : str
        Path to the raw photons.
    output_path : str
        Path to output directory
    light_field_geometry_path : str
        Path to instrument's light-field calibration.
    merlict_plenoscope_propagator_config_path : path
        Path to the config file which controls the night-sky-background
        flux and the photo-detection efficiency of the instrument.
    random_seed : int
        Seed for merlict.
    merlict_plenoscope_propagator_path : str (default: None)
        Path to the merlict executable.
        If None, the path is looked up in the user's configfile.

    Returns
    -------
    merlict's return code : int
    """
    if merlict_plenoscope_raw_photon_propagation_path is None:
        merlict_plenoscope_raw_photon_propagation_path = configfile.read()[
            "merlict-plenoscope-raw-photon-propagation"
        ]

    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    mct_propagate_call = [
        merlict_plenoscope_raw_photon_propagation_path,
        "-l",
        light_field_geometry_path,
        "-c",
        merlict_plenoscope_propagator_config_path,
        "-i",
        input_path,
        "-o",
        output_path,
        "--all_truth",
        "-r",
        str(random_seed),
    ]

    o_path = output_path + ".stdout.txt"
    e_path = output_path + ".stderr.txt"
    with open(o_path, "wt") as fo, open(e_path, "wt") as fe:
        rc = subprocess.call(mct_propagate_call, stdout=fo, stderr=fe)
    return rc


def read_plenoscope_geometry(merlict_scenery_path):
    """
    Parses the cofiguration for merlict's ligth-field camera from a scenery.

    Parameters
    ----------
    merlict_scenery_path : str
        Path to the scenery

    Returns
    -------
    config : dict
    """
    with open(merlict_scenery_path, "rt") as f:
        _scenery = json_utils.loads(f.read())
    children = _scenery["children"]
    for child in children:
        if child["type"] == "Frame" and child["name"] == "Portal":
            protal = child.copy()
    for child in protal["children"]:
        if child["type"] == "LightFieldSensor":
            light_field_sensor = child.copy()
    return light_field_sensor


def make_plenoscope_propagator_config(
    night_sky_background_ligth_key="nsb_la_palma_2013_benn",
    photo_electric_converter_key="hamamatsu_r11920_100_05",
):
    """
    Create the config to control the night-sky-background flux and the
    photo-detection-efficiency in merlict's simulations.

    Parameters
    ----------
    night_sky_background_ligth_key : str
        A key pointing to the package photon_spectra.
    photo_electric_converter_key : str
        A key pointing to the package photon_spectra.

    Returns
    -------
    config : dict
    """
    nsb = getattr(photon_spectra, night_sky_background_ligth_key).init()
    pec = getattr(photon_spectra, photo_electric_converter_key).init()

    return make_plenoscope_propagator_config_explicit(
        night_sky_background_ligth=nsb,
        photo_electric_converter=pec,
    )


def make_plenoscope_propagator_config_explicit(
    night_sky_background_ligth,
    photo_electric_converter,
):
    """
    Create the config to control the night-sky-background flux and the
    photo-detection-efficiency in merlict's simulations.

    Parameters
    ----------
    night_sky_background_ligth : dict
        Describes the flux of nightly photons. Format according to package
        photon_spectra.
    photo_electric_converter : dict
        Describes the detection efficiency of photosensors. Format
        according to package photon_spectra.

    Returns
    -------
    config : dict
    """
    nsb = night_sky_background_ligth
    pec = photo_electric_converter

    assert len(nsb["wavelength"]) == len(nsb["value"])
    assert nsb["units"][0] == "m"
    assert nsb["units"][1] == "m^{-2} sr^{-1} s^{-1} m^{-1}"
    assert np.all(nsb["value"] > 0.0), "can be tiny, but must not be zero"

    assert len(pec["wavelength"]) == len(pec["value"])
    assert pec["units"][0] == "m"
    assert pec["units"][1] == "1"
    assert np.all(pec["value"] <= 1.0)

    # sorted in wavelength
    assert np.all(np.gradient(nsb["wavelength"]) > 0.0)
    assert np.all(np.gradient(pec["wavelength"]) > 0.0)

    # max wavelength of photosensor must exceed max wavelength of nsb.
    if nsb["wavelength"][-1] >= pec["wavelength"][-1]:
        assert nsb["wavelength"][-1] - pec["wavelength"][-1] < 0.5e-9
        nsb["wavelength"][-1] = pec["wavelength"][-1] - 1e-9

    if nsb["wavelength"][0] > pec["wavelength"][0]:
        pec["wavelength"], pec["value"] = _limit_min_wavelength(
            wavelengths=pec["wavelength"],
            values=pec["value"],
            min_wavelength=nsb["wavelength"][0],
        )

    _nsb = {}
    _nsb["flux_vs_wavelength"] = np.c_[nsb["wavelength"], nsb["value"]]
    _nsb["exposure_time"] = 50e-9
    _nsb["comment"] = nsb["key"] + "," + nsb["reference"]

    _pec = {}
    _pec["quantum_efficiency_vs_wavelength"] = np.c_[
        pec["wavelength"], pec["value"]
    ]
    _pec["dark_rate"] = 1e-3
    _pec["probability_for_second_puls"] = 0.0
    _pec["comment"] = pec["key"] + "," + pec["reference"]

    _phs = {}
    _phs["time_slice_duration"] = 0.5e-9
    _phs["single_photon_arrival_time_resolution"] = 0.416e-9

    cfg = {}
    cfg["night_sky_background_ligth"] = _nsb
    cfg["photo_electric_converter"] = _pec
    cfg["photon_stream"] = _phs
    return cfg


def _limit_min_wavelength(wavelengths, values, min_wavelength):
    keep_mask = wavelengths > min_wavelength
    num_keep = sum(keep_mask)
    min_wavelength_value = np.interp(
        x=min_wavelength, xp=wavelengths, fp=values
    )
    _w = np.nan * np.ones(num_keep + 1)
    _v = np.nan * np.ones(num_keep + 1)
    _w[0] = min_wavelength
    _v[0] = min_wavelength_value
    _w[1:] = wavelengths[keep_mask]
    _v[1:] = values[keep_mask]
    return _w, _v
