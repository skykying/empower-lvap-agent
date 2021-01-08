import setuptools

exec(open('control/version.py').read())

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="unimon-ctl",
  keywords="unikernel clickos unimon",
  version=__version__,
  author="Will Fantom",
  author_email="w.fantom@lancaster.ac.uk",
  description='Control ClickOS Domains (and get unimon data)',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/willfantom/unimon-ctl",
  packages=setuptools.find_packages(),
  classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
    ],
  install_requires=['pyxs'],
  entry_points={
    'console_scripts': [
        'unimon-ctl=control.cli:main',
        'clickos-ctl=control.cli:main'
    ],
  },
  python_requires='>=3.6',
)