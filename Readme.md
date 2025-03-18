# PDDL and SMT Analyzer

A Python-based tool for analyzing PDDL and SMT-LIB files. This repository provides utilities to compute key metrics such as the number of grounded operators, branching factor, operator density, effect ratios, AST depth, and an estimated complexity score for both PDDL and SMT descriptions.

## Features

- **PDDL Analysis**
  - Compatible with classical (instantaneous) and temporal (durative) planning problems
  - Counts total grounded operators (instantiated actions)
  - Calculates average branching factor
  - Computes operator density (ratio of grounded operators to objects)
  - Computes positive-to-negative effect ratio for both instantaneous and durative actions
  - Estimates complexity as the logarithm of a combined metric

- **SMT Analysis**
  - Counts the number of free variables
  - Counts constraints based on the top-level structure of the formula
  - Gathers statistics on the operators used by traversing the AST
  - Determines the AST depth
  - Estimates complexity as the logarithm of a combined metric

## Requirements

- Python 3.6 or higher
- [unified-planning](https://github.com/aiplan4eu/unified-planning) – for parsing and analyzing PDDL files
- [pysmt](https://pysmt.readthedocs.io/en/latest/) – for parsing and analyzing SMT-LIB files

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/hsu-aut/PDDL-and-SMT-Metrics-Framework.git
    cd PDDL-and-SMT-Metrics-Framework
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```


## Usage

### Running the Main Script

The main script loads the PDDL domain and problem files, and optionally an SMT-LIB file, to perform the analysis.

- **Analyze PDDL files only:**

    ```bash
    python evaluation.py -d path/to/domain.pddl -p path/to/problem.pddl
    ```

- **Analyze both PDDL and SMT files:**

    ```bash
    python evaluation.py -d path/to/domain.pddl -p path/to/problem.pddl -s path/to/file.smt2
    ```

## Contributing

Contributions are welcome! If you have ideas for improvements or encounter any issues, please open an issue or submit a pull request.
