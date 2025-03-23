import argparse
import logging
from pddl_metrics import PDDLAnalyzer  # Import the PDDLAnalyzer class
from smt_metrics import SMTAnalyzer      # Import the SMTAnalyzer class

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Loads PDDL domain and problem files and optionally an SMT file for analysis."
    )
    parser.add_argument("-d", "--domain", required=True, help="Path to the PDDL domain file")
    parser.add_argument("-p", "--problem", required=True, help="Path to the PDDL problem file")
    parser.add_argument("-s", "--smt", help="Optional: Path to the SMT-LIB file for analysis")
    
    args = parser.parse_args()

    # Process PDDL files (check/replace umlauts)    
    domainfile = args.domain
    problemfile = args.problem
    logging.info(f"Domain file: {domainfile}")
    logging.info(f"Problem file: {problemfile}")

    try:
        # PDDL analysis
        logging.info("PDDL files loaded successfully!")

        analyzer = PDDLAnalyzer(domainfile, problemfile)
        pddl_metrics = analyzer.get_metrics()

        logging.info("\nPDDL Metrics:")
        logging.info(f"Total Ground Operators: {pddl_metrics['ground_operators']}")
        logging.info(f"Average Branching Factor: {pddl_metrics['branching_factor']:.2f}")
        logging.info(f"Operator Density: {pddl_metrics['operator_density']:.2f}")
        logging.info(f"Positive to Negative Effect Ratio: {pddl_metrics['effect_ratio']:.2f}")
        logging.info(f"Estimated Planning Complexity: {pddl_metrics['estimated_complexity']:.2f}")

    except Exception as e:
        logging.error(f"Error loading the PDDL files: {e}")

    # If an SMT file is provided, perform SMT analysis
    if args.smt:
        try:
            logging.info(f"\nAnalyzing SMT file: {args.smt}")
            smt_analyzer = SMTAnalyzer(args.smt)
            smt_metrics = smt_analyzer.get_metrics()

            logging.info("\nSMT Metrics:")
            logging.info(f"Free Variables: {smt_metrics['variables']}")
            logging.info(f"Constraints: {smt_metrics['constraints']}")
            logging.info(f"Operator Statistics (OS): {smt_metrics['operator_statistics']}")
            logging.info(f"(OS) Unique Symbols: {smt_metrics['unique_symbols']}")
            logging.info(f"(OS) unique_real_constants: {smt_metrics['unique_real_constants']}")

            logging.info(f"AST Depth: {smt_metrics['ast_depth']}")
            logging.info(f"Estimated Complexity: {smt_metrics['estimated_complexity']:.2f}")
        except Exception as e:
            logging.error(f"Error loading the SMT file: {e}")
