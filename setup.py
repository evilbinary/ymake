from time import time
import setuptools
import os,sys,re

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="yymake",
    version="0.8.5",
    author="evilbinary",
    author_email="rootntsd@gmail.com",
    description="A cross build dsl make tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evilbinary/ymake",
    project_urls={
        "Bug Tracker": "https://github.com/evilbinary/ymake/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ya = yaya:process',
            'yaya = yaya:process',
            'ymake = yaya:process',
            'yymake = yaya:process',
        ],
    },
    package_dir={"": "ymake"},
    packages=["."],
    install_requires=[
        'pytest',
        'colorama',
        'networkx', 
        'colorlog',
        'diskcache'
    ],
    python_requires=">=2.6",
)