#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

name = "psychopy-crs"
version = "0.0.1"
packages = [
    'psychopy_crs'
]
package_dir = {
    'psychopy_crs': 'psychopy_crs'
}
package_data = {
   "": ["*.txt", "*.md"]
}

description = (
    "Extension package for PsychoPy which adds support for various hardware "
    "devices by Cambridge Research Systems.")

setup(
    name=name,
    version=version,
    packages=packages,
    package_dir=package_dir,
    package_data=package_data,
    author="Matthew D. Cutone",
    author_email="mcutone@opensciencetools.org",
    description=description,
    url="https://github.com/mdcutone/psychopy-crs",
    classifiers=[
        "License :: OSI Approved :: GPL3",
        'Programming Language :: Python :: 3'],
    keywords="psychopy hardware photometer display"
)
