from setuptools import setup, find_packages


setup(name='prune-requirements',
      version='1.0',
      author='Evan Klitzke',
      author_email='evan@eklitzke.org',
      description='try to prune requirements.txt files',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'prune-requirements = prune_requirements.app:main'
          ]})
