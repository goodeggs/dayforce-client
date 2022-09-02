import setuptools


def get_version():
    version = {}
    with open("dayforce_client/version.py") as fp:
        exec(fp.read(), version)
    return version["__version__"]


with open("README.md", "r") as f:
    readme = f.read()


setuptools.setup(
    name="dayforce_client",
    author="David Wallace",
    author_email="david.wallace@goodeggs.com",
    version=get_version(),
    url="https://github.com/goodeggs/dayforce_client",
    description="A python client for typed interactions with the Dayforce API.",
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "Topic :: Software Development",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="dayforce python",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "requests",
        "attrs",
        "pysftp",
        "paramiko",
        "cryptography",
    ],
    python_requires=">=3.6",
)
