from setuptools import setup


setup(
    name='groupkit-app-engine',
    version='1.0.0',
    license='MIT',
    author='Grow Authors',
    author_email='hello@grow.io',
    packages=[
        'groupkit',
    ],
    install_requires=[
        'flask',
        'google-api-python-client',
        'google-auth',
        'google-cloud-ndb',
        'requests-oauthlib',
        'urllib3',
    ],
)
