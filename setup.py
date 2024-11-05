from setuptools import setup, find_packages

setup(
    name='vvmtools',
    version='1.0.0',
    author='Aaron Hsieh, Shao-Yu Tseng',
    author_email='R12229025@ntu.edu.tw',
    description="This is a package for VVM simulation data loading, analysis, and plotting.",
    url="https://github.com/Aaron-Hsieh-0129/VVMTools.git",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'xarray',
        'netCDF4',
        'matplotlib',
    ],

)
