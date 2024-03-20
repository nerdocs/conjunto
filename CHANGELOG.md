# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.21] - 2024-03-21
- use gettext_lazy for model translations
- rename conjunto migration 0003 to proper name

## [0.0.20] - 2024-03-21
### Fixes
- add missing data files

## [0.0.19] - 2024-03-21
- switch build tool from flit to setuptools
- gitignore mo files
- add menu check for anonymous

## [0.0.18] - 2024-03-13
### Added
- Token helper views
- variable icon font sizes in button components

## [0.0.17] - 2024-03-08
- update HtmxLinkElement

## [0.0.16] - 2024-03-05
- add HTMX lightbox
- disable modal form button when posting
- enable htmx spinner
- rebase HtmxSetModelAttributeView on SuccessEventMixin

## [0.0.15] - 2023-02-29
- add datagrid-item component
- improve "static" page views

## [0.0.14] - 2023-02-28
- fix issues with tabler https://github.com/tabler/tabler/issues/1836
- breaking: rename required_permissions attribute to permission_required in IMenuItems
- improve link functionality

## [0.0.13] - 2023-02-27
### Added
- let listitem component accept subtitle slot additionally to attribute
- allow autocomplete and custom form attrs in ModalFormViews
- provide function to generate secure passwords
- add helper functions for menus: is_staff, is_authenticated
### Changed
- breaking change of HTMX mixin names to better explain their purpose
- rename "Site Editor" permissions group to "Content Editor"

## [0.0.12] - 2023-02-23
### Added
- protected media files download support

## [0.0.11] - 2023-02-21
- improve updatable component

## [0.0.10] - 2023-02-19
### Added
- another fixes for HTMX form handling and redirects

## [0.0.9] - 2023-02-19
### Added
- allow auto img tags in datagrids
- fixes for HTMX form handling and redirects

## [0.0.8]
- fix error with LicensePage

## [0.0.7]
- fix PRODUCTION env variable for red background bar

## [0.0.6]
- mark testing sites with read header bar
- rename GDAPS based "component" to "element" to avoid name clashes with django-web-components
- massively improve element rendering
- begin adding some tabler components: list, (action)buttons, etc.
- migrate some more helper classes from medux-common

## [0.0.5] 2023-12-23
- update translations
- move CMS functionality in own subapp `conjunto.cms`

## [0.0.4] 2023-12-23
### Fixed
- maintenance mode

### Changed
- rename maintenance_text to maintenance_content

## [0.0.3]
### Added
- documentation at readthedocs
- many small bugfixes

## [0.0.2]
### Added
- move many common used classes + helpers from medux-common to Conjunto
- Makefile for common tasks 

## [0.0.1]
- initial version

