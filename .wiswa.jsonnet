local utils = import 'utils.libjsonnet';

{
  description: 'Get progress information for an ffmpeg process.',
  keywords: ['command line', 'ffmpeg'],
  project_name: 'ffmpeg-progress',
  version: '0.0.5',
  want_main: true,
  copilot+: {
    intro: 'ffmpeg-progress is a command line utility and library to get progress information for a newly created ffmpeg process.',
  },
  pyproject+: {
    project+: {
      classifiers+: [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
      ],
    },
    tool+: {
      coverage+: {
        report+: { omit+: ['typing.py'] },
        run+: { omit+: ['typing.py'] },
      },
      poetry+: {
        dependencies+: {
          psutil: utils.latestPypiPackageVersionCaret('psutil'),
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': utils.latestPypiPackageVersionCaret('types-psutil'),
            },
          },
        },
      },
    },
  },
}
