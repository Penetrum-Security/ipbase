from setuptools import setup, find_packages


setup(
    name='ipbase',
    version="0.1",
    license="GPLv3",
    author="Penetrum LLC",
    author_email="contact@penetrum.com",
    description="Bad IP lookup tool",
    scripts=['ipbase'],
    install_requires=open("requirements.txt").read().split("\n")
)


