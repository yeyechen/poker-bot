from setuptools import setup, find_packages

setup(
    name="poker-bot",
    version="0.1.0",
    author="Yeye Chen",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "numpy>=1.24.0",
    ],
    python_requires=">=3.11",
)
