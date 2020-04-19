
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nxp",
    version="0.1.0",
    author="Jonathan Hadida",
    author_email="jonathan.hadida@unknown.invalid",
    description="Natural eXpression Parsing — A Python 3 parsing library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jhadida/nxp",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
)
