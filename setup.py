"""Package setup for PyFORC."""
import setuptools

setuptools.setup(
    name="PyFORC",
    version="1.1.1",
    author="Peyton Murray",
    author_email="peynmurray@gmail.com",
    description="FORC analysis in Python",
    url="https://github.com/peytondmurray/pyforc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "scipy",
        "pytest",
        "coverage",
    ]
)
