from setuptools import setup, find_packages

setup(
    name='paladin_ire',
    description='a from-scratch python roguelike built in curses',
    url='https://pokeybill.us/paladin_ire',
    author='Bill (pokeybill) Normandin',
    author_email='bill@pokeybill.us',
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Topic :: Games/Entertainment :: Role-Playing'
        ],
    py_modules=['paladin_ire'],
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        paladin_ire=paladin_ire
        """,
)
