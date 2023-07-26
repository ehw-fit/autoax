# Xel-FPGAs
This repository presents a basic scheme for evaluating Xel-FPGAs algorithm for automatic approximation of hardware accelerators. By the end of September 2023 basic examples (such as a gaussian filter) will be added.

## Requirements:
- Python3, Pandas, Scikit-learn, pyparetoarchive packages
- ABC available under berkley-abc command (default in Ubuntu)

## Script descriptions
- 01: generate random assignments
- 02: generate Verilog files by template
- External synthesis and simulation tool must be running, not in this repository, depends on the final task.
- 03: parsing results and quality
- 04: learning by different pipelines (like in the paper)
- 05: design exploration (for different pipelines)
- 06: gerate of pseudo-optimal Verilog files (from configs)
- External synthesis and simulation tool must be running, not in this repository, depends on the final task.
- 07: parsing results
