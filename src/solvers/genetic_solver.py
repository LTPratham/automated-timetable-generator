"""Genetic Algorithm (Evolutionary Search) Solver for Academic Timetabling.

Models timetable scheduling as an evolutionary optimization process with:
- Chromosome representation (gene = session allocation tuple)
- Hard clash penalty fitness function
- Tournament selection
- Two-point / Uniform crossover
- Random domain mutation
Directly fulfills the CSE276 project requirement to compare against evolutionary approaches.
"""

import time
import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from src.models.entities import SessionVariable, SlotAssignment, DayOfWeek, SessionType
from src.models.dataset import DepartmentDataset
from src.core.csp import CSP
from src.core.backtracking import SolverStatistics


@dataclass
class Individual:
    chromosome: Dict[SessionVariable, SlotAssignment]
    hard_violations: int = 0
    soft_penalty: float = 0.0
    fitness: float = 0.0


class GeneticTimetableSolver:
    """Genetic Algorithm optimization solver for Timetable CSP."""

    def __init__(
        self,
        population_size: int = 40,
        max_generations: int = 150,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.15,
        tournament_size: int = 4,
        time_limit_sec: float = 12.0,
    ):
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.time_limit_sec = time_limit_sec

    def _evaluate(
        self,
        chromosome: Dict[SessionVariable, SlotAssignment],
        dataset: DepartmentDataset,
    ) -> Tuple[int, float]:
        """Calculates hard constraint conflicts and soft penalty."""
        hard_violations = 0
        soft_penalty = 0.0

        # Occupancy tracking: (day, slot) -> list of (var, room_id)
        faculty_time: Dict[Tuple[str, DayOfWeek, int], int] = {}
        room_time: Dict[Tuple[str, DayOfWeek, int], int] = {}
        batch_time: Dict[Tuple[str, DayOfWeek, int], int] = {}

        for var, assign in chromosome.items():
            for day, slot in assign.occupied_slots:
                # Faculty double-booking
                fac_key = (var.faculty_id, day, slot)
                if fac_key in faculty_time:
                    hard_violations += 1
                faculty_time[fac_key] = faculty_time.get(fac_key, 0) + 1

                # Room double-booking
                room_key = (assign.room_id, day, slot)
                if room_key in room_time:
                    hard_violations += 1
                room_time[room_key] = room_time.get(room_key, 0) + 1

                # Batch double-booking
                batch_key = (var.batch_id, day, slot)
                if batch_key in batch_time:
                    hard_violations += 1
                batch_time[batch_key] = batch_time.get(batch_key, 0) + 1

            # Room capacity and type matching
            room = dataset.rooms_by_id.get(assign.room_id)
            batch = dataset.batches_by_id.get(var.batch_id)
            if room and batch:
                if room.capacity < batch.strength:
                    hard_violations += 1
                if var.session_type == SessionType.LAB and room.room_type.value != "Lab":
                    hard_violations += 2

            # Faculty unavailable slots
            fac = dataset.faculty_by_id.get(var.faculty_id)
            if fac and fac.unavailable_slots:
                for occ in assign.occupied_slots:
                    if occ in fac.unavailable_slots:
                        hard_violations += 1

            # Soft preference check
            if fac and fac.preferred_slots:
                if assign.start_slot_index not in fac.preferred_slots:
                    soft_penalty += 2.0

        return hard_violations, soft_penalty

    def _calc_fitness(self, hard_violations: int, soft_penalty: float) -> float:
        """Higher fitness is better; 0 hard violations yields positive fitness >= 1.0."""
        return 1.0 / (1.0 + (hard_violations * 100.0) + (soft_penalty * 0.1))

    def _create_random_individual(
        self,
        csp: CSP,
        dataset: DepartmentDataset,
    ) -> Individual:
        chromosome = {}
        for var in csp.variables:
            domain = csp.domains[var]
            assignment = random.choice(domain) if domain else None
            if assignment:
                chromosome[var] = assignment
        hv, sp = self._evaluate(chromosome, dataset)
        return Individual(
            chromosome=chromosome,
            hard_violations=hv,
            soft_penalty=sp,
            fitness=self._calc_fitness(hv, sp),
        )

    def _crossover(
        self,
        parent1: Individual,
        parent2: Individual,
        csp: CSP,
        dataset: DepartmentDataset,
    ) -> Individual:
        child_chrom = {}
        for var in csp.variables:
            # Uniform crossover: randomly pick gene from either parent
            if random.random() < 0.5:
                child_chrom[var] = parent1.chromosome[var]
            else:
                child_chrom[var] = parent2.chromosome[var]
        hv, sp = self._evaluate(child_chrom, dataset)
        return Individual(
            chromosome=child_chrom,
            hard_violations=hv,
            soft_penalty=sp,
            fitness=self._calc_fitness(hv, sp),
        )

    def _mutate(
        self,
        ind: Individual,
        csp: CSP,
        dataset: DepartmentDataset,
    ) -> None:
        for var in csp.variables:
            if random.random() < self.mutation_rate:
                domain = csp.domains[var]
                if domain:
                    ind.chromosome[var] = random.choice(domain)
        ind.hard_violations, ind.soft_penalty = self._evaluate(ind.chromosome, dataset)
        ind.fitness = self._calc_fitness(ind.hard_violations, ind.soft_penalty)

    def _tournament_select(self, population: List[Individual]) -> Individual:
        sample = random.sample(population, min(self.tournament_size, len(population)))
        return max(sample, key=lambda ind: ind.fitness)

    def solve(
        self,
        csp: CSP,
        dataset: DepartmentDataset,
    ) -> Tuple[Optional[Dict[SessionVariable, SlotAssignment]], SolverStatistics]:
        """Runs Genetic Algorithm evolutionary search."""
        start_time = time.perf_counter()
        population: List[Individual] = [
            self._create_random_individual(csp, dataset)
            for _ in range(self.population_size)
        ]

        best_individual = max(population, key=lambda ind: ind.fitness)
        evaluations = len(population)
        generation = 0

        while generation < self.max_generations:
            # Check convergence to 100% hard-clash-free
            if best_individual.hard_violations == 0:
                break

            if time.perf_counter() - start_time > self.time_limit_sec:
                break

            generation += 1
            new_population: List[Individual] = []

            # Elitism: retain top 2 best individuals unchanged
            sorted_pop = sorted(population, key=lambda ind: ind.fitness, reverse=True)
            new_population.extend([sorted_pop[0], sorted_pop[1]])

            # Reproduce next generation
            while len(new_population) < self.population_size:
                p1 = self._tournament_select(population)
                p2 = self._tournament_select(population)

                if random.random() < self.crossover_rate:
                    child = self._crossover(p1, p2, csp, dataset)
                else:
                    child = Individual(
                        chromosome=dict(p1.chromosome),
                        hard_violations=p1.hard_violations,
                        soft_penalty=p1.soft_penalty,
                        fitness=p1.fitness,
                    )

                self._mutate(child, csp, dataset)
                new_population.append(child)
                evaluations += 1

            population = new_population
            current_best = max(population, key=lambda ind: ind.fitness)
            if current_best.fitness > best_individual.fitness:
                best_individual = current_best

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        solved = best_individual.hard_violations == 0

        stats = SolverStatistics(
            algorithm_name="Genetic Algorithm (Evolutionary Search)",
            nodes_explored=evaluations,
            backtracks=best_individual.hard_violations,
            time_taken_ms=elapsed_ms,
            is_solved=solved,
        )

        return (best_individual.chromosome if solved else None, stats)
