import pandas as pd

data = [
    {"Position": 1, "Team": "Arsenal", "Played": 10, "Won": 9, "Drawn": 0, "Lost": 1, "GF": 15, "GA": 5, "GD": 10, "Points": 27},
    {"Position": 2, "Team": "Brighton and Hove Albion", "Played": 10, "Won": 7, "Drawn": 1, "Lost": 2, "GF": 26, "GA": 7, "GD": 19, "Points": 22},
    {"Position": 3, "Team": "Manchester City", "Played": 10, "Won": 7, "Drawn": 0, "Lost": 3, "GF": 21, "GA": 13, "GD": 8, "Points": 21},
    {"Position": 4, "Team": "Liverpool", "Played": 10, "Won": 5, "Drawn": 3, "Lost": 2, "GF": 14, "GA": 10, "GD": 4, "Points": 18},
    {"Position": 5, "Team": "Chelsea", "Played": 10, "Won": 5, "Drawn": 1, "Lost": 4, "GF": 19, "GA": 16, "GD": 3, "Points": 16},
    {"Position": 6, "Team": "Everton", "Played": 10, "Won": 4, "Drawn": 4, "Lost": 2, "GF": 12, "GA": 10, "GD": 2, "Points": 16},
    {"Position": 7, "Team": "Bournemouth", "Played": 10, "Won": 4, "Drawn": 3, "Lost": 3, "GF": 16, "GA": 14, "GD": 2, "Points": 15},
    {"Position": 8, "Team": "Brentford", "Played": 10, "Won": 3, "Drawn": 5, "Lost": 2, "GF": 16, "GA": 11, "GD": 5, "Points": 14},
    {"Position": 9, "Team": "Leeds United", "Played": 10, "Won": 3, "Drawn": 5, "Lost": 2, "GF": 10, "GA": 8, "GD": 2, "Points": 14},
    {"Position": 10, "Team": "Aston Villa", "Played": 10, "Won": 3, "Drawn": 4, "Lost": 3, "GF": 14, "GA": 17, "GD": -3, "Points": 13},
    {"Position": 11, "Team": "Tottenham Hotspur", "Played": 10, "Won": 3, "Drawn": 3, "Lost": 4, "GF": 10, "GA": 11, "GD": -1, "Points": 12},
    {"Position": 12, "Team": "Newcastle United", "Played": 10, "Won": 3, "Drawn": 3, "Lost": 4, "GF": 13, "GA": 16, "GD": -3, "Points": 12},
    {"Position": 13, "Team": "Hull City", "Played": 10, "Won": 2, "Drawn": 5, "Lost": 3, "GF": 11, "GA": 11, "GD": 0, "Points": 11},
    {"Position": 14, "Team": "Ipswich Town", "Played": 10, "Won": 3, "Drawn": 2, "Lost": 5, "GF": 15, "GA": 20, "GD": -5, "Points": 11},
    {"Position": 15, "Team": "Fulham", "Played": 10, "Won": 2, "Drawn": 4, "Lost": 4, "GF": 10, "GA": 12, "GD": -2, "Points": 10},
    {"Position": 16, "Team": "Nottingham Forest", "Played": 10, "Won": 2, "Drawn": 3, "Lost": 5, "GF": 9, "GA": 13, "GD": -4, "Points": 9},
    {"Position": 17, "Team": "Coventry City", "Played": 10, "Won": 3, "Drawn": 0, "Lost": 7, "GF": 10, "GA": 19, "GD": -9, "Points": 9},
    {"Position": 18, "Team": "Manchester United", "Played": 10, "Won": 1, "Drawn": 5, "Lost": 4, "GF": 14, "GA": 19, "GD": -5, "Points": 8},
    {"Position": 19, "Team": "Sunderland", "Played": 10, "Won": 2, "Drawn": 2, "Lost": 6, "GF": 8, "GA": 17, "GD": -9, "Points": 8},
    {"Position": 20, "Team": "Crystal Palace", "Played": 10, "Won": 2, "Drawn": 1, "Lost": 7, "GF": 10, "GA": 24, "GD": -14, "Points": 7}
]

df = pd.DataFrame(data)
df.to_excel('premier_league_table.xlsx', index=False)
print('Excel generated successfully.')
