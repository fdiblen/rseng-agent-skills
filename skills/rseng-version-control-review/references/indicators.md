<!-- Generated file - do not edit. Rebuilt by the rseng-agent-skills
     pipeline from the configured content sources; see extensions/. -->

# Quality indicator checklist

Check each indicator that applies; judge applicability by the
software's tier (analysis code, prototype tool, infrastructure).

## FAIRness

- [ ] Software has no linting issues (`has_no_linting_issues`)
      The project addresses or resolves warnings identified by compilers, safe modes, or linters.
- [ ] Software uses a tool for warnings or mistakes (`uses_tool_for_warnings_and_mistakes`)
      This indicator checks that the project enables one or more compiler warning flags, a "safe" language mode, or uses a separate "linter" tool to look for code quality errors or common simple mistakes, if there is at least one FLOSS tool that can implement this criterion in the selected language.
- [ ] Software makes use of version control (`version_control_use`)
      This indicator aims to determine if a software project uses version control.

## Functional suitability

- [ ] Software requires human code review. (`human_code_review_requirement`)
      This indicator aims to determine if a software project requires human code review before pull requests.

## Maintainability

- [ ] Code duplication follows community conventions (`code_duplication_ok`)
      The code duplication ratio is maintained at a reasonable level according to community's standards and conventions. Code duplication ratio is the percentage of code within a code base or project that is syntactically identical, often measured using code blocks. An example for calculating it may be (lines_duplicated/lines_of_code)*100.
- [ ] Code smells follow community conventions (`code_smells_ok`)
      The code smell ratio is maintained at a reasonable level according to community standards and conventions. Code smells are indicators of possible design problems mainly for maintainability of the code (i.e. functions too large, code that is how to read, too many input parameters for a function, etc.). The density of code smells can be estimated with the code smell ratio, an estimator of code smells within a codebase of project often meassured using rule-based checks (i.e. Sonarqube). An example for calculating it could be (code_smells/lines_of_code)*1000.
- [ ] Coupling between objects follows community conventions (`coupling_between_objects_ok`)
      The coupling between objects (CBO) ratio is maintained at a reasonable level according to the community's standards or expectations
- [ ] Cyclomatic complexity follows community conventions (`cyclomatic_complexity_ok`)
      Cyclomatic complexity (i.e., the number of linearly independent paths through a program’s source code) of the whole software component or modules/components/classes/functions/methods should follow the conventions established by the community responsible for maintaining the tool. Cyclomatic complexity is created by calculating the number of different code paths in the flow of the program. A program that has complex control flow requires more tests to achieve good code coverage and is less maintainable.
- [ ] Software has no linting issues (`has_no_linting_issues`)
      The project addresses or resolves warnings identified by compilers, safe modes, or linters.
- [ ] Cohesion among methods/functions of a module follows community conventions (`internal_cohesion_ok`)
      The cohesion among methods/functions of a module is maintained to a reasonable level according to community expectations and standards. Cohesion describes how related the functions within a single module are. Low cohesion implies that a given module performs tasks which are not very related to each other and hence can create problems as the module becomes large
- [ ] Number of lines of code follows community standards or expectations (`lines_of_code_ok`)
      Number of lines of code for the whole software project or components/modules/classes/functions/methods should follow the conventions established by the community responsible for maintaining the source code
- [ ] Maintainability index follows community conventions (`maintainability_index_ok`)
      The maintainability index (i.e., degree of effectiveness and efficiency with which a product or system can be modified by the intended maintainers) should follow conventions and standards established by the community responsible for maintaining the source code or system. The maintainability index depends on 3 main factors: cyclomatic complexiy, lines of code and halstead volume (amount of information that needs to be processed to understand the code). An example for calculating it could be MAX(0,(171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code))*100 / 171).
- [ ] Software uses a tool for warnings or mistakes (`uses_tool_for_warnings_and_mistakes`)
      This indicator checks that the project enables one or more compiler warning flags, a "safe" language mode, or uses a separate "linter" tool to look for code quality errors or common simple mistakes, if there is at least one FLOSS tool that can implement this criterion in the selected language.
