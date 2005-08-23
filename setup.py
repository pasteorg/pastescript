from setuptools import setup, find_packages

version = '0.1'

setup(
    name="PasteScript",
    version=version,
    description="A pluggable command-line frontend to commands for Paste applications",
    long_description="""\
See also the `Subversion repository <http://svn.pythonpaste.org/Paste/Script/trunk#egg=Paste-Script-%sdev>`_
""" % version,
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Python Software Foundation License",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    keywords='web wsgi application framework command-line framework',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/script/script.html",
    namespace_packages=['paste'],
    packages=find_packages(exclude='tests'),
    zip_safe=True,
    )
