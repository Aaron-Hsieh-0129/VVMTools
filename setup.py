from setuptools import setup, find_packages

setup(
    name='vvmtools',
    version='0.1.0',
    description='A collection of tools for VVM simulation data loading and analysis.',
    author='Aaron Hsieh',
    author_email='R12229025@ntu.edu.tw',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'xarray',
        'netCDF4',
        'matplotlib',
    ],
)
