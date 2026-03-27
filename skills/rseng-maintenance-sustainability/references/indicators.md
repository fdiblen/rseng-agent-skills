<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills
     pipeline from the configured content sources; see extensions/. -->

# Quality indicator checklist

Check each indicator that applies; judge applicability by the
software's tier (analysis code, prototype tool, infrastructure).

## Compatibility

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.

## FAIRness

- [ ] Software has releases (`has_releases`)
      To enable collaborative review, the project's source repository MUST include interim versions for review between releases; it MUST NOT include only final releases. This indicator determines if a software project has releases. This can be achieved by looking for tags or using software that retrieves related data.
- [ ] Software has up-to-date metadata (`metadata_is_up_to_date`)
      Metadata information reflects the current description of a software project. This indicator ensures that the current project metadata provides up to date, accurate and relevant information about a software component.
- [ ] Software has documentation (`software_has_documentation`)
      This indicator aims to determine if a software project comes with many forms of documentation like readme or readthedocs
- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.
- [ ] Software follows versioning standards (`versioning_standards_use`)
      This indicator aims to determine if the version (or versions) of a software tool follows an established community convention like semantic versioning (SemVer) or calendar versioning (CalVer).

## Interaction Capability

- [ ] Software has documentation (`software_has_documentation`)
      This indicator aims to determine if a software project comes with many forms of documentation like readme or readthedocs

## Maintainability

- [ ] Software has continuous integration tests (`has_ci-tests`)
      This indicator aims to determine if the project runs tests before pull requests are merged.
- [ ] Software has releases (`has_releases`)
      To enable collaborative review, the project's source repository MUST include interim versions for review between releases; it MUST NOT include only final releases. This indicator determines if a software project has releases. This can be achieved by looking for tags or using software that retrieves related data.
- [ ] Software has up-to-date metadata (`metadata_is_up_to_date`)
      Metadata information reflects the current description of a software project. This indicator ensures that the current project metadata provides up to date, accurate and relevant information about a software component.
- [ ] Software has ci/cd workflows in its repository (`repository_workflows`)
      This indicator tries aims determine if a software project makes use of workflows to automate processes like testing and deployment.
- [ ] Software provides issue tracking (`support_issue_tracking`)
      The software project offers an accessible issue tracking system (e.g., GitHub/GitLab Issues or a helpdesk) that is used to report, document, and manage bugs, enhancement requests, and user-facing operational issues.

## Reliability

- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.

## Security

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.

## Sustainability

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.
