<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills
     pipeline from RSQKit content; see pipeline/upstream.lock. -->

# Quality indicator checklist

Check each indicator that applies; judge applicability by the
software's tier (analysis code, prototype tool, infrastructure).

## Community

- [ ] Project has active communication channels (`has_active_communication_channels`)
      The project has communication channels (i.e. Slack, Gitter, etc.) where users and developers can discuss project-related matters and also be up to date with updates, notices and other relevant information.
- [ ] Project has active contributors beyond core maintainers (`has_active_contributors`)
      Contributions and/or other additions/updates to the project aren't centralised on only the core maintainers, but also other contributors.
- [ ] Software repository has contribution guidelines (`has_contribution_guidelines`)
      The software repository provides contribution guidelines in case someone wants to contribute to the project.
- [ ] Responses to issues and/or pull requests are done within a defined timeframe (`response_timeframe_ok`)
      The maintainers of the project's repository respond to issues and/or pull requests within a defined time frame that follows the related community's conventions.

## Compatibility

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.

## FAIRness

- [ ] Software is archived in a scholarly repository (`archived_in_scholarly_repository`)
      The source code repository is archived in a scholarly repository (e.g Zenodo, HAL) to ensure that software can be found and accessed in a scholarly context.
- [ ] Software is archived in Software Heritage (`archived_in_software_heritage`)
      The source code repository is found in the universal source code archive, Software Heritage, to ensure long-term access to the full development history.
- [ ] The documentation coverage for the codebase follows community conventions (`code_documentation_coverage_ok`)
      This check tries to determine if the project's codebase is mostly documented according according to community conventions and standards (i.e. docstrings).
- [ ] CodeMeta completeness (`codemeta_completeness`)
      This indicator checks that the codemeta file is sufficiently complete (according to community expectations). That is, the percentage of properties that are filled with metadata is above an acceptable threshold established by a target community. This indicator does not assess the quality of the metadata fields available.
- [ ] Software has descriptive metadata (`descriptive_metadata`)
      This indicator aims to determine if a software component comes with descriptive metadata that provides information. This includes, but is not limited to: name, domain, programming language, date created, date of first publication, keywords, related links, etc..
- [ ] Software has no linting issues (`has_no_linting_issues`)
      The project addresses or resolves warnings identified by compilers, safe modes, or linters.
- [ ] Software has releases (`has_releases`)
      To enable collaborative review, the project's source repository MUST include interim versions for review between releases; it MUST NOT include only final releases. This indicator determines if a software project has releases. This can be achieved by looking for tags or using software that retrieves related data.
- [ ] Software is listed in a registry (`listed_in_registry`)
      The target source code repository is in a disciplinary or community registry (e.g ascl.net, bio.tools, swMath, RRID portal, RSD, WikiData, DataCite, etc.) to ensure that software can be found and accessed.
- [ ] Software has up-to-date metadata (`metadata_is_up_to_date`)
      Metadata information reflects the current description of a software project. This indicator ensures that the current project metadata provides up to date, accurate and relevant information about a software component.
- [ ] All tests defined by the software component pass (`passed_tests_ok`)
      The software tool passes all the tests provided within its own repository.
- [ ] Software has persistent and unique identifier (`persistent_and_unique_identifier`)
      This indicator tries to determine if the software identifier is based on a suitable identifier scheme, and test it can be resolved. This is done by checking if the identifier uses an identifier scheme contained in a list of globally unique identifier schemes
- [ ] Software specifies requirements (`requirements_specified`)
      This indicator tries to determine if the project specifies what is required to use the software.
- [ ] Software uses citation (`software_has_citation`)
      This indicator aims to determine if the project uses a citation to reference contributors and authors (e.g., through a CFF file, in the README, etc).
- [ ] Software has documentation (`software_has_documentation`)
      This indicator aims to determine if a software project comes with many forms of documentation like readme or readthedocs
- [ ] Software has license (`software_has_license`)
      This check tries to determine if the project has published a license
- [ ] Software uses an appropriate license for different file types (`software_has_license_for_file_types`)
      This indicator determines if the project has an appropriate licenses for its different file types (e.g., documentation, images, code, tests, etc.). The REUSE specification defines good practices for accomplishing this task.
- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.
- [ ] The project's repository includes a container build file (`software_is_containerized`)
      The project's repository where its source code is hosted includes a container build file to containerize it (i.e. Dockerfile, Podman, Apptainer, etc.).
- [ ] Software uses a tool for warnings or mistakes (`uses_tool_for_warnings_and_mistakes`)
      This indicator checks that the project enables one or more compiler warning flags, a "safe" language mode, or uses a separate "linter" tool to look for code quality errors or common simple mistakes, if there is at least one FLOSS tool that can implement this criterion in the selected language.
- [ ] Software makes use of version control (`version_control_use`)
      This indicator aims to determine if a software project uses version control.
- [ ] Software follows versioning standards (`versioning_standards_use`)
      This indicator aims to determine if the version (or versions) of a software tool follows an established community convention like semantic versioning (SemVer) or calendar versioning (CalVer).

## Flexibility

- [ ] Software is published as a downloadable package (`has_published_package`)
      This indicator aims to determine if a software project is published as a downloadable package.
- [ ] Software specifies requirements (`requirements_specified`)
      This indicator tries to determine if the project specifies what is required to use the software.

## Functional suitability

- [ ] Has a measure of functional correctness (`functional_correctness`)
      For analysis code specifically, is there a quantifiable measure of the functional correctness of the software output. This indicator focuses on computational/statistical correctness. For example, in an ML model software context, the indicator measures whether the repository reports metrics like Accuracy, F1-score, or ROC-AUC to prove the model performs as intended. However other performance metrics may also address the indicator. Evaluation metrics may be provided through documentation, tables or scripts available in the source code of the target tool.
- [ ] Software requires human code review. (`human_code_review_requirement`)
      This indicator aims to determine if a software project requires human code review before pull requests.
- [ ] All tests defined by the software component pass (`passed_tests_ok`)
      The software tool passes all the tests provided within its own repository.
- [ ] Software has sufficient test coverage (`software_test_coverage`)
      Indicates that the test suite covers most (or ideally all) the code branches, input fields, and functionality

## Interaction Capability

- [ ] Software has documentation (`software_has_documentation`)
      This indicator aims to determine if a software project comes with many forms of documentation like readme or readthedocs

## Maintainability

- [ ] Code churn follows community conventions (`code_churn_ok`)
      The code churn (how much a source code has changed over time) of the project's source code is maintained within a reasonable level according to the community's standards and conventions. An example of how to calculate it would be code churn = added lines + deleted lines.
- [ ] The documentation coverage for the codebase follows community conventions (`code_documentation_coverage_ok`)
      This check tries to determine if the project's codebase is mostly documented according according to community conventions and standards (i.e. docstrings).
- [ ] Code duplication follows community conventions (`code_duplication_ok`)
      The code duplication ratio is maintained at a reasonable level according to community's standards and conventions. Code duplication ratio is the percentage of code within a code base or project that is syntactically identical, often measured using code blocks. An example for calculating it may be (lines_duplicated/lines_of_code)*100.
- [ ] Code smells follow community conventions (`code_smells_ok`)
      The code smell ratio is maintained at a reasonable level according to community standards and conventions. Code smells are indicators of possible design problems mainly for maintainability of the code (i.e. functions too large, code that is how to read, too many input parameters for a function, etc.). The density of code smells can be estimated with the code smell ratio, an estimator of code smells within a codebase of project often meassured using rule-based checks (i.e. Sonarqube). An example for calculating it could be (code_smells/lines_of_code)*1000.
- [ ] Coupling between objects follows community conventions (`coupling_between_objects_ok`)
      The coupling between objects (CBO) ratio is maintained at a reasonable level according to the community's standards or expectations
- [ ] Cyclomatic complexity follows community conventions (`cyclomatic_complexity_ok`)
      Cyclomatic complexity (i.e., the number of linearly independent paths through a program’s source code) of the whole software component or modules/components/classes/functions/methods should follow the conventions established by the community responsible for maintaining the tool. Cyclomatic complexity is created by calculating the number of different code paths in the flow of the program. A program that has complex control flow requires more tests to achieve good code coverage and is less maintainable.
- [ ] Project has active communication channels (`has_active_communication_channels`)
      The project has communication channels (i.e. Slack, Gitter, etc.) where users and developers can discuss project-related matters and also be up to date with updates, notices and other relevant information.
- [ ] Software has continuous integration tests (`has_ci-tests`)
      This indicator aims to determine if the project runs tests before pull requests are merged.
- [ ] Software has no linting issues (`has_no_linting_issues`)
      The project addresses or resolves warnings identified by compilers, safe modes, or linters.
- [ ] Software has releases (`has_releases`)
      To enable collaborative review, the project's source repository MUST include interim versions for review between releases; it MUST NOT include only final releases. This indicator determines if a software project has releases. This can be achieved by looking for tags or using software that retrieves related data.
- [ ] Cohesion among methods/functions of a module follows community conventions (`internal_cohesion_ok`)
      The cohesion among methods/functions of a module is maintained to a reasonable level according to community expectations and standards. Cohesion describes how related the functions within a single module are. Low cohesion implies that a given module performs tasks which are not very related to each other and hence can create problems as the module becomes large
- [ ] Number of lines of code follows community standards or expectations (`lines_of_code_ok`)
      Number of lines of code for the whole software project or components/modules/classes/functions/methods should follow the conventions established by the community responsible for maintaining the source code
- [ ] Maintainability index follows community conventions (`maintainability_index_ok`)
      The maintainability index (i.e., degree of effectiveness and efficiency with which a product or system can be modified by the intended maintainers) should follow conventions and standards established by the community responsible for maintaining the source code or system. The maintainability index depends on 3 main factors: cyclomatic complexiy, lines of code and halstead volume (amount of information that needs to be processed to understand the code). An example for calculating it could be MAX(0,(171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code))*100 / 171).
- [ ] Software has up-to-date metadata (`metadata_is_up_to_date`)
      Metadata information reflects the current description of a software project. This indicator ensures that the current project metadata provides up to date, accurate and relevant information about a software component.
- [ ] Project repository is active (`project_is_active`)
      This indicator aims to determine if a project's repository is maintained by its corresponding maintainers (i.e. commiting within a reasonable time window or having a status of "Active").
- [ ] Software has ci/cd workflows in its repository (`repository_workflows`)
      This indicator tries aims determine if a software project makes use of workflows to automate processes like testing and deployment.
- [ ] Software specifies requirements (`requirements_specified`)
      This indicator tries to determine if the project specifies what is required to use the software.
- [ ] Software provides issue tracking (`support_issue_tracking`)
      The software project offers an accessible issue tracking system (e.g., GitHub/GitLab Issues or a helpdesk) that is used to report, document, and manage bugs, enhancement requests, and user-facing operational issues.
- [ ] Software uses a tool for warnings or mistakes (`uses_tool_for_warnings_and_mistakes`)
      This indicator checks that the project enables one or more compiler warning flags, a "safe" language mode, or uses a separate "linter" tool to look for code quality errors or common simple mistakes, if there is at least one FLOSS tool that can implement this criterion in the selected language.

## Open Source Software

- [ ] Project has active communication channels (`has_active_communication_channels`)
      The project has communication channels (i.e. Slack, Gitter, etc.) where users and developers can discuss project-related matters and also be up to date with updates, notices and other relevant information.
- [ ] Project has active contributors beyond core maintainers (`has_active_contributors`)
      Contributions and/or other additions/updates to the project aren't centralised on only the core maintainers, but also other contributors.
- [ ] Software repository has contribution guidelines (`has_contribution_guidelines`)
      The software repository provides contribution guidelines in case someone wants to contribute to the project.
- [ ] Responses to issues and/or pull requests are done within a defined timeframe (`response_timeframe_ok`)
      The maintainers of the project's repository respond to issues and/or pull requests within a defined time frame that follows the related community's conventions.

## Reliability

- [ ] Software provides tests. (`software_has_tests`)
      Evaluates the extent to which the software has been tested, including unit tests, integration tests, and system tests, to ensure reliability and correctness.
- [ ] Software has sufficient test coverage (`software_test_coverage`)
      Indicates that the test suite covers most (or ideally all) the code branches, input fields, and functionality

## Safety

- [ ] Software uses fuzzing (`uses_fuzzing`)
      This indicator checks that the software produced by the project includes software written using a memory-unsafe language (e.g., C or C++), then at least one dynamic tool (e.g., a fuzzer or web application scanner) be routinely used in combination with a mechanism to detect memory safety problems such as buffer overwrites.

## Security

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.
- [ ] Project repository has no binary artifacts (`has_no_binary_artifacts`)
      The repository does not contain binary artifacts. Binary artifacts are files generated by compilation or packaging tools that contain code that is no longer human-readable (i.e. .class, .jar, .war, .pyc, etc.).
- [ ] No critical vulnerabilities (`no_critical_vulnerability`)
      Checks if reported critical vulnerabilities have been fixed
- [ ] No leaked credentials (`no_leaked_credentials`)
      Checks if hardcoded secrets like passwords, API keys, and tokens is stored in the public git repository
- [ ] Has static analysis for common vulnerabilities (`static_analysis_common_vulnerabilities`)
      At least one static code analysis tool used includes rules or techniques to detect common vulnerabilities specific to the language or environment.

## Sustainability

- [ ] Software has dependency management solution (`dependency_management`)
      Reviews how external libraries and dependencies are managed to ensure compatibility and security.

## sustaintability

- [ ] Software repository has contribution guidelines (`has_contribution_guidelines`)
      The software repository provides contribution guidelines in case someone wants to contribute to the project.
