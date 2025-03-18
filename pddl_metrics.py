import math
import logging
import os
import unified_planning as up
from unified_planning.model import InstantaneousAction, DurativeAction
from typing import Dict
from unified_planning.io import PDDLReader

logging.basicConfig(level=logging.INFO)

class PDDLAnalyzer:
    """Analyzes PDDL domain and problem files and computes various metrics."""

    def __init__(self, domainfile: str, problemfile: str):
        logging.info("Initializing PDDLAnalyzer")
        self.domainfile, self.problemfile = self.process_pddl_files(domainfile, problemfile)

        try:
            reader = PDDLReader()
            self.problem = reader.parse_problem(self.domainfile, self.problemfile)
            self.kind = self.problem.kind
            logging.debug(f"ProblemKind features: {self.kind.features}")
        except Exception as e:
            logging.error(f"Error loading PDDL files: {e}")
            raise

        logging.info("PDDLAnalyzer initialized successfully")

    def supports_temporal_logic(self) -> bool:
        """Checks if the problem uses temporal logic."""
        return self.kind.has_time() or self.kind.has_timed_effects() or self.kind.has_timed_goals()

    def count_actions(self) -> int:
        """Counts the number of defined actions."""
        return len(self.problem.actions)

    def has_durative_actions(self) -> bool:
        """Checks if the problem contains durative actions."""
        return self.kind.has_time()

    def has_fluents(self) -> bool:
        """Checks if the problem uses fluents (numeric or boolean variables)."""
        has_numeric_fluents = (
            self.kind.has_numeric_fluents() or
            self.kind.has_object_fluents() or
            self.kind.has_int_fluents() or
            self.kind.has_real_fluents()
        )
        has_boolean_fluents = any(fluent.type.is_bool_type() for fluent in self.problem.fluents)

        return has_numeric_fluents or has_boolean_fluents

    def count_ground_operators(self) -> int:
        """Calculates the total number of possible instantiated operators."""
        total_ground_operators = 0
        for action in self.problem.actions:
            param_combinations = 1
            for param in action.parameters:
                num_objects = sum(1 for _ in self.problem.objects(param.type))
                param_combinations *= max(1, num_objects)
            total_ground_operators += param_combinations
        return total_ground_operators

    def branching_factor(self) -> float:
        """Calculates the average branching factor."""
        num_ground_ops = self.count_ground_operators()
        num_abstract_ops = len(self.problem.actions)
        return num_ground_ops / num_abstract_ops if num_abstract_ops > 0 else 1

    def operator_density(self) -> float:
        """Calculates operator density as grounded operators per object."""
        total_ground_ops = self.count_ground_operators()
        num_objects = len(self.problem.all_objects)
        return total_ground_ops / num_objects if num_objects > 0 else 1


    def effect_ratio(self) -> float:
        """Computes the ratio of positive to negative effects."""
        total_pos = total_neg = 0

        for action in self.problem.actions:
            if isinstance(action, DurativeAction):
                for timing, effects_list in action.effects.items():
                    for effect in effects_list:
                        if effect.value.is_true():
                            total_pos += 1
                        elif effect.value.is_false():
                            total_neg += 1
            elif isinstance(action, InstantaneousAction):
                for effect in action.effects:
                    if effect.value.is_true():
                        total_pos += 1
                    elif effect.value.is_false():
                        total_neg += 1
                    elif effect.value.is_constant():
                        if effect.value.constant_value() > 0:
                            total_pos += 1
                        else:
                            total_neg += 1

        total_neg = max(1, total_neg)
        return max(0.1, total_pos / total_neg)

    def estimated_complexity(self) -> float:
        """Calculates estimated planning complexity analogously to pddlpy."""
        num_ground_ops = max(0.1, self.count_ground_operators())
        b_factor = max(0.1, self.branching_factor())
        e_ratio = max(0.1, self.effect_ratio())

        return math.log2(num_ground_ops * b_factor * e_ratio)

    def get_metrics(self) -> Dict[str, float]:
        """Returns all calculated metrics as a dictionary."""
        return {
            "supports_temporal_logic": self.supports_temporal_logic(),
            "num_actions": self.count_actions(),
            "has_durative_actions": self.has_durative_actions(),
            "has_fluents": self.has_fluents(),
            "ground_operators": self.count_ground_operators(),
            "branching_factor": self.branching_factor(),
            "operator_density": self.operator_density(),
            "effect_ratio": self.effect_ratio(),
            "estimated_complexity": self.estimated_complexity()
        }

    def process_pddl_files(self, domainfile, problemfile):
        """Checks and converts files if non-ASCII characters are present."""
        if not self.check_non_ascii_chars(domainfile):
            domainfile = self.replace_umlauts(domainfile)
        if not self.check_non_ascii_chars(problemfile):
            problemfile = self.replace_umlauts(problemfile)
        return domainfile, problemfile

    def check_non_ascii_chars(self, file_path):
        """Checks for non-ASCII characters in a file."""
        with open(file_path, "rb") as f:
            data = f.read()
        non_ascii_chars = [(i, byte) for i, byte in enumerate(data) if byte > 127]
        if non_ascii_chars:
            logging.error(f"Non-ASCII characters found in {file_path} at positions: {non_ascii_chars[:5]}...")
            return False
        return True

    def replace_umlauts(self, file_path):
        """Replaces German umlauts and saves an ASCII-only version of the file."""
        new_file_path = os.path.splitext(file_path)[0] + "_ascii.pddl"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("ö", "oe").replace("ä", "ae").replace("ü", "ue").replace("ß", "ss")
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Saved ASCII-only file as: '{new_file_path}'")
        return new_file_path


# Example usage
if __name__ == "__main__":
    analyzer = PDDLAnalyzer("usecase/D_MPS500_temporal.pddl", "usecase/P_MPS500_einfach.pddl")
    metrics = analyzer.get_metrics()
    logging.info(f"PDDL analysis completed: {metrics}")