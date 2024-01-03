from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'Automated generation of an LDO for SKY130'
LONG_DESCRIPTION = 'Automated generation of an LDO for SKY130'

setup(
        name="LDOCAC", 
        version=VERSION,
        author="AC3E (Mario Romero)",
        author_email="mario@1159.cl",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages()
)