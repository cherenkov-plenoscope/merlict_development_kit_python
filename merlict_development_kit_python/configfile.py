import os
import json_utils


def get_configfile_path(programname="merlict_develompment_kit_python.json"):
    return os.path.join(os.path.expanduser("~"), "." + programname)


def read():
    configfile_path = get_configfile_path()
    if not os.path.exists(configfile_path):
        write(config=default(build_dir="build"))

    with open(configfile_path, "rt") as f:
        config = json_utils.loads(f.read())
    return config


def write(config):
    with open(get_configfile_path(), "wt") as f:
        f.write(json_utils.dumps(config, indent=4))


def default(build_dir):
    out = {}
    executables = [
        "merlict-plenoscope-calibration",
        "merlict-plenoscope-calibration-map",
        "merlict-plenoscope-calibration-reduce",
        "merlict-plenoscope-propagation",
        "merlict-plenoscope-raw-photon-propagation",
        "merlict-eventio-converter",
        "merlict-propagate",
        "merlict-cameraserver",
        "merlict-show-photons",
        "merlict-show",
    ]
    for exe in executables:
        out[exe] = os.path.join(os.path.abspath(build_dir), exe)
    return out
