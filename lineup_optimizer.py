import argparse
import random
import statistics
from typing import List, Dict, Tuple
from game_simulator import Player, load_players, simulate_game


class LineupResult:
    def __init__(self, lineup: List[Player], runs_per_game: List[int]):
        self.lineup = lineup
        self.runs_per_game = runs_per_game
        self.mean_runs = statistics.mean(runs_per_game)
        self.std_dev = statistics.stdev(runs_per_game) if len(runs_per_game) > 1 else 0.0
        self.total_games = len(runs_per_game)
    
    def __str__(self):
        lineup_names = [player.name for player in self.lineup]
        return f"Mean: {self.mean_runs:.2f} ± {self.std_dev:.2f} | Lineup: {', '.join(lineup_names)}"


def generate_random_lineup(players: List[Player], lineup_size: int = 9) -> List[Player]:
    """Generate a random lineup by sampling players without replacement"""
    if lineup_size > len(players):
        lineup_size = len(players)
    return random.sample(players, lineup_size)


def evaluate_lineup(lineup: List[Player], num_games: int, innings: int = 6) -> LineupResult:
    """Evaluate a lineup by running multiple game simulations"""
    runs_per_game = []
    
    for _ in range(num_games):
        game_result = simulate_game(lineup, innings)
        runs_per_game.append(game_result['total_runs'])
    
    return LineupResult(lineup, runs_per_game)


def optimize_lineups(players: List[Player], num_lineups: int, num_games: int, 
                    top_n: int, lineup_size: int = 9, innings: int = 6) -> List[LineupResult]:
    """
    Generate and evaluate random lineups to find the best performers
    """
    results = []
    
    print(f"Evaluating {num_lineups} random lineups...")
    print(f"Each lineup plays {num_games} games of {innings} innings")
    print(f"Lineup size: {lineup_size} players")
    print("-" * 60)
    
    for i in range(num_lineups):
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_lineups} lineups evaluated")
        
        # Generate random lineup
        lineup = generate_random_lineup(players, lineup_size)
        
        # Evaluate lineup performance
        result = evaluate_lineup(lineup, num_games, innings)
        results.append(result)
    
    # Sort by mean runs (descending)
    results.sort(key=lambda x: x.mean_runs, reverse=True)
    
    return results[:top_n]


def main():
    parser = argparse.ArgumentParser(description='Optimize baseball lineups through simulation')
    parser.add_argument('-nl', '--num-lineups', type=int, default=100,
                       help='Number of random lineups to generate (default: 100)')
    parser.add_argument('-ng', '--num-games', type=int, default=10,
                       help='Number of games to simulate per lineup (default: 10)')
    parser.add_argument('-tn', '--top-n', type=int, default=10,
                       help='Number of top lineups to report (default: 10)')
    parser.add_argument('-ls', '--lineup-size', type=int, default=9,
                       help='Size of each lineup (default: 9)')
    parser.add_argument('-i', '--innings', type=int, default=6,
                       help='Number of innings per game (default: 6)')
    parser.add_argument('-f', '--file', type=str, default='lineup_example.csv',
                       help='CSV file containing player data (default: lineup_example.csv)')
    
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
    
    # Run optimization
    top_lineups = optimize_lineups(
        players=players,
        num_lineups=args.num_lineups,
        num_games=args.num_games,
        top_n=args.top_n,
        lineup_size=args.lineup_size,
        innings=args.innings
    )
    
    # Display results
    print(f"\nTop {len(top_lineups)} Lineups:")
    print("=" * 80)
    for i, result in enumerate(top_lineups, 1):
        print(f"{i:2d}. {result}")
    
    # Summary statistics
    if top_lineups:
        best_lineup = top_lineups[0]
        print(f"\nBest Lineup Details:")
        print(f"Mean runs per game: {best_lineup.mean_runs:.3f}")
        print(f"Standard deviation: {best_lineup.std_dev:.3f}")
        print(f"Games simulated: {best_lineup.total_games}")
        print(f"Total runs in all games: {sum(best_lineup.runs_per_game)}")
        print(f"Run distribution: Min={min(best_lineup.runs_per_game)}, Max={max(best_lineup.runs_per_game)}")


if __name__ == "__main__":
    main()