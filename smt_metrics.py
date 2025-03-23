import math
import io
import logging
from typing import Dict, Any
from pysmt.smtlib.parser import SmtLibParser
from pysmt.fnode import FNode
from pysmt.operators import op_to_str

logging.basicConfig(level=logging.INFO)

class SMTAnalyzer:
    """
    A class for analyzing SMT-LIB descriptions.
    It extracts:
      - Number of variables and constraints
      - Operator usage statistics
      - Unique symbols and real constants
      - AST depth
      - Estimated complexity
    """

    def __init__(self, smt_file: str):
        """
        Loads and parses the SMT-LIB file, extracting all 'assert' formulas.
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
            # Extract all assert commands from the script
            self.formulas = [cmd.args[0] for cmd in script.commands if cmd.name == "assert"]
        except Exception as e:
            logging.error(f"Error parsing SMT-LIB file: {e}")
            raise

    def count_variables(self) -> int:
        """
        Counts the number of free variables used across all formulas.
        """
        vars = set()
        for f in self.formulas:
            vars.update(f.get_free_variables())
        return len(vars)

    def count_constraints(self) -> int:
        """
        Returns the number of assert statements (top-level constraints).
        """
        return len(self.formulas)

    def operator_statistics(self) -> Dict[str, int]:
        """
        Accurately counts every operator usage in the ASTs of all formulas.
        Each OR/AND counts exactly once per usage (matches SMT-LIB source).
        """
        stats = {}

        def _walk(node: FNode):
            op_str = op_to_str(node.node_type())
            stats[op_str] = stats.get(op_str, 0) + 1
            for child in node.args():
                _walk(child)

        for formula in self.formulas:
            _walk(formula)

        return stats



    def count_unique_symbols(self) -> int:
        """
        Counts the number of unique variable names used across all formulas.
        """
        symbols = set()

        def _walk(node: FNode):
            if node.is_symbol():
                symbols.add(node.symbol_name())
            for child in node.args():
                _walk(child)

        for formula in self.formulas:
            _walk(formula)

        return len(symbols)

    def count_unique_real_constants(self) -> int:
        """
        Counts the number of unique real constant values used.
        """
        constants = set()

        def _walk(node: FNode):
            if node.is_real_constant():
                constants.add(str(node.constant_value()))
            for child in node.args():
                _walk(child)

        for formula in self.formulas:
            _walk(formula)

        return len(constants)

    def ast_depth(self) -> int:
        """
        Determines the maximum depth of the AST across all assert formulas.
        """
        def depth(node: FNode) -> int:
            if node.is_constant() or node.is_symbol():
                return 1
            else:
                return 1 + max((depth(child) for child in node.args()), default=0)

        return max((depth(f) for f in self.formulas), default=0)

    def estimated_complexity(self) -> float:
        """
        Estimates the overall formula complexity as:
        log2(variables * constraints * total_ops * max_ast_depth)
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
        Collects and returns all analysis metrics in a dictionary.
        Includes both operator usage and unique entity counts.
        """
        op_stats = self.operator_statistics()

        return {
            "variables": self.count_variables(),
            "constraints": self.count_constraints(),
            "operator_statistics": op_stats,
            "unique_symbols": self.count_unique_symbols(),
            "unique_real_constants": self.count_unique_real_constants(),
            "ast_depth": self.ast_depth(),
            "estimated_complexity": self.estimated_complexity()
        }
