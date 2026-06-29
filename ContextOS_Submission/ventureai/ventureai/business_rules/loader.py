import os
import yaml
import sys
from typing import List
from business_rules.models import Rule

class RuleLoader:
    @staticmethod
    def load_rules(file_path: str = None) -> List[Rule]:
        """Loads rules from the specified YAML file path, defaulting to config path."""
        if not file_path:
            file_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "business_rules",
                "rules.yaml"
            )
            
        if not os.path.exists(file_path):
            sys.stderr.write(f"Warning: Business rules file not found at {file_path}. Returning empty rule set.\n")
            return []
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            if not data or "rules" not in data:
                return []
                
            rules = []
            for rule_dict in data["rules"]:
                try:
                    rules.append(Rule(**rule_dict))
                except Exception as parse_err:
                    sys.stderr.write(f"Warning: Failed to parse rule dict {rule_dict}: {parse_err}\n")
            return rules
        except Exception as e:
            sys.stderr.write(f"Error loading business rules from {file_path}: {e}\n")
            return []
