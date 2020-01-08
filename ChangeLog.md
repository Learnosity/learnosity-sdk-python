# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.3.2] - 2020-01-08
### Fixed
- Removed the explicit dependency on `urllib3` as we do not use it directly.
- Updated testing commands and dependency declaration to remove deprecated uses
  of setuptool's `tests_require` configuration and `test` command.

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
- Add better context to `DataApiException`s
- Telemetry support

### Security
- Bump requests to 2.21.0 (CVE-2018-18074)
- Bump urllib3 to 1.24.3 (CVE-2018-20060, CVE-2019-11324)


## [v0.2.0] - 2018-10-17
### Added
- utils.Uuid
