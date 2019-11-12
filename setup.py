import os
from setuptools import setup, find_packages


setup(
    name='acaicli',
    version='0.1',
    description='Acai System CLI',
    url='https://github.com/acai-systems/acaicli',
    author='Chang Xu',
    author_email='changx@andrew.cmu.edu',
    license='MIT',
    packages=find_packages(),
    scripts=['acaicli/acai'],
    include_package_data=True,
    dependency_links=['git+https://github.com/acai-systems/acaisdk'],
    zip_safe=True
)
