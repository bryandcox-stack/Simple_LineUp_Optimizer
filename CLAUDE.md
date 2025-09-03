# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Baseball Lineup Optimizer that uses statistical simulation and genetic algorithms to find optimal batting orders. The system simulates games to determine which lineup configurations generate the most runs.

## Key Components

- `game_simulator.py`: Core game simulation engine with player statistics and at-bat logic
- `lineup_optimizer.py`: Random lineup search and evaluation
- `genetic_optimizer.py`: Genetic algorithm for lineup evolution
- `master_optimizer.py`: Main script combining random search + genetic algorithm
- `lineup_example.csv`: Sample player data
- `lineups_optimized.csv`: Generated optimization results

## Development Commands

### Running Optimizations
```bash
# Basic optimization (default settings)
python master_optimizer.py

# Quick test
python master_optimizer.py -nr 50 -g 20 -ng 10

# Extensive optimization  
python master_optimizer.py -nr 500 -g 100 -p 100 -ng 25

# Reproducible results
python master_optimizer.py --seed 12345
```

### Testing Individual Components
```bash
# Test game simulator
python game_simulator.py

# Test random optimization
python lineup_optimizer.py -nl 100 -ng 10

# Test genetic algorithm
python genetic_optimizer.py -g 30 -p 40
```

## Data Format

Input CSV requires these columns:
- Player: Player name
- AB: At bats (total)
- 1B: Singles hit
- 2B: Doubles hit  
- 3B: Triples hit
- HR: Home runs hit

System calculates: `Outs = AB - (1B + 2B + 3B + HR)`

## Architecture

### Game Simulation
- `player_hit()`: Weighted random selection based on player stats
- `simulate_inning()`: Runs until 3 outs, handles base running
- `simulate_game()`: Multiple innings with cycling lineup

### Optimization Methods
1. **Random Search**: Broad exploration of lineup permutations
2. **Genetic Algorithm**: Focused optimization using:
   - Tournament selection
   - Order crossover (preserves batting positions)
   - Swap mutation
   - Elitism (keeps best performers)

### Result Processing
- Combines random + GA results
- Ranks by mean runs per game
- Saves statistics and lineups to CSV
- Tracks which method found each top performer

## Key Dependencies

Uses only Python standard library:
- `csv`, `random`, `statistics`, `argparse`, `time`, `typing`
- No external packages required

## Limitations

This is a simplified simulation that does NOT include:
- Stolen bases or base stealing
- Double plays or defensive complexity  
- Pitcher-specific batting averages
- Situational hitting statistics
- Advanced baseball strategy

Focus is on batting order optimization using historical hitting statistics.