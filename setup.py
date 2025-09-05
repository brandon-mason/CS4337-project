#!/usr/bin/env python3
"""
Setup script for the Computer Vision Sheet Music Player project.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="CS4337-project",
    version="1.0.0",
    author="Computer Vision Project",
    description="A computer vision-based sheet music player using OpenCV",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/brandon-mason/CS4337-project",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "CS4337-project=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="computer-vision, music, sheet-music, midi, opencv, midi",
    project_urls={
        "Source": "https://github.com/brandon-mason/CS4337-project",
        "Documentation": "https://github.com/brandon-mason/CS4337-project#readme",
    },
)
