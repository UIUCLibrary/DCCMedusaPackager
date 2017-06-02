from setuptools import setup
import MedusaPackager
setup(
    name=MedusaPackager.__title__,
    version=MedusaPackager.__version__,
    packages=['MedusaPackager'],
    entry_points={
        'console_scripts': ['packagemedusa=MedusaPackager.processcli:main']
    },
    url=MedusaPackager.__version__,
    zip_safe=False,
    test_suite='tests',
    license='',
    author=MedusaPackager.__author__,
    author_email=MedusaPackager.__author_email__,
    description=MedusaPackager.__description__,
)
