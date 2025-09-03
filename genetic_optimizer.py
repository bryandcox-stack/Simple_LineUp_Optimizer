import argparse
import random
import statistics
from typing import List, Dict, Tuple
from game_simulator import Player, load_players, simulate_game
from lineup_optimizer import LineupResult, evaluate_lineup


class GeneticLineupOptimizer:
    def __init__(self, players: List[Player], lineup_size: int = 9, 
                 population_size: int = 50, mutation_rate: float = 0.1, 
                 tournament_size: int = 3):
        self.players = players
        self.lineup_size = min(lineup_size, len(players))
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.population = []
        self.fitness_cache = {}
    
    def create_random_lineup(self) -> List[Player]:
        """Create a random lineup (chromosome)"""
        return random.sample(self.players, self.lineup_size)
    
    def initialize_population(self) -> None:
        """Initialize the population with random lineups"""
        self.population = []
        for _ in range(self.population_size):
            lineup = self.create_random_lineup()
            self.population.append(lineup)
    
    def evaluate_fitness(self, lineup: List[Player], num_games: int, innings: int = 6) -> float:
        """Evaluate fitness (average runs) for a lineup with caching"""
        lineup_key = tuple(player.name for player in lineup)
        
        if lineup_key not in self.fitness_cache:
            result = evaluate_lineup(lineup, num_games, innings)
            self.fitness_cache[lineup_key] = result.mean_runs
        
        return self.fitness_cache[lineup_key]
    
    def tournament_selection(self, population: List[List[Player]], 
                           fitness_scores: List[float]) -> List[Player]:
        """Select parent using tournament selection"""
        tournament_indices = random.sample(range(len(population)), self.tournament_size)
        tournament_fitness = [(i, fitness_scores[i]) for i in tournament_indices]
        winner_index = max(tournament_fitness, key=lambda x: x[1])[0]
        return population[winner_index].copy()
    
    def order_crossover(self, parent1: List[Player], parent2: List[Player]) -> List[Player]:
        """
        Order crossover (OX): Preserves relative order while mixing parents
        Takes a segment from parent1 and fills remaining positions with parent2's order
        """
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child with segment from parent1
        child = [None] * size
        child[start:end] = parent1[start:end]
        
        # Fill remaining positions with parent2's order
        parent2_filtered = [p for p in parent2 if p not in child[start:end]]
        
        # Fill positions before the segment
        p2_idx = 0
        for i in range(start):
            child[i] = parent2_filtered[p2_idx]
            p2_idx += 1
        
        # Fill positions after the segment
        for i in range(end, size):
            child[i] = parent2_filtered[p2_idx]
            p2_idx += 1
        
        return child
    
    def swap_mutation(self, lineup: List[Player]) -> List[Player]:
        """Swap two random positions in the lineup"""
        if random.random() < self.mutation_rate:
            lineup = lineup.copy()
            i, j = random.sample(range(len(lineup)), 2)
            lineup[i], lineup[j] = lineup[j], lineup[i]
        return lineup
    
    def evolve_generation(self, num_games: int, innings: int = 6) -> Tuple[List[float], float]:
        """Evolve one generation and return fitness scores and best fitness"""
        # Evaluate fitness for current population
        fitness_scores = []
        for lineup in self.population:
            fitness = self.evaluate_fitness(lineup, num_games, innings)
            fitness_scores.append(fitness)
        
        # Create next generation
        new_population = []
        
        # Elitism: Keep best individual
        best_idx = fitness_scores.index(max(fitness_scores))
        new_population.append(self.population[best_idx].copy())
        
        # Generate rest of population through crossover and mutation
        while len(new_population) < self.population_size:
            parent1 = self.tournament_selection(self.population, fitness_scores)
            parent2 = self.tournament_selection(self.population, fitness_scores)
            
            child = self.order_crossover(parent1, parent2)
            child = self.swap_mutation(child)
            
            new_population.append(child)
        
        self.population = new_population
        return fitness_scores, max(fitness_scores)
    
    def optimize(self, generations: int, num_games: int, innings: int = 6, 
                verbose: bool = True) -> List[LineupResult]:
        """Run the genetic algorithm optimization"""
        self.initialize_population()
        
        if verbose:
            print(f"Genetic Algorithm Parameters:")
            print(f"Population size: {self.population_size}")
            print(f"Generations: {generations}")
            print(f"Mutation rate: {self.mutation_rate}")
            print(f"Tournament size: {self.tournament_size}")
            print(f"Games per evaluation: {num_games}")
            print("-" * 60)
        
        best_fitness_history = []
        
        for generation in range(generations):
            fitness_scores, best_fitness = self.evolve_generation(num_games, innings)
            best_fitness_history.append(best_fitness)
            
            if verbose and (generation + 1) % 10 == 0:
                avg_fitness = statistics.mean(fitness_scores)
                print(f"Generation {generation + 1:3d}: Best={best_fitness:.2f}, Avg={avg_fitness:.2f}")
        
        # Final evaluation with more games for better statistics
        final_results = []
        final_fitness_scores = []
        
        for lineup in self.population:
            result = evaluate_lineup(lineup, num_games * 2, innings)  # More games for final eval
            final_results.append(result)
            final_fitness_scores.append(result.mean_runs)
        
        # Sort by fitness
        sorted_results = sorted(final_results, key=lambda x: x.mean_runs, reverse=True)
        
        if verbose:
            print(f"\nEvolution complete!")
            print(f"Best fitness improved from ~{best_fitness_history[0]:.2f} to {max(final_fitness_scores):.2f}")
        
        return sorted_results


def main():
    parser = argparse.ArgumentParser(description='Optimize baseball lineups using genetic algorithm')
    parser.add_argument('-g', '--generations', type=int, default=50,
                       help='Number of generations to evolve (default: 50)')
    parser.add_argument('-p', '--population', type=int, default=50,
                       help='Population size (default: 50)')
    parser.add_argument('-ng', '--num-games', type=int, default=10,
                       help='Number of games to simulate per evaluation (default: 10)')
    parser.add_argument('-tn', '--top-n', type=int, default=10,
                       help='Number of top lineups to report (default: 10)')
    parser.add_argument('-ls', '--lineup-size', type=int, default=9,
                       help='Size of each lineup (default: 9)')
    parser.add_argument('-i', '--innings', type=int, default=6,
                       help='Number of innings per game (default: 6)')
    parser.add_argument('-f', '--file', type=str, default='lineup_example.csv',
                       help='CSV file containing player data (default: lineup_example.csv)')
    parser.add_argument('-m', '--mutation-rate', type=float, default=0.1,
                       help='Mutation rate (default: 0.1)')
    parser.add_argument('-t', '--tournament-size', type=int, default=3,
                       help='Tournament size for selection (default: 3)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare genetic algorithm with random search')
    
    args = parser.parse_args()
    
    # Load players
    try:
        players = load_players(args.file)
        print(f"Loaded {len(players)} players from {args.file}")
        print(f"Available players: {', '.join([p.name for p in players])}")
        print()
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.file}'")
        return
    except Exception as e:
        print(f"Error loading players: {e}")
        return
    
    # Validate lineup size
    if args.lineup_size > len(players):
        print(f"Warning: Lineup size ({args.lineup_size}) is larger than available players ({len(players)})")
        print(f"Using all {len(players)} players in each lineup")
        args.lineup_size = len(players)
    
    # Run genetic algorithm
    ga_optimizer = GeneticLineupOptimizer(
        players=players,
        lineup_size=args.lineup_size,
        population_size=args.population,
        mutation_rate=args.mutation_rate,
        tournament_size=args.tournament_size
    )
    
    ga_results = ga_optimizer.optimize(
        generations=args.generations,
        num_games=args.num_games,
        innings=args.innings,
        verbose=True
    )
    
    # Display results
    print(f"\nTop {min(args.top_n, len(ga_results))} Genetic Algorithm Results:")
    print("=" * 80)
    for i, result in enumerate(ga_results[:args.top_n], 1):
        print(f"{i:2d}. {result}")
    
    # Compare with random search if requested
    if args.compare:
        print(f"\nComparing with random search...")
        from lineup_optimizer import optimize_lineups
        
        random_results = optimize_lineups(
            players=players,
            num_lineups=args.population * args.generations // 10,  # Similar total evaluations
            num_games=args.num_games,
            top_n=1,
            lineup_size=args.lineup_size,
            innings=args.innings
        )
        
        print(f"\nComparison:")
        print(f"GA Best:     {ga_results[0].mean_runs:.2f} ± {ga_results[0].std_dev:.2f}")
        print(f"Random Best: {random_results[0].mean_runs:.2f} ± {random_results[0].std_dev:.2f}")
        improvement = ga_results[0].mean_runs - random_results[0].mean_runs
        print(f"GA Improvement: {improvement:+.2f} runs per game")


if __name__ == "__main__":
    main()