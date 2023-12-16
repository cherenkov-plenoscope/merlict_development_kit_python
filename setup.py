import setuptools
import os


with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

with open(
    os.path.join(
        "merlict_development_kit_python_cherenkov-plenoscope-project",
        "version.py",
    )
) as f:
    txt = f.read()
    last_line = txt.splitlines()[-1]
    version_string = last_line.split()[-1]
    version = version_string.strip("\"'")

setuptools.setup(
    name="merlict_development_kit_python",
    version=version,
    description=(
        "A python package to ease the call of executables in "
        "the merlict_development_kit."
    ),
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cherenkov-plenoscope/merlict_development_kit_python",
    author="Sebastian Achim Mueller",
    author_email="Sebastian Achim Mueller@mail",
    packages=[
        "merlict_development_kit_python",
    ],
    package_data={"merlict_development_kit_python": []},
    install_requires=[
        "json_utils_sebastian-achim-mueller",
        "photon_spectra_cherenkov-plenoscope-project",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
)
