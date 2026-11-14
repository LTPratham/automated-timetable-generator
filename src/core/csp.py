"""Core Constraint Satisfaction Problem (CSP) abstraction."""

from abc import ABC, abstractmethod
from typing import Dict, List, Generic, TypeVar, Optional, Any, Set

V = TypeVar("V")  # Variable type
D = TypeVar("D")  # Domain value type


class Constraint(Generic[V, D], ABC):
    """Abstract base class for all constraints in the CSP."""

    def __init__(self, variables: List[V], name: Optional[str] = None):
        self.variables: List[V] = variables
        self.name: str = name or self.__class__.__name__

    @abstractmethod
    def is_satisfied(self, assignment: Dict[V, D]) -> bool:
        """Returns True if the constraint is satisfied given the current partial assignment."""
        pass


class CSP(Generic[V, D]):
    """Generic Constraint Satisfaction Problem framework."""

    def __init__(self, variables: List[V], domains: Dict[V, List[D]]):
        self.variables: List[V] = variables
        self.domains: Dict[V, List[D]] = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = {var: [] for var in variables}

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        """Registers a constraint for all variables it governs."""
        for var in constraint.variables:
            if var not in self.variables:
                raise LookupError(f"Variable {var} in constraint not found in CSP variables")
            self.constraints[var].append(constraint)

    def is_consistent(self, variable: V, value: D, assignment: Dict[V, D]) -> bool:
        """Checks if assigning value to variable violates any constraint with currently assigned variables."""
        # Speculatively apply assignment
        assignment[variable] = value
        for constraint in self.constraints[variable]:
            if not constraint.is_satisfied(assignment):
                del assignment[variable]
                return False
        del assignment[variable]
        return True

    def is_complete(self, assignment: Dict[V, D]) -> bool:
        """Returns True if every variable has an assigned value."""
        return len(assignment) == len(self.variables)

    def get_neighbors(self, variable: V) -> Set[V]:
        """Returns all other variables that share at least one constraint with the given variable."""
        neighbors: Set[V] = set()
        for constraint in self.constraints[variable]:
            for neighbor in constraint.variables:
                if neighbor != variable:
                    neighbors.add(neighbor)
        return neighbors

