# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.3.6] - 2024-02-14

## [v0.3.6] - 2024-02-14

## [v0.3.6] - 2024-02-14

## [v0.3.6] - 2024-02-14

## [v0.3.3] - 2024-02-14

## [v0.3.3] - 2024-02-14
### Fixed
- Fixed images in README for PyPi description

## [v0.3.5] - 2023-09-28
### Fixed
- Added support for expiry date in security object.

## [v0.3.4] - 2023-09-05
### Added
- Add Annotations API as a service

### Security
- Bump certifi minimum version to 2023.7.22

## [v0.3.3] - 2023-06-28
### Fixed
- Fixed a bug where non-ASCII characters are escaped which causes `Signature Mismatch` this is resolved by setting `ensure_ascii=False`.

### Security
- Upgraded signature to match the security standard.

### Security
- Update dependencies

## [v0.3.2] - 2020-01-08
### Fixed
- Removed the explicit dependency on `urllib3` as we do not use it directly.
- Updated testing commands and dependency declaration to remove deprecated uses
  of setuptool's `tests_require` configuration and `test` command.

### Added
- Started active support for Python 3.7--3.9

### Changed
- Dropped support for EoLed Python<3.6

### Removed
- Python 2.7 compat code

## [v0.3.1] - 2019-08-07
### Fixed
- Fixed an issue where the `DataApi` class's `results_iter` method would return no data 
  when receiving responses from Data API endpoints that set the "`data`" field of the
  response to an object (like the [itembank/questions endpoint](https://reference.learnosity.com/data-api/endpoints/itembank_endpoints#getQuestions) 
  when `item_references` is included in the request).

## [v0.3.0] - 2019-06-17
### Added
- This ChangeLog!
- Example code
- Add better context to `DataApiException`
- Telemetry support

### Security
- Bump requests to 2.21.0 (CVE-2018-18074)
- Bump urllib3 to 1.24.3 (CVE-2018-20060, CVE-2019-11324)

## [v0.2.0] - 2018-10-17
### Added
- utils.Uuid
