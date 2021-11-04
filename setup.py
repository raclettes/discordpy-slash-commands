from os import path
from setuptools import setup

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(path.abspath(path.dirname(__file__)), 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.readlines()

setup(name='dpyslash',
      version='1.2.2',
      description='Improves slash commands for Python',
      author='starsflower',
      url='https://github.com/starsflower/discordpy-slash-commands',
      license="MIT",
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
      ],
      packages=['pyslash'],
      package_dir={'pyslash': './pyslash'},
      install_requires=install_requires,

      # Description
      long_description=long_description,
      long_description_content_type='text/markdown'
)
