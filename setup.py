from distutils.core import setup

setup(
    name='concept_formation',
    version='0.1.0',
    author='Christopher J. MacLellan, Erik Harpstead',
    author_email='maclellan.christopher@gmail.com, whitill29@gmail.com',
    packages=['concept_formation', 'towelstuff.test'],
    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/concept_formation/',
    license='LICENSE.txt',
    description='A library for doing incremental concept formation using algorithms in the COBWEB family',
    long_description=open('README.md').read(),
    install_requires=[],
)