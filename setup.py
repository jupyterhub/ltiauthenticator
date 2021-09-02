from setuptools import find_packages
from setuptools import setup


setup(
    name="jupyterhub-ltiauthenticator",
    version="1.2.0",
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
)
