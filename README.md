# Baseball Lineup Optimizer

A Python-based baseball lineup optimization system that uses statistical simulation and genetic algorithms to find the best batting order combinations. The system simulates games to determine which lineup configurations generate the most runs.

## Overview

This project contains a simplified baseball simulation that focuses on optimizing batting lineups. The simulation **does not account for**:
- Stolen bases
- Double plays  
- Batting averages against different pitch types
- Advanced defensive metrics
- Situational hitting statistics

Instead, it uses historical hitting statistics (singles, doubles, triples, home runs, at-bats) to simulate at-bat outcomes and optimize batting order through:

1. **Random Search**: Broad exploration of possible lineups
2. **Genetic Algorithm**: Focused optimization of promising lineups
3. **Statistical Analysis**: Performance tracking with mean/standard deviation

## Files Structure

```
LineUp_Optimizer/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── CLAUDE.md                 # Development documentation
├── lineup_example.csv        # Sample player data
├── game_simulator.py         # Core game simulation engine
├── lineup_optimizer.py       # Random lineup search
├── genetic_optimizer.py      # Genetic algorithm optimization
├── master_optimizer.py       # Main optimization script
└── lineups_optimized.csv     # Generated optimization results
```

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Run with default settings**:
   ```bash
   python master_optimizer.py
   ```
   This will:
   - Generate 200 random lineups
   - Use the top 20 to seed a genetic algorithm
   - Evolve for 50 generations with population of 50
   - Save top 25 lineups to `lineups_optimized.csv`

2. **View results**:
   ```bash
   # Terminal output shows optimization progress and top lineups
   # CSV file contains detailed statistics for all top lineups
   ```

## Data Format

### Input CSV Format
Your player data CSV should have these columns:
```csv
Player,AB,1B,2B,3B,HR
Matt,535,144,36,1,21
Ozzie,533,127,21,1,14
...
```

Where:
- **Player**: Player name
- **AB**: At bats (total plate appearances)
- **1B**: Singles hit
- **2B**: Doubles hit  
- **3B**: Triples hit
- **HR**: Home runs hit

The system calculates outs as: `Outs = AB - (1B + 2B + 3B + HR)`

### Output CSV Format
The generated `lineups_optimized.csv` contains:
```csv
Rank,Mean_Runs,Std_Dev,Total_Games,Min_Runs,Max_Runs,Pos_1,Pos_2,Pos_3,...
1,4.633,3.419,30,0,13,Drake,Matt,Eli,Austin,Mike,...
```

## Usage Examples

### Basic Usage
```bash
# Use default settings
python master_optimizer.py

# Specify input file
python master_optimizer.py -f my_players.csv

# Quick test with fewer evaluations
python master_optimizer.py -nr 50 -g 20 -ng 10
```

### Reproducible Results
```bash
# Set random seed for reproducible results
python master_optimizer.py --seed 12345

# Run again with same seed to get identical results
python master_optimizer.py --seed 12345
```

### Custom Parameters
```bash
# Extensive optimization
python master_optimizer.py -nr 500 -g 100 -p 100 -ng 25

# Save more lineups
python master_optimizer.py -sn 50 --save-csv my_results.csv

# Random search only (skip genetic algorithm)
python master_optimizer.py --random-only -nr 1000
```

### Analysis Options
```bash
# Quiet mode (minimal output)
python master_optimizer.py -q

# Skip saving results
python master_optimizer.py --no-save

# Display more top lineups
python master_optimizer.py -tn 20
```

## Command Line Arguments

### Data & Basic Parameters
- `-f, --file`: Input CSV file (default: `lineup_example.csv`)
- `-ls, --lineup-size`: Players per lineup (default: `9`)
- `-i, --innings`: Innings per game (default: `6`) 
- `-ng, --num-games`: Games per evaluation (default: `15`)

### Random Search Phase
- `-nr, --num-random`: Random lineups to generate (default: `200`)
- `-ss, --seed-size`: Best random lineups for GA seeding (default: `20`)

### Genetic Algorithm Phase  
- `-g, --generations`: GA generations (default: `50`)
- `-p, --population`: GA population size (default: `50`)
- `-m, --mutation-rate`: Mutation probability 0.0-1.0 (default: `0.1`)
- `-t, --tournament-size`: Tournament selection size (default: `3`)

### Output Options
- `-tn, --top-n`: Top lineups to display (default: `10`)
- `--save-csv`: Output CSV filename (default: `lineups_optimized.csv`)
- `-sn, --save-num`: Number of lineups to save (default: `25`)
- `--no-save`: Skip CSV output
- `-q, --quiet`: Reduce output verbosity

### Control Options
- `-s, --seed`: Random seed for reproducibility (default: auto-generated)
- `--random-only`: Skip genetic algorithm phase

## How It Works

### 1. Game Simulation
Each at-bat uses weighted random selection based on player statistics:
- Player with 400 AB, 100 singles, 20 doubles, 5 HR has: 275 outs, 100 singles, etc.
- Random selection weighted by these frequencies determines at-bat outcome

### 2. Base Running
Simplified base running logic:
- Singles advance all runners one base
- Doubles score runners from 2B and 3B  
- Triples score all runners on base
- Home runs score everyone including batter
- Runners score when reaching home plate

### 3. Inning Structure  
- Each inning continues until 3 outs are recorded
- Lineup cycles through all players in batting order
- No substitutions or pinch hitters

### 4. Optimization Process

**Phase 1 - Random Search:**
- Generates many random lineup permutations
- Simulates multiple games per lineup
- Calculates mean runs and standard deviation
- Identifies top-performing lineups

**Phase 2 - Genetic Algorithm:**
- Seeds population with best random lineups
- Uses tournament selection for parents
- Order crossover preserves batting position relationships
- Swap mutation exchanges player positions
- Evolves toward higher-scoring lineups

**Phase 3 - Results:**
- Combines and ranks all lineups from both phases
- Saves top performers with complete statistics
- Shows which method found each top lineup

### 5. Statistical Analysis
Each lineup is evaluated across multiple games to provide:
- **Mean runs per game**: Average scoring performance
- **Standard deviation**: Consistency measure  
- **Min/Max runs**: Performance range
- **Sample size**: Number of games simulated

## Interpreting Results

### Terminal Output
```
OPTIMAL LINEUP:
 1. Drake
 2. Matt  
 3. Eli
 4. Austin
 ...
Best lineup found by: Genetic Algorithm

Top 5 Final Results (Combined Random + GA):
 1. [GA    ] Mean: 4.63 ± 3.42 | Lineup: Drake, Matt, Eli, Austin...
 2. [Random] Mean: 4.40 ± 2.47 | Lineup: Mike, Drake, Matt, Ron...
```

### CSV Analysis
- **Rank**: Overall performance ranking
- **Mean_Runs**: Average runs per game (higher is better)
- **Std_Dev**: Variability (lower suggests more consistent)  
- **Pos_1 through Pos_9**: Batting order from leadoff to 9th

### Performance Considerations
- **Higher mean**: Better offensive production
- **Lower std dev**: More predictable scoring
- **Sample size**: More games = more reliable statistics
- **Method source**: GA vs Random indicates optimization effectiveness

## Limitations & Assumptions

This is a **simplified simulation** with these limitations:

### What's NOT Included:
- ❌ Stolen bases and base stealing
- ❌ Double plays and fielding errors
- ❌ Pitcher-specific batting averages
- ❌ Situational hitting (RISP, clutch performance)
- ❌ Ballpark effects and weather conditions
- ❌ Fatigue and player condition
- ❌ In-game strategy and substitutions

### What IS Included:
- ✅ Historical hitting statistics simulation
- ✅ Base running advancement logic
- ✅ Batting order optimization
- ✅ Statistical performance analysis
- ✅ Multiple optimization algorithms

### Key Assumptions:
- Player performance is consistent across all at-bats
- Historical statistics predict future performance
- Batting order significantly impacts run production
- Simplified game rules provide meaningful optimization insights

## Troubleshooting

### Common Issues

**"FileNotFoundError: lineup_example.csv"**
- Ensure your CSV file exists in the current directory
- Use `-f filename.csv` to specify a different file

**"Lineup size larger than available players"**
- System automatically adjusts lineup size to available players
- Add more players to your CSV for larger lineups

**"No improvement from genetic algorithm"**
- Try increasing generations (`-g 100`) or population (`-p 100`) 
- Random search sometimes finds better lineups than GA
- This is normal behavior - the system saves the best from both methods

**Very low run totals**
- Check your player statistics for accuracy
- Ensure AB = 1B + 2B + 3B + HR + Outs (system calculates outs)
- Players with very few hits will generate many outs

### Performance Tips

**For faster testing:**
```bash
python master_optimizer.py -nr 50 -g 20 -ng 5
```

**For thorough optimization:**
```bash  
python master_optimizer.py -nr 1000 -g 200 -p 100 -ng 50
```

**For reproducible research:**
```bash
python master_optimizer.py --seed 12345 -sn 100
```

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

This system provides a foundation for baseball lineup optimization. Potential enhancements could include:
- Advanced base stealing simulation
- Pitcher-batter matchup data
- Situational hitting statistics  
- Double play probability modeling
- Multi-objective optimization (runs vs consistency)
- Integration with real-time baseball APIs

---

**Note**: This is a statistical simulation tool for educational and analytical purposes. Actual baseball involves many more variables and complexities than this simplified model can capture.