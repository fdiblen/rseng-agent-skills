<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills
     pipeline from RSQKit content; see pipeline/upstream.lock. -->

# Quality indicator checklist

Check each indicator that applies; judge applicability by the
software's tier (analysis code, prototype tool, infrastructure).

## FAIRness

- [ ] All tests defined by the software component pass (`passed_tests_ok`)
      The software tool passes all the tests provided within its own repository.
- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.

## Functional suitability

- [ ] All tests defined by the software component pass (`passed_tests_ok`)
      The software tool passes all the tests provided within its own repository.
- [ ] Software has sufficient test coverage (`software_test_coverage`)
      Indicates that the test suite covers most (or ideally all) the code branches, input fields, and functionality

## Maintainability

- [ ] Software has continuous integration tests (`has_ci-tests`)
      This indicator aims to determine if the project runs tests before pull requests are merged.

## Reliability

- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.
- [ ] Software has sufficient test coverage (`software_test_coverage`)
      Indicates that the test suite covers most (or ideally all) the code branches, input fields, and functionality
