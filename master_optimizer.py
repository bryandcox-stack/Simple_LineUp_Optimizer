#!/usr/bin/env python3
"""
Master Lineup Optimizer - Combines Random Search + Genetic Algorithm

This script performs a two-phase optimization:
1. Random Search Phase: Generates many random lineups to find good starting points
2. Genetic Algorithm Phase: Evolves the best random lineups to find optimal solutions

The hybrid approach combines the broad exploration of random search with the 
focused exploitation of genetic algorithms for superior results.
"""

import argparse
import time
import random
import statistics
import csv
from typing import List, Dict, Tuple, Optional
from game_simulator import Player, load_players, simulate_game
from lineup_optimizer import LineupResult, evaluate_lineup, optimize_lineups
from genetic_optimizer import GeneticLineupOptimizer


class MasterLineupOptimizer:
    def __init__(self, players: List[Player], seed: Optional[int] = None):
        self.players = players
        self.seed = seed
        self.results = {
            'random_phase': None,
            'ga_phase': None,
            'best_overall': None,
            'timing': {},
            'seed': seed
        }
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            print(f"Random seed set to: {seed}")
        else:
            # Generate and use a random seed for reproducibility
            self.seed = random.randint(1, 1000000)
            random.seed(self.seed)
            self.results['seed'] = self.seed
            print(f"Generated random seed: {self.seed}")
    
    def run_random_phase(self, num_lineups: int, num_games: int, lineup_size: int, 
                        innings: int, seed_size: int, verbose: bool = True) -> List[LineupResult]:
        """Phase 1: Random search to find good starting lineups"""
        if verbose:
            print("=" * 80)
            print("PHASE 1: RANDOM SEARCH INITIALIZATION")
            print("=" * 80)
        
        start_time = time.time()
        
        random_results = optimize_lineups(
            players=self.players,
            num_lineups=num_lineups,
            num_games=num_games,
            top_n=seed_size,
            lineup_size=lineup_size,
            innings=innings
        )
        
        elapsed = time.time() - start_time
        self.results['timing']['random_phase'] = elapsed
        self.results['random_phase'] = random_results
        
        if verbose:
            print(f"\nRandom Phase Complete!")
            print(f"Evaluated {num_lineups} random lineups in {elapsed:.1f} seconds")
            print(f"Best random lineup: {random_results[0].mean_runs:.2f} ± {random_results[0].std_dev:.2f} runs")
            print(f"Selected top {len(random_results)} lineups for genetic optimization")
        
        return random_results
    
    def run_genetic_phase(self, seed_lineups: List[LineupResult], population_size: int,
                         generations: int, num_games: int, lineup_size: int, innings: int,
                         mutation_rate: float, tournament_size: int, verbose: bool = True) -> List[LineupResult]:
        """Phase 2: Genetic algorithm starting from best random lineups"""
        if verbose:
            print(f"\n{'=' * 80}")
            print("PHASE 2: GENETIC ALGORITHM OPTIMIZATION")
            print("=" * 80)
        
        start_time = time.time()
        
        # Create custom GA optimizer with seeded population
        ga_optimizer = GeneticLineupOptimizer(
            players=self.players,
            lineup_size=lineup_size,
            population_size=population_size,
            mutation_rate=mutation_rate,
            tournament_size=tournament_size
        )
        
        # Seed population with best random lineups
        ga_optimizer.population = []
        for result in seed_lineups:
            ga_optimizer.population.append(result.lineup.copy())
        
        # Fill remaining population with random lineups
        while len(ga_optimizer.population) < population_size:
            random_lineup = ga_optimizer.create_random_lineup()
            ga_optimizer.population.append(random_lineup)
        
        # Run genetic algorithm
        ga_results = ga_optimizer.optimize(
            generations=generations,
            num_games=num_games,
            innings=innings,
            verbose=verbose
        )
        
        elapsed = time.time() - start_time
        self.results['timing']['ga_phase'] = elapsed
        self.results['ga_phase'] = ga_results
        
        if verbose:
            print(f"\nGenetic Phase Complete!")
            print(f"Evolved {generations} generations in {elapsed:.1f} seconds")
            if seed_lineups:
                improvement = ga_results[0].mean_runs - seed_lineups[0].mean_runs
                print(f"Improvement over best random: {improvement:+.2f} runs per game")
        
        return ga_results
    
    def optimize(self, num_random_lineups: int = 200, seed_size: int = 20,
                population_size: int = 50, generations: int = 50, num_games: int = 15,
                lineup_size: int = 9, innings: int = 6, mutation_rate: float = 0.1,
                tournament_size: int = 3, verbose: bool = True) -> Dict:
        """Run complete optimization workflow"""
        
        total_start = time.time()
        
        if verbose:
            print("MASTER LINEUP OPTIMIZER")
            print("Hybrid Random Search + Genetic Algorithm")
            print("=" * 80)
            print(f"Random Seed: {self.seed}")
            print(f"Dataset: {len(self.players)} players")
            print(f"Lineup size: {lineup_size} players")
            print(f"Game length: {innings} innings")
            print(f"Games per evaluation: {num_games}")
            print()
            print("Optimization Strategy:")
            print(f"1. Random search: {num_random_lineups} lineups")
            print(f"2. Select top {seed_size} for genetic seeding")
            print(f"3. Genetic algorithm: {generations} generations, population {population_size}")
            print()
        
        # Phase 1: Random Search
        random_results = self.run_random_phase(
            num_lineups=num_random_lineups,
            num_games=num_games,
            lineup_size=lineup_size,
            innings=innings,
            seed_size=seed_size,
            verbose=verbose
        )
        
        # Phase 2: Genetic Algorithm
        ga_results = self.run_genetic_phase(
            seed_lineups=random_results,
            population_size=population_size,
            generations=generations,
            num_games=num_games,
            lineup_size=lineup_size,
            innings=innings,
            mutation_rate=mutation_rate,
            tournament_size=tournament_size,
            verbose=verbose
        )
        
        # Final analysis - combine and sort all results
        all_results = list(random_results) + list(ga_results)
        all_results.sort(key=lambda x: x.mean_runs, reverse=True)
        
        total_elapsed = time.time() - total_start
        self.results['timing']['total'] = total_elapsed
        self.results['best_overall'] = all_results[0] if all_results else None
        self.results['all_combined'] = all_results
        
        if verbose:
            self.print_final_summary()
        
        return {
            'best_lineup': self.results['best_overall'],
            'ga_results': ga_results,
            'random_results': random_results,
            'all_combined': all_results,
            'timing': self.results['timing']
        }
    
    def print_final_summary(self):
        """Print comprehensive optimization summary"""
        print(f"\n{'=' * 80}")
        print("OPTIMIZATION COMPLETE - FINAL SUMMARY")
        print("=" * 80)
        
        timing = self.results['timing']
        print(f"Total Time: {timing['total']:.1f} seconds")
        print(f"  Random Phase: {timing['random_phase']:.1f}s")
        print(f"  Genetic Phase: {timing['ga_phase']:.1f}s")
        print()
        
        random_best = self.results['random_phase'][0]
        ga_best = self.results['ga_phase'][0]
        
        print("Performance Comparison:")
        print(f"Best Random:  {random_best.mean_runs:.3f} ± {random_best.std_dev:.3f} runs/game")
        print(f"Best Genetic: {ga_best.mean_runs:.3f} ± {ga_best.std_dev:.3f} runs/game")
        
        improvement = ga_best.mean_runs - random_best.mean_runs
        pct_improvement = (improvement / random_best.mean_runs) * 100
        print(f"Improvement:  {improvement:+.3f} runs/game ({pct_improvement:+.1f}%)")
        
        print(f"\nOPTIMAL LINEUP:")
        best_overall = self.results['best_overall']
        lineup_names = [player.name for player in best_overall.lineup]
        for i, name in enumerate(lineup_names, 1):
            print(f"{i:2d}. {name}")
        
        # Show which method found the best lineup
        random_results = self.results['random_phase']
        ga_results = self.results['ga_phase']
        source = "Genetic Algorithm" if best_overall in ga_results else "Random Search"
        print(f"Best lineup found by: {source}")
        
        print(f"\nReproducibility:")
        print(f"Random seed used: {self.seed}")
        print(f"Use --seed {self.seed} to reproduce these exact results")
    
    def save_lineups_to_csv(self, results: List[LineupResult], filename: str, 
                           num_to_save: int, metadata: Dict) -> None:
        """Save top lineups and their statistics to CSV file"""
        if not results:
            print(f"No results to save to {filename}")
            return
        
        results_to_save = results[:min(num_to_save, len(results))]
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with metadata
            writer.writerow(['# Lineup Optimization Results'])
            writer.writerow([f'# Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([f'# Random Seed: {metadata.get("seed", "N/A")}'])
            writer.writerow([f'# Total Players: {metadata.get("total_players", "N/A")}'])
            writer.writerow([f'# Lineup Size: {metadata.get("lineup_size", "N/A")}'])
            writer.writerow([f'# Games Per Evaluation: {metadata.get("num_games", "N/A")}'])
            writer.writerow([f'# Innings Per Game: {metadata.get("innings", "N/A")}'])
            writer.writerow([''])  # Empty row
            
            # Write column headers
            headers = ['Rank', 'Mean_Runs', 'Std_Dev', 'Total_Games', 'Min_Runs', 'Max_Runs']
            # Add position headers (1st, 2nd, 3rd, etc.)
            lineup_size = len(results_to_save[0].lineup) if results_to_save else 9
            for i in range(1, lineup_size + 1):
                headers.append(f'Pos_{i}')
            
            writer.writerow(headers)
            
            # Write data rows
            for rank, result in enumerate(results_to_save, 1):
                row = [
                    rank,
                    f'{result.mean_runs:.3f}',
                    f'{result.std_dev:.3f}',
                    result.total_games,
                    min(result.runs_per_game),
                    max(result.runs_per_game)
                ]
                
                # Add player names for each position
                for player in result.lineup:
                    row.append(player.name)
                
                writer.writerow(row)
        
        print(f"\nSaved top {len(results_to_save)} lineups to: {filename}")
        print(f"File includes statistical performance and lineup configurations")


def main():
    parser = argparse.ArgumentParser(
        description='Master Lineup Optimizer - Hybrid Random Search + Genetic Algorithm',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data and basic parameters
    parser.add_argument('-f', '--file', type=str, default='lineup_example.csv',
                       help='CSV file containing player data')
    parser.add_argument('-ls', '--lineup-size', type=int, default=9,
                       help='Size of each lineup')
    parser.add_argument('-i', '--innings', type=int, default=6,
                       help='Number of innings per game')
    parser.add_argument('-ng', '--num-games', type=int, default=15,
                       help='Number of games to simulate per lineup evaluation')
    
    # Random search phase parameters
    parser.add_argument('-nr', '--num-random', type=int, default=200,
                       help='Number of random lineups to generate in Phase 1')
    parser.add_argument('-ss', '--seed-size', type=int, default=20,
                       help='Number of best random lineups to seed GA population')
    
    # Genetic algorithm phase parameters
    parser.add_argument('-g', '--generations', type=int, default=50,
                       help='Number of generations to evolve in Phase 2')
    parser.add_argument('-p', '--population', type=int, default=50,
                       help='Population size for genetic algorithm')
    parser.add_argument('-m', '--mutation-rate', type=float, default=0.1,
                       help='Mutation rate for genetic algorithm (0.0-1.0)')
    parser.add_argument('-t', '--tournament-size', type=int, default=3,
                       help='Tournament size for genetic algorithm selection')
    
    # Output parameters
    parser.add_argument('-tn', '--top-n', type=int, default=10,
                       help='Number of top lineups to display in results')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Reduce output verbosity')
    
    # Output and saving options
    parser.add_argument('--random-only', action='store_true',
                       help='Run only random search phase (skip genetic algorithm)')
    parser.add_argument('--save-csv', type=str, default='lineups_optimized.csv',
                       help='CSV file to save top lineups (default: lineups_optimized.csv)')
    parser.add_argument('--no-save', action='store_true',
                       help='Skip saving results to CSV file')
    parser.add_argument('-sn', '--save-num', type=int, default=25,
                       help='Number of top lineups to save to CSV (default: 25)')
    parser.add_argument('--save-results', type=str, metavar='FILE',
                       help='Save detailed results to specified file (deprecated)')
    
    # Reproducibility
    parser.add_argument('-s', '--seed', type=int, default=None,
                       help='Random seed for reproducible results (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Load players
    try:
        players = load_players(args.file)
        if not args.quiet:
            print(f"Loaded {len(players)} players from {args.file}")
            player_names = [p.name for p in players]
            print(f"Players: {', '.join(player_names)}")
            print()
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.file}'")
        return 1
    except Exception as e:
        print(f"Error loading players: {e}")
        return 1
    
    # Validate parameters
    if args.lineup_size > len(players):
        print(f"Warning: Lineup size ({args.lineup_size}) > available players ({len(players)})")
        print(f"Using all {len(players)} players")
        args.lineup_size = len(players)
    
    if args.seed_size > args.population:
        print(f"Warning: Seed size ({args.seed_size}) > population size ({args.population})")
        args.seed_size = args.population
    
    # Create and run optimizer
    optimizer = MasterLineupOptimizer(players, seed=args.seed)
    
    if args.random_only:
        # Run only random search
        results = optimizer.run_random_phase(
            num_lineups=args.num_random,
            num_games=args.num_games,
            lineup_size=args.lineup_size,
            innings=args.innings,
            seed_size=args.top_n,
            verbose=not args.quiet
        )
        
        print(f"\nTop {len(results)} Random Search Results:")
        print("=" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i:2d}. {result}")
        
        # Save random-only results to CSV
        if not args.no_save:
            metadata = {
                'seed': optimizer.seed,
                'total_players': len(players),
                'lineup_size': args.lineup_size,
                'num_games': args.num_games,
                'innings': args.innings
            }
            optimizer.save_lineups_to_csv(results, args.save_csv, args.save_num, metadata)
    else:
        # Run complete optimization
        results = optimizer.optimize(
            num_random_lineups=args.num_random,
            seed_size=args.seed_size,
            population_size=args.population,
            generations=args.generations,
            num_games=args.num_games,
            lineup_size=args.lineup_size,
            innings=args.innings,
            mutation_rate=args.mutation_rate,
            tournament_size=args.tournament_size,
            verbose=not args.quiet
        )
        
        # Display top results (combined from both phases)
        if not args.quiet:
            print(f"\nTop {args.top_n} Final Results (Combined Random + GA):")
            print("=" * 80)
            all_combined = results['all_combined']
            for i, result in enumerate(all_combined[:args.top_n], 1):
                source = "GA" if result in results['ga_results'] else "Random"
                print(f"{i:2d}. [{source:6}] {result}")
        
        # Save results to CSV (combined random + GA results)
        if not args.no_save:
            final_results = results['all_combined']  # Use combined results instead of just GA
            metadata = {
                'seed': optimizer.seed,
                'total_players': len(players),
                'lineup_size': args.lineup_size,
                'num_games': args.num_games,
                'innings': args.innings
            }
            optimizer.save_lineups_to_csv(final_results, args.save_csv, args.save_num, metadata)
    
    return 0


if __name__ == "__main__":
    exit(main())