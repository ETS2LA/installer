import sys
import os
from setuptools import setup

pkg_name = 'DearPyGui_Markdown'
version = '1.0.2'


def list_dir_all(top_dir='.'):
    for root, dirs, files in os.walk(top_dir):
        for dir_ in dirs:
            yield os.path.abspath(os.path.join(root, dir_))
        for file in files:
            yield os.path.abspath(os.path.join(root, file))


with open('requirements.txt') as f:
    install_requires = [line for line in f.read().splitlines() if line and not line.startswith('#')]
data_filenames = [os.path.relpath(filename, pkg_name)
                  for filename in list_dir_all(pkg_name)
                  if '__pycache__' not in filename]
sys.argv += ['bdist_wheel']

setup(
    name=pkg_name,
    version=version,
    description='',
    long_description='',
    long_description_content_type='text/markdown',
    author='IvanNazaruk',
    author_email='',
    packages=[pkg_name],
    package_data={pkg_name: data_filenames},
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=install_requires,
    license='MIT'
)
