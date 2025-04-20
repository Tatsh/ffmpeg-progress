local utils = import 'utils.libjsonnet';

local utils = import 'utils.libjsonnet';

(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Get progress information for an ffmpeg process.',
  keywords: ['command line', 'ffmpeg'],
  project_name: 'ffmpeg-progress',
  version: '0.0.5',
  want_main: true,
  citation+: {
    'date-released': '2025-04-16',
  },
  pyproject+: {
    project+: {
      classifiers+: [
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
      ],
    },
    tool+: {
      poetry+: {
        dependencies+: {
          click: '^8.1.8',
          psutil: '^7.0.0',
        },
        group+: {
          dev+: {
            dependencies+: {
              'types-psutil': '^7.0.0.20250401',
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
