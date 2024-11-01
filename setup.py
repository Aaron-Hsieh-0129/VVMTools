from setuptools import setup, find_packages

setup(
    name='vvmtools',
    version='1.0.0',
    description='A collection of tools for VVM simulation data loading, analysis, and plotting.',
    author='Aaron Hsieh, Shao-Yu Tseng',
    author_email='R12229025@ntu.edu.tw',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'xarray',
        'netCDF4',
        'matplotlib',
    ],
)
