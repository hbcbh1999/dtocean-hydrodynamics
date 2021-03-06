# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

- Added change log.
- Added continuous integration configuration files.

### Fixed

- Numerous PEP8 fixes.
- Tidal module velocity profile generator switched to Manning's formulation as
  was incorrectly set to the Soulsby type.
- Fixed bugs in the array layout optimiser code.
- Fixed bug in calculation of device depths for wave module approximation test.
- Fixed depreciation warning when sending arguments to setup.py test.
- Refactored distance_from_streamline to improve readability.
- Fixed issues with using non-rectangular domain in the tidal module.
- Fixed issues determining depth excluded zones with non-rectangular domains.
- NaNs are now set to zero in interp_at_point and edge cases are better
  handled.

### Changed

- Changed wave modules mean power output per device to return actual power
  generated rather than the sum of all powers accross the power matrix.
- Optimised EnergyProduction function by reducing number of calls to
  block_diag. This has provided a one third reduction in run times.

## [1.0.0] - 2017-01-05

### Added

- Initial import of dtocean-core from SETIS.
