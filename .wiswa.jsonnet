local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Get progress information for an ffmpeg process.',
  keywords: ['command line', 'ffmpeg'],
  project_name: 'ffmpeg-progress',
  version: '0.0.6',
  want_main: true,
  want_appimage: false,
  want_flatpak: false,
  want_snap: false,
  publishing+: { flathub: 'sh.tat.ffmpeg-progress' },
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
