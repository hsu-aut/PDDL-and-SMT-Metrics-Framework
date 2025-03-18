import math
import io
import logging
from typing import Dict, Any
from pysmt.smtlib.parser import SmtLibParser
from pysmt.fnode import FNode

logging.basicConfig(level=logging.INFO)

class SMTAnalyzer:
    """
    A class for analyzing SMT-LIB descriptions.
    The following metrics are extracted:
      - Number of free variables
      - Number of constraints (interpreted as the number of top-level sub-statements)
      - Statistics on the operators used
      - Depth of the abstract syntax tree (AST)
      - An estimation of the complexity as the logarithm of a combined value
    """

    def __init__(self, smt_file: str):
        """
        Loads and parses the SMT-LIB file.
        """
        self.smt_file = smt_file
        try:
            with open(smt_file, "r") as f:
                content = f.read()
        except FileNotFoundError:
            logging.error(f"File not found: {smt_file}")
            raise
        except IOError as e:
            logging.error(f"Error reading file {smt_file}: {e}")
            raise

        stream = io.StringIO(content)
        parser = SmtLibParser()
        try:
            script = parser.get_script(stream)
            self.formula = script.get_last_formula()
        except Exception as e:
            logging.error(f"Error parsing SMT-LIB file: {e}")
            raise

    def count_variables(self) -> int:
        """
        Counts the number of free variables in the formula.
        """
        return len(self.formula.get_free_variables())

    def count_constraints(self) -> int:
        """
        Counts the number of constraints.
        This is interpreted as the number of direct sub-statements of the top-level formula,
        if it represents a conjunction (And).
        """
        if self.formula.is_and():
            return len(self.formula.args())
        else:
            return 1

    def operator_statistics(self) -> Dict[str, int]:
        """
        Collects the frequencies of the operators used in the formula
        by recursively traversing the AST.
        """
        stats = {}
        visited = set()

        def _walk(node: FNode):
            # Avoid multiple visits (DAG)
            if node in visited:
                return
            visited.add(node)
            op = node.node_type()
            stats[op] = stats.get(op, 0) + 1
            for child in node.args():
                _walk(child)

        _walk(self.formula)
        return stats

    def ast_depth(self) -> int:
        """
        Recursively determines the depth of the abstract syntax tree (AST) of the formula.
        """
        def depth(node: FNode) -> int:
            if node.is_constant() or node.is_symbol():
                return 1
            else:
                return 1 + max((depth(child) for child in node.args()), default=0)
        return depth(self.formula)

    def estimated_complexity(self) -> float:
        """
        Estimates the complexity based on the number of variables,
        constraints, operators, and the AST depth.
        """
        var_count = self.count_variables()
        constr_count = self.count_constraints()
        op_stats = self.operator_statistics()
        total_ops = sum(op_stats.values())
        depth = self.ast_depth()

        product = var_count * constr_count * total_ops * depth
        if product <= 0:
            return 0.0
        return math.log2(product)

    def get_metrics(self) -> Dict[str, Any]:
        """
        Returns all collected metrics as a dictionary.
        """
        return {
            "variables": self.count_variables(),
            "constraints": self.count_constraints(),
            "operator_statistics": self.operator_statistics(),
            "ast_depth": self.ast_depth(),
            "estimated_complexity": self.estimated_complexity()
        }