from setuptools import setup
from Redy.Tools.Version import Version

# with open('./README.rst', encoding='utf-8') as f:
#     readme = f.read()
readme = ''

version_filename = 'next_version'
with open(version_filename) as f:
    version = Version(f.read().strip())

setup(name='Redy',
      version=str(version),
      keywords='python solution',
      description="an integrated library for module python",
      long_description=readme,
      license='MIT',
      url='https://github.com/thautwarm/Redy',
      author='thautwarm',
      author_email='twshere@outlook.com',
      include_package_data=True,
      install_requires=['bytecode>=0.7'],
      packages=['Redy', 'Redy.Async', 'Redy.Collections', 'Redy.Magic', 'Redy.Tools', 'Redy.ADT', 'Redy.Opt', 'Redy.Opt.builtin_features'],
      platforms='any',
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython'],
      zip_safe=False
      )

version.increment(version_number_idx=2, increment=1)
if version[2] is 42:
    version.increment(version_number_idx=1, increment=1)
if version[1] is 42:
    version.increment(version_number_idx=0, increment=1)

with open(version_filename, 'w') as f:
    f.write(str(version))
