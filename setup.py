from setuptools import setup
setup(
    packages=['MedusaPackager'],
    entry_points={
        'console_scripts': ['packagemedusa=MedusaPackager.processcli:main']
    },
    test_suite='tests',
)
