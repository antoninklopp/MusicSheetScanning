from setuptools import setup, find_packages

setup(name="MusicScanning", 
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    packages=find_packages())