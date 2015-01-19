from distutils.core import setup

setup(name='snu-etl-video-downloader',
      version='0.1.0',
      description='Streaming Video Downloader for etl.snu.ac.kr',
      url='https://bitbucket.org/whoknowwhat/snu-etl-video-downloader',
      author='eM',
      author_email='whoknowwhat0623@gmail.com',
      packages=['snu_etl_video_downloader'],
      install_requires=['requests(==2.3.0)',
                        'snulogin(==0.1.0)',
                        'python-librtmp(==0.2.1)'],
      zip_safe=False)
