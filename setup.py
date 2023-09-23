from time import time
import setuptools
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="yymake",
    version="0.1.2",
    author="evilbinary",
    author_email="rootntsd@gmail.com",
    description="A corss build dsl make tool",
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
    package_dir={"": "ymake"},
    packages=setuptools.find_packages(where="ymake"),
    install_requires=[
        'pytest',
        'colorama',
        'networkx', 
        'colorlog'
    ],
    python_requires=">=3.0",
)