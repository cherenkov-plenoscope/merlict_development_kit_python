import numpy as np
import subprocess
import os
from . import configfile


def make_jobs(
    scenery_path,
    num_photons_per_block,
    map_dir,
    num_blocks,
    random_seed=0,
    merlict_map_path=None,
):
    """
    Returns a list of jobs (dicts) which can be processed by run_job().
    Each job adds a bit more statistics to the estimate of the light-field's
    geometry.

    Parameters
    ----------
    scenery_path : str
        Path to the scenery containing the instrument of which the
        light-field's geometry will be estimated of.
    num_photons_per_block: int
        The number of photons to be thrown in a single job.
    map_dir : str
        Path to the directory where the mapping of the jobs is done, i.e. where
        the jobs write their individual output to.
    num_blocks : int
        The number of jobs.
    random_seed : int
        The random_seed for the estimate.
    merlict_map_path : str (default: None)
        Path to the executable. In merlict, executing one job.
        If None, the path is looked up in the user's configfile.
    """
    if merlict_map_path is None:
        merlict_map_path = configfile.read()[
            "merlict-plenoscope-calibration-map"
        ]

    jobs = []
    running_seed = int(random_seed)

    for i in range(num_blocks):
        jobs.append(
            {
                "merlict_map_path": merlict_map_path,
                "scenery_path": scenery_path,
                "random_seed": running_seed,
                "map_dir": map_dir,
                "num_photons_per_block": num_photons_per_block,
            }
        )
        running_seed += 1
    return jobs


def run_job(job):
    """
    Wrap the merlict executable to run a job for the parallel estimate
    of the light-field's geometry.

    Parameters
    ----------
    job : dict
    """
    seed_str = "{:d}".format(job["random_seed"])
    call = [
        job["merlict_map_path"],
        "-s",
        job["scenery_path"],
        "-n",
        "{:d}".format(job["num_photons_per_block"]),
        "-o",
        os.path.join(job["map_dir"], seed_str),
        "-r",
        seed_str,
    ]
    return subprocess.call(call)


def reduce(map_dir, out_dir, merlict_reduce_path=None):
    """
    Reduce the intermediate results in the map_dir and write them to the
    out_dir.

    Parameters
    ----------

    map_dir : str
        Path to the directory where jobs have written their output to.
    out_dir : str
        Path to the output directory which will represent the
        light-field-geometry.
    merlict_reduce_path : str (default: None)
        Path to the executable. In merlict, reducing the results of the jobs.
        If None, the path is looked up in the user's configfile.
    """
    if merlict_reduce_path is None:
        merlict_reduce_path = configfile.read()[
            "merlict-plenoscope-calibration-reduce"
        ]

    return subprocess.call(
        [
            merlict_reduce_path,
            "--input",
            map_dir,
            "--output",
            out_dir,
        ]
    )
