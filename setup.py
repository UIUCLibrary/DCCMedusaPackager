from setuptools import setup

setup(
    name='MedusaPackager',
    version='0.0.1',
    packages=['MedusaPackager', 'scripts', 'tests'],
    entry_points={'console_scripts': ['packagemedusa = scripts.process:main']},
    url='',
    license='',
    author='Henry Borchers',
    author_email='hborcher@illinois.edu',
    description='Script for packaging DCC files for ingesting into Medusa'
)
