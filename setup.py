from setuptools import find_packages, setup

install_requires = [
    'numpy',
    'posix-ipc',
    'pyarrow',
]

setup(
    name='oremda',
    use_scm_version=True,
    description='Open Reproducible Electron Microscopy Data Analysis',
    long_description='Open Reproducible Electron Microscopy Data Analysis',
    url='https://github.com/OpenChemistry/oremda',
    author='Kitware Inc',
    license='BSD 3-Clause',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(),
    install_requires=install_requires,
)
