# [1.0]

## [1.0.0]

### Merged PRs

* **BREAKING CHANGE**:   Log out current user when a new user logs in, reducing confusion about which 'user' is logged in. Multiple 'LTI' users can exist for the same 'human' user - often per-course. This makes sure the 'correct' LTI user is logged in whenever a launch request is clicked, instead of deferring to a previous launch request's LTI user. [#31](https://github.com/jupyterhub/ltiauthenticator/pull/31) ([@U4I-fedir-kryvytskyi](https://github.com/U4I-fedir-kryvytskyi))

# [0.4]

## [0.4.0]

### Merged PRs

#### Fixes
* Fix bug about "has no attribute request" if x-forwarded-proto wasn't part of the web request header [#25](https://github.com/jupyterhub/ltiauthenticator/pull/25) ([@consideRatio](https://github.com/consideRatio))
* Bump oauthlib dependency from ==2.* to >=3.0 to be compatible with JupyterHub 1.0.0 [#24](https://github.com/jupyterhub/ltiauthenticator/pull/24) ([@consideRatio](https://github.com/consideRatio))

#### Maintenance
* Add TravisCI and PyPI badges [#27](https://github.com/jupyterhub/ltiauthenticator/pull/27) ([@consideRatio](https://github.com/consideRatio))
* CI/CD update [#26](https://github.com/jupyterhub/ltiauthenticator/pull/26) ([@consideRatio](https://github.com/consideRatio))
* Update Readme with Moodle instructions [#20](https://github.com/jupyterhub/ltiauthenticator/pull/20) ([@rtcn2](https://github.com/rtcn2))
* Remove python 3.4 support [#18](https://github.com/jupyterhub/ltiauthenticator/pull/18) ([@yuvipanda](https://github.com/yuvipanda))
* Link to Canvas' external app docs. [#15](https://github.com/jupyterhub/ltiauthenticator/pull/15) ([@ryanlovett](https://github.com/ryanlovett))

# [v0.3]
This is the projects first release on GitHub even though there was some releases
to PyPI. A lot of work was put in by pushing directly to the master branch. For
a full list of changes only the commit history will do justice.

### Merged PRs
* Canvas ID Authentication [#7](https://github.com/jupyterhub/ltiauthenticator/pull/7) ([@samhinshaw](https://github.com/samhinshaw))
* Canvas Implementation Instructions [#6](https://github.com/jupyterhub/ltiauthenticator/pull/6) ([@samhinshaw](https://github.com/samhinshaw))
* Add support for forwarded protocol in headers (reverse_proxy) [#5](https://github.com/jupyterhub/ltiauthenticator/pull/5) ([@brospars](https://github.com/brospars))
