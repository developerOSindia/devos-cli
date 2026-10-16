#!/usr/bin/env python3
"""
DeveloperOS Unified CLI (devos)
Setup configuration for local installation and packaging.
"""

from setuptools import setup, find_packages

setup(
    name="devos-cli",
    version="1.0.0",
    description="DeveloperOS Unified Developer CLI - Zero-dependency, ultra-fast developer utilities",
    author="DeveloperOS Team",
    author_email="engineering@developeros.in",
    url="https://developeros.in",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "devos = devos.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
    ],
)
