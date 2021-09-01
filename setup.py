from setuptools import find_packages
from setuptools import setup


setup(
    name="jupyterhub-ltiauthenticator",
    version="1.1.1.dev",
    description="JupyterHub authenticator implementing LTI v1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jupyterhub/ltiauthenticator",
    author="Yuvi Panda",
    author_email="yuvipanda@gmail.com",
    license="3 Clause BSD",
    packages=find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "josepy==1.4.0",
        "jupyterhub>=1.3.0",
        "jwcrypto==0.8",
        "jwt==1.2.0",
        "oauthlib>=3.0",
        "oauthenticator>=0.13.0",
        "pem==20.1.0",
        "pycryptodome==3.9.8",
        "PyJWT==1.7.1",
        "pyjwkest==1.4.2",
    ],
)
