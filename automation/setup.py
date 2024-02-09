from setuptools import setup, find_packages

VERSION = "0.0.1"
DESCRIPTION = "Automated generation of an PMIC for SKY130"
LONG_DESCRIPTION = "Automated generation of an PMIC for SKY130"

setup(
    name="pmicgen",
    version=VERSION,
    author="AC3E (Mario Romero)",
    author_email="mario@1159.cl",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    entry_points={"console_scripts": ["pmicgen = cli.main:main"]},
)
