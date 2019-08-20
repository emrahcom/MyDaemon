from setuptools import setup

setup(
    name='mydaemon',
    version='0.1.10',
    packages=['mydaemon'],
    description='Python daemon module',
    url = 'https://github.com/emrahcom/MyDaemon',
    author = 'emrah',
    author_email = 'emrah.com@gmail.com',
    license='MIT',
    keywords = 'daemon daemonize background service fork',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
