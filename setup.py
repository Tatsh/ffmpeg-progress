from setuptools import setup

setup(name='ffmpeg-progress',
      version='0.0.4',
      author='Andrew Udvare',
      author_email='audvare@gmail.com',
      url='https://github.com/Tatsh/ffmpeg-progress',
      python_requires='>=3.5',
      py_modules=['ffmpeg_progress'],
      description='Get progress information for an ffmpeg process.',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Multimedia :: Sound/Audio :: Conversion',
          'Topic :: Multimedia :: Video',
          'Topic :: Multimedia :: Video :: Conversion',
          'Topic :: Utilities',
      ],
      install_requires=['psutil>=5.6.3'])
