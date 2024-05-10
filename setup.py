from setuptools import setup, find_packages

setup(
    name='DupCheck',
    version='0.1.1',
    author='Kirill Krasnoshchekov',
    author_email='krvkir@gmail.com',
    description='Set a central dir, index it and check any file against this dir.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/krvkir/dupcheck',
    packages=find_packages(),
    install_requires=[
        # List your project's dependencies here, e.g.,
        # 'requests>=2.23.0',
    ],
    classifiers=[
        # Choose classifiers from https://pypi.org/classifiers/
        # 'Development Status :: 3 - Alpha',
        # 'Intended Audience :: Developers',
        # 'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3',
        'Programming Language :: Python :: 3',
    ],
    keywords='deduplication hashing',  # Keywords that define your package best
    python_requires='>=3.6',
    # entry_points={
    #     'console_scripts': [
    #         'yourscript=yourpackage.module:function',
    #     ],
    # },
)
