from setuptools import find_packages
from setuptools import setup


setup(
    name="jupyterhub-ltiauthenticator",
    version="1.3.0",
    description="JupyterHub authenticator implementing LTI v1.1 and LTI v1.3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jupyterhub/ltiauthenticator",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    license="3 Clause BSD",
    packages=find_packages(exclude="./tests"),
    python_requires=">=3.6",
    install_requires=[
        "escapism>=1.0",
        "josepy>=1.4.0",
        "jupyterhub>=1.2",
        "jwcrypto>=0.8",
        "oauthlib>=3.1",
        "oauthenticator>=0.13.0",
        "pem>=20.1.0",
        "pycryptodome>=3.9.8",
        "PyJWT>=1.7.1,<2",
        "pyjwkest>=1.4.2",
    ],
    package_data={
        "": ["*.html"],
    },  # noqa: E231
)
