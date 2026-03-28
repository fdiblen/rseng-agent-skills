<!-- Generated file - do not edit.
     Source: pages/tasks/using_version_control.md @ 03a8352e0701acf6ae28a1f6c9069e9b2caf8e7e
     From RSQKit (the Research Software Quality Kit) by the EVERSE project and the RSQKit team (https://everse.software/RSQKit/using_version_control),
     CC-BY-4.0. DOI: 10.5281/zenodo.14923573 -->

## How do I choose the right version control system for my research project?

### Description

Selecting an appropriate version control system (VCS) is crucial for managing research software effectively.
This decision impacts collaboration, data management, and long-term project sustainability.

### Considerations

* Project size and complexity
* Team size and geographical distribution
* Types of files (code, data, documents)
* Required integrations with other research tools
* Team's technical expertise
* Long-term goals and potential for open-source contribution
* Handling of large binary files common in research
* Compliance with institutional policies and grant requirements

### Solutions

* For most research projects, choose [Git](https://git-scm.com/):
   * Widely used in both academia and industry
   * Excellent for collaborative work and open-source projects
   * Large ecosystem of tools and hosting platforms ([GitHub](https://github.com/), [GitLab](https://about.gitlab.com/))
* For projects with large binary files, consider:
   * [Git Large File Storage](https://git-lfs.github.com/) (LFS)
   * [Perforce](https://www.perforce.com/) , if dealing with extremely large datasets
* For teams new to version control:
   * Start with [Git](https://git-scm.com/), but provide thorough training
   * Consider [Mercurial](https://www.mercurial-scm.org/) as an alternative if [Git](https://git-scm.com/) proves too complex
* For projects requiring strict access control - [Subversion](https://github.com/apache/subversion) (SVN) might be suitable, though less modern

## How do I implement version control in my research workflow?

### Description

Implementing version control in a research context involves more than just choosing a system. It requires establishing workflows, educating team members, and integrating with existing research practices.

### Considerations

* Current data management practices
* Reproducibility requirements of your research
* Collaboration patterns within your team and with external partners
* Integration with data analysis pipelines and tools
* Publication and open science practices
* Long-term archiving of research outputs

### Solutions

* Establish a clear workflow:
   * Define a branching strategy (e.g., Git Flow for larger projects)
   * Set guidelines for commit messages and code reviews
* Integrate with your development environment:
   * Set up your Integrated Development Environment (IDE), such as [Visual Studio Code](https://code.visualstudio.com/), [RStudio](https://posit.co/download/rstudio-desktop/), [PyCharm](https://www.jetbrains.com/pycharm/) or [Eclipse](https://eclipseide.org/), or a text editor to work with your VCS
   * Implement continuous integration for automated testing
* Educate your team:
   * Provide training on basic VCS concepts and commands
   * Create documentation for your specific workflow
* Ensure reproducibility:
   * Use tags to mark versions used in publications
   * Include configuration files and dependencies in version control
* Facilitate collaboration:
   * Use a platform like GitHub or GitLab for easy sharing and collaboration
   * Implement code review practices to maintain quality
* Maintain your repository:
   * Regularly backup your repository
   * Periodically clean up old branches and review access permissions

## Tool- or Domain-Specific Tasks

This is a suggested list tool-specific sub-tasks to have a look at.
