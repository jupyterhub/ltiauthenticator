from setuptools import setup, find_packages

setup(
    name='jupyterhub-ltiauthenticator',
    version='1.0.0',
    description='JupyterHub authenticator implementing LTI v1',
    url='https://github.com/yuvipanda/jupyterhub-ltiauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'jupyterhub>=0.8',
        'oauthlib>=3.0'
    ]
)
