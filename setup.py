from setuptools import setup

setup(
    name='DCCMedusaPackager',
    version='0.0.1',
    packages=['MedusaPackager', 'scripts', 'tests'],
    entry_points={
        'console_scripts': ['packagemedusa=process:main']
    },
    url='https://github.com/UIUCLibrary/DCCMedusaPackager',
    scripts=['scripts/processcli.py'],
    zip_safe=False,
    test_suite='tests',
    license='',
    author='Henry Borchers',
    author_email='hborcher@illinois.edu',
    description='Script for packaging DCC files for ingesting into Medusa',
)
