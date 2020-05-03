
import setuptools
import json

# Information:
#
# Official tutorial: https://packaging.python.org/tutorials/packaging-projects/
# List of PyPI classifiers: https://pypi.org/classifiers/
#
# If you put your Python module(s) in folder src/, set:
#   packages=setuptools.find_packages('src'),
#   package_dir={'': 'src'}
#

# load contents from various config files
with open('package.json') as fh:
    data = json.load(fh)

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version.txt") as fh:
    version = fh.read().strip()

# check data fields
required = {'name','author','author_email','description','homepage'}
assert required <= data.keys(), ValueError('Missing required field(s).')

# remap field names if needed
data['url'] = data.pop('homepage')

# ------------------------------------------------------------------------

setuptools.setup(
    **data,
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)
