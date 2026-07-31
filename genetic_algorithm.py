import random
import math
from dataclasses import dataclass, field
from typing import List, Callable, Tuple

@dataclass
class Individual:
    genes:   List[float]
    fitness: float = 0.0

    def __lt__(self, other): return self.fitness < other.fitness

class GeneticAlgorithm:
    def __init__(self, pop_size=100, gene_length=10, mutation_rate=0.05,
                 crossover_rate=0.8, elitism=0.1, tournament_size=5,
                 gene_range=(-10, 10)):
        self.pop_size       = pop_size
        self.gene_length    = gene_length
        self.mutation_rate  = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism        = elitism
        self.tournament_size = tournament_size
        self.gene_range     = gene_range
        self.population:    List[Individual] = []
        self.best_history:  List[float] = []
        self.avg_history:   List[float] = []
        self.generation     = 0

    def initialize(self):
        lo, hi = self.gene_range
        self.population = [
            Individual(genes=[random.uniform(lo, hi) for _ in range(self.gene_length)])
            for _ in range(self.pop_size)
        ]

    def evaluate(self, fitness_fn: Callable[[List[float]], float]):
        for ind in self.population:
            ind.fitness = fitness_fn(ind.genes)
        self.population.sort(reverse=True)

    def tournament_select(self) -> Individual:
        contestants = random.sample(self.population, self.tournament_size)
        return max(contestants, key=lambda x: x.fitness)

    def crossover(self, p1: Individual, p2: Individual) -> Tuple[Individual, Individual]:
        if random.random() > self.crossover_rate:
            return Individual(p1.genes[:]), Individual(p2.genes[:])

        if random.random() < 0.5:
            pt = random.randint(1, self.gene_length - 1)
            c1 = Individual(p1.genes[:pt] + p2.genes[pt:])
            c2 = Individual(p2.genes[:pt] + p1.genes[pt:])
        else:
            c1_genes, c2_genes = [], []
            for i in range(self.gene_length):
                alpha = random.random()
                c1_genes.append(alpha * p1.genes[i] + (1 - alpha) * p2.genes[i])
                c2_genes.append(alpha * p2.genes[i] + (1 - alpha) * p1.genes[i])
            c1, c2 = Individual(c1_genes), Individual(c2_genes)

        return c1, c2

    def mutate(self, ind: Individual):
        lo, hi = self.gene_range
        for i in range(self.gene_length):
            if random.random() < self.mutation_rate:
                if random.random() < 0.5:
                    ind.genes[i] += random.gauss(0, (hi - lo) * 0.1)
                else:
                    ind.genes[i] = random.uniform(lo, hi)
                ind.genes[i] = max(lo, min(hi, ind.genes[i]))

    def evolve(self, fitness_fn: Callable, generations: int = 200, verbose: bool = True):
        self.initialize()
        self.evaluate(fitness_fn)

        for gen in range(generations):
            self.generation = gen + 1
            elite_count = int(self.pop_size * self.elitism)
            new_pop     = self.population[:elite_count]

            while len(new_pop) < self.pop_size:
                p1 = self.tournament_select()
                p2 = self.tournament_select()
                c1, c2 = self.crossover(p1, p2)
                self.mutate(c1)
                self.mutate(c2)
                new_pop.extend([c1, c2])

            self.population = new_pop[:self.pop_size]
            self.evaluate(fitness_fn)

            best = self.population[0]
            avg  = sum(i.fitness for i in self.population) / self.pop_size
            self.best_history.append(best.fitness)
            self.avg_history.append(avg)

            if verbose and (gen + 1) % 20 == 0:
                print(f"  Gen {gen+1:>4} | Best: {best.fitness:>10.4f} | Avg: {avg:>10.4f}")

        return self.population[0]


def sphere_function(genes):
    return -sum(x**2 for x in genes)

def rastrigin_function(genes):
    n = len(genes)
    return -(10 * n + sum(x**2 - 10 * math.cos(2 * math.pi * x) for x in genes))

def ackley_function(genes):
    n   = len(genes)
    s1  = sum(x**2 for x in genes)
    s2  = sum(math.cos(2 * math.pi * x) for x in genes)
    val = -20 * math.exp(-0.2 * math.sqrt(s1 / n)) - math.exp(s2 / n) + 20 + math.e
    return -val

def tsp_fitness(genes):
    n      = len(genes)
    order  = sorted(range(n), key=lambda i: genes[i])
    cities = [(0,0),(1,5),(5,2),(6,6),(8,3),(2,8),(7,1),(3,4),(9,7),(4,9)]
    total  = 0
    for i in range(len(cities)):
        c1 = cities[order[i]]
        c2 = cities[order[(i+1) % len(cities)]]
        total += math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
    return -total


if __name__ == "__main__":
    problems = [
        ("Sphere",    sphere_function,    (-5.12, 5.12),  10),
        ("Rastrigin", rastrigin_function, (-5.12, 5.12),  10),
        ("Ackley",    ackley_function,    (-5, 5),        10),
        ("TSP",       tsp_fitness,        (-10, 10),      10),
    ]

    print("=" * 52)
    print("  Genetic Algorithm Optimizer")
    print("=" * 52)

    for name, fn, gene_range, n_genes in problems:
        print(f"\n{'─' * 52}")
        print(f"  Problem: {name} ({n_genes}D)")
        print(f"{'─' * 52}")

        ga = GeneticAlgorithm(
            pop_size=150, gene_length=n_genes,
            mutation_rate=0.08, crossover_rate=0.85,
            gene_range=gene_range
        )
        best = ga.evolve(fn, generations=200)
        print(f"\n  Best fitness : {best.fitness:.6f}")
        print(f"  Best genes   : [{', '.join(f'{g:.4f}' for g in best.genes[:5])}...]")
