# Changelog

## [1.1]

### [1.1.0] - 2021-09-01

#### New features added

- Add username_key as an LTI 1.1 Authenticator configurable [#48](https://github.com/jupyterhub/ltiauthenticator/pull/48) ([@jgwerner](https://github.com/jgwerner))

#### Bugs fixed

- Remove exception when default custom_canvas_user_id argument is not included in LTI 1.1 launch request [#51](https://github.com/jupyterhub/ltiauthenticator/pull/51) ([@jgwerner](https://github.com/jgwerner))
- Fix oauthlib dependency [#37](https://github.com/jupyterhub/ltiauthenticator/pull/37) ([@brospars](https://github.com/brospars))

#### Maintenance and upkeep improvements

- Fix release instructions by reverting to use bump2version [#66](https://github.com/jupyterhub/ltiauthenticator/pull/66) ([@consideRatio](https://github.com/consideRatio))
- Add pyupgrade and prettier to pre-commit, and apply it [#63](https://github.com/jupyterhub/ltiauthenticator/pull/63) ([@consideRatio](https://github.com/consideRatio))
- Use pre-commit.ci to run pre-commit tests [#62](https://github.com/jupyterhub/ltiauthenticator/pull/62) ([@consideRatio](https://github.com/consideRatio))
- docs: initialize read-the-docs based documentation [#61](https://github.com/jupyterhub/ltiauthenticator/pull/61) ([@consideRatio](https://github.com/consideRatio))
- Update release documentation and dependency [#59](https://github.com/jupyterhub/ltiauthenticator/pull/59) ([@jgwerner](https://github.com/jgwerner))
- Rename master to main [#58](https://github.com/jupyterhub/ltiauthenticator/pull/58) ([@consideRatio](https://github.com/consideRatio))
- Update tests workflow [#56](https://github.com/jupyterhub/ltiauthenticator/pull/56) ([@jgwerner](https://github.com/jgwerner))
- Refactor LTI 1.1 validator [#44](https://github.com/jupyterhub/ltiauthenticator/pull/44) ([@jgwerner](https://github.com/jgwerner))
- Add common utility functions for LTI 1.1 and LTI 1.3 [#43](https://github.com/jupyterhub/ltiauthenticator/pull/43) ([@jgwerner](https://github.com/jgwerner))
- Refactor LTI11 source [#41](https://github.com/jupyterhub/ltiauthenticator/pull/41) ([@jgwerner](https://github.com/jgwerner))
- Add pre-commit and formatting tools [#40](https://github.com/jupyterhub/ltiauthenticator/pull/40) ([@jgwerner](https://github.com/jgwerner))

#### Documentation improvements

- Add example LTI 1.1 configuration and readme [#54](https://github.com/jupyterhub/ltiauthenticator/pull/54) ([@jgwerner](https://github.com/jgwerner))
- README: updated k8s example [#52](https://github.com/jupyterhub/ltiauthenticator/pull/52) ([@BenGig](https://github.com/BenGig))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/ltiauthenticator/graphs/contributors?from=2020-12-04&to=2021-08-15&type=c))

[@BenGig](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3ABenGig+updated%3A2020-12-04..2021-08-15&type=Issues) | [@brospars](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Abrospars+updated%3A2020-12-04..2021-08-15&type=Issues) | [@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3AconsideRatio+updated%3A2020-12-04..2021-08-15&type=Issues) | [@jgwerner](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Ajgwerner+updated%3A2020-12-04..2021-08-15&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Ayuvipanda+updated%3A2020-12-04..2021-08-15&type=Issues)

## [1.0]

### [1.0.0] - 2020-12-04

**BREAKING CHANGE**: Log out current user when a new user logs in, reducing confusion about which 'user' is logged in. Multiple 'LTI' users can exist for the same 'human' user - often per-course. This makes sure the 'correct' LTI user is logged in whenever a launch request is clicked, instead of deferring to a previous launch request's LTI user. [#31](https://github.com/jupyterhub/ltiauthenticator/pull/31) ([@U4I-fedir-kryvytskyi](https://github.com/U4I-fedir-kryvytskyi))

#### Bugs fixed

- Log out old user when new user logs in [#31](https://github.com/jupyterhub/ltiauthenticator/pull/31) ([@U4I-fedir-kryvytskyi](https://github.com/U4I-fedir-kryvytskyi))

#### Maintenance and upkeep improvements

- GitHub actions + drop py35 [#33](https://github.com/jupyterhub/ltiauthenticator/pull/33) ([@consideRatio](https://github.com/consideRatio))

#### Contributors to this release

([GitHub contributors page for this release](https://github.com/jupyterhub/ltiauthenticator/graphs/contributors?from=2019-12-11&to=2020-11-12&type=c))

[@consideRatio](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3AconsideRatio+updated%3A2019-12-11..2020-11-12&type=Issues) | [@ptcane](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Aptcane+updated%3A2019-12-11..2020-11-12&type=Issues) | [@U4I-fedir-kryvytskyi](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3AU4I-fedir-kryvytskyi+updated%3A2019-12-11..2020-11-12&type=Issues) | [@welcome](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Awelcome+updated%3A2019-12-11..2020-11-12&type=Issues) | [@yuvipanda](https://github.com/search?q=repo%3Ajupyterhub%2Fltiauthenticator+involves%3Ayuvipanda+updated%3A2019-12-11..2020-11-12&type=Issues)

## [0.4]

### [0.4.0] - 2019-12-11

#### Bugs fixed

- Fix bug about "has no attribute request" if x-forwarded-proto wasn't part of the web request header [#25](https://github.com/jupyterhub/ltiauthenticator/pull/25) ([@consideRatio](https://github.com/consideRatio))
- Bump oauthlib dependency from ==2.\* to >=3.0 to be compatible with JupyterHub 1.0.0 [#24](https://github.com/jupyterhub/ltiauthenticator/pull/24) ([@consideRatio](https://github.com/consideRatio))

#### Maintenance and upkeep improvements

- Add TravisCI and PyPI badges [#27](https://github.com/jupyterhub/ltiauthenticator/pull/27) ([@consideRatio](https://github.com/consideRatio))
- CI/CD update [#26](https://github.com/jupyterhub/ltiauthenticator/pull/26) ([@consideRatio](https://github.com/consideRatio))
- Update Readme with Moodle instructions [#20](https://github.com/jupyterhub/ltiauthenticator/pull/20) ([@rtcn2](https://github.com/rtcn2))
- Remove python 3.4 support [#18](https://github.com/jupyterhub/ltiauthenticator/pull/18) ([@yuvipanda](https://github.com/yuvipanda))
- Link to Canvas' external app docs. [#15](https://github.com/jupyterhub/ltiauthenticator/pull/15) ([@ryanlovett](https://github.com/ryanlovett))

## [0.3]

### [0.3.0]

This is the projects first release on GitHub even though there was some releases
to PyPI. A lot of work was put in by pushing directly to the master branch. For
a full list of changes only the commit history will do justice.

#### Merged PRs

- Canvas ID Authentication [#7](https://github.com/jupyterhub/ltiauthenticator/pull/7) ([@samhinshaw](https://github.com/samhinshaw))
- Canvas Implementation Instructions [#6](https://github.com/jupyterhub/ltiauthenticator/pull/6) ([@samhinshaw](https://github.com/samhinshaw))
- Add support for forwarded protocol in headers (reverse_proxy) [#5](https://github.com/jupyterhub/ltiauthenticator/pull/5) ([@brospars](https://github.com/brospars))
