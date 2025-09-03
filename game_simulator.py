import csv
import random
from typing import Dict, List, Tuple


class Player:
    def __init__(self, name: str, ab: int, singles: int, doubles: int, triples: int, homers: int):
        self.name = name
        self.ab = ab
        self.singles = singles
        self.doubles = doubles
        self.triples = triples
        self.homers = homers
        self.hits = singles + doubles + triples + homers
        self.outs = ab - self.hits
        
    def __str__(self):
        return f"{self.name}: {self.hits}/{self.ab} (.{int(1000*self.hits/self.ab):03d})"


def load_players(filename: str) -> List[Player]:
    """Load players from CSV file"""
    players = []
    with open(filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Player']:  # Skip empty rows
                players.append(Player(
                    name=row['Player'],
                    ab=int(row['AB']),
                    singles=int(row['1B']),
                    doubles=int(row['2B']),
                    triples=int(row['3B']),
                    homers=int(row['HR'])
                ))
    return players


def player_hit(player: Player) -> str:
    """
    Simulate a player's at-bat using weighted random selection based on their stats.
    Returns: 'out', '1B', '2B', '3B', or 'HR'
    """
    outcomes = ['out'] * player.outs + ['1B'] * player.singles + ['2B'] * player.doubles + ['3B'] * player.triples + ['HR'] * player.homers
    return random.choice(outcomes)


def simulate_inning(lineup: List[Player], batter_index: int) -> Tuple[int, int]:
    """
    Simulate one inning. Returns (runs_scored, next_batter_index)
    """
    bases = [None, None, None]  # [1B, 2B, 3B]
    outs = 0
    runs = 0
    current_batter = batter_index
    
    while outs < 3:
        player = lineup[current_batter]
        result = player_hit(player)
        
        if result == 'out':
            outs += 1
        elif result == '1B':
            # Runner on 3B scores
            if bases[2]:
                runs += 1
            # Advance all runners
            bases[2] = bases[1]  # 2B -> 3B
            bases[1] = bases[0]  # 1B -> 2B
            bases[0] = player    # Batter to 1B
        elif result == '2B':
            # Runners on 2B and 3B score
            if bases[1]:
                runs += 1
            if bases[2]:
                runs += 1
            # Advance runners
            bases[2] = bases[0]  # 1B -> 3B
            bases[1] = player    # Batter to 2B
            bases[0] = None
        elif result == '3B':
            # All runners score
            runs += sum(1 for base in bases if base is not None)
            # Clear bases and put batter on 3B
            bases = [None, None, player]
        elif result == 'HR':
            # Everyone scores including batter
            runs += sum(1 for base in bases if base is not None) + 1
            # Clear all bases
            bases = [None, None, None]
        
        current_batter = (current_batter + 1) % len(lineup)
    
    return runs, current_batter


def simulate_game(lineup: List[Player], innings: int = 6) -> Dict:
    """Simulate a complete game and return results"""
    total_runs = 0
    inning_scores = []
    batter_index = 0
    
    for inning in range(innings):
        runs, batter_index = simulate_inning(lineup, batter_index)
        total_runs += runs
        inning_scores.append(runs)
    
    return {
        'total_runs': total_runs,
        'inning_scores': inning_scores,
        'lineup': [player.name for player in lineup]
    }


def main():
    # Load players
    players = load_players('lineup_example.csv')
    
    print("Loaded players:")
    for player in players:
        print(f"  {player}")
    
    print(f"\nSimulating game with {len(players)} players, 6 innings...")
    
    # Simulate game
    result = simulate_game(players, 6)
    
    print(f"\nGame Results:")
    print(f"Total Runs: {result['total_runs']}")
    print(f"Inning Scores: {result['inning_scores']}")
    print(f"Lineup: {', '.join(result['lineup'])}")


if __name__ == "__main__":
    main()