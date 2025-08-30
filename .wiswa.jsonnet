local utils = import 'utils.libjsonnet';

(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Get progress information for an ffmpeg process.',
  keywords: ['command line', 'ffmpeg'],
  project_name: 'ffmpeg-progress',
  version: '0.0.5',
  want_main: true,
  copilot: {
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
      poetry+: {
        dependencies+: {
          psutil: '^7.0.0',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': '^7.0.0.20250601',
            },
          },
        },
      },
    },
  },
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
