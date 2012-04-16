import sys
from setuptools import setup, find_packages

version = '0.1'

deps = ['hgapi >= 1.0.1']

# we only support python 2.6+ right now
assert sys.version_info[0] == 2
assert sys.version_info[1] >= 6

setup(name='w3cRunner',
      version=version,
      description='mirror for mozilla and w3c testing files',
      long_description="",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Sam Garrett',
      author_email='samdgarrett@gmail.com',
      url='https://github.com/ctalbert/w3c_testmirror/',
      license='MPL',
      dependency_links = [
         "http://pypi.python.org/packages/source/h/hgapi/hgapi-1.0.1.zip"
      ],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      runtps = tps.cli:main
      w3cRunner = w3cRunner:main
      """,
      data_files=[
        ('w3cRunner', ['config/config.json.in']),
      ],
      )
