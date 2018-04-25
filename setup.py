from setuptools import setup


setup(
    name='groupkit-app-engine',
    version='0.1.0',
    license='MIT',
    author='Grow Authors',
    author_email='hello@grow.io',
    packages=[
        'groupkit',
    ],
    install_requires=[
        'requests-oauthlib',
        'google-auth',
        'flask',
        'google-api-python-client',
        'urllib3',
    ],
)
