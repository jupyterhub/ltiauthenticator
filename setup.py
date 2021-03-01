import os
import sys

from setuptools import setup, find_packages


# setup logic from github.com/jupyterhub/jupyterhub
v = sys.version_info
if v[:2] < (3, 6):
    error = "ERROR: LTIAuthenticator requires Python version 3.6 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

# Get the current package version.
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join("_version.py")) as f:
    exec(f.read(), {}, version_ns)


setup(
<<<<<<< HEAD
    name="jupyterhub-ltiauthenticator",
    version="1.0.1.dev",
    description="JupyterHub authenticator implementing LTI v1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jupyterhub/ltiauthenticator",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    license="3 Clause BSD",
    packages=find_packages(exclude="./tests"),
    python_requires=">=3.6",
    install_requires=["jupyterhub>=0.8", "oauthlib>=3.1", "escapism>=1.0"],
    package_data={
        "": ["*.html"],
    },  # noqa: E231
=======
    name='jupyterhub-ltiauthenticator',
    version='1.0.0',
    description='JupyterHub authenticator implementing LTI v1.1 / v1.3',
    url='https://github.com/jupyterhub/ltiauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        'josepy==1.4.0',
        'jupyterhub>=1.3.0',
        'jwcrypto==0.8',
        'oauthlib>=3.0',
        'oauthenticator>=0.13.0',
        'pem==20.1.0',
        'pycryptodome==3.9.8',
        'PyJWT==1.7.1',
        'pyjwkest==1.4.2',
    ]
>>>>>>> first commit of wip
)
