import argparse

from util.criterion_util import getScheme

from criteria.condorcet_winner import condorcet_winner
from criteria.condorcet_loser import condorcet_loser
from criteria.majority import majority
from criteria.participation import participation

scheme: str
criterion: str

"""
    To do list:
        Flags:
            --realistic
                Only generates elections with 'realistic' numbers
            --simple
                Only generates elections with 'simple' numbers
            --partisan
                Generates an election where voters voted strictly partisan
            --out
                Writes the generated election into a .json file
            --num-candidates
                Sets number of candidates
            --num-voters
                Sets number of voters
            --num-unique-ballots
                Sets number of unique ballots
            --all
                Collects all elections found
"""

def main() -> None:
    getInput()
    testCriterion()

def getInput() -> None:
    global scheme, criterion
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--scheme', type=str, default='borda', help='The desired scheme')
    parser.add_argument('--criterion', type=str, default='condorcet_winner', help='The desired criterion')
    args = parser.parse_args()
    scheme = args.scheme
    criterion = args.criterion

def testCriterion() -> None:
    global criterion, scheme
    passes: bool
    match criterion:
        case 'condorcet_winner':
            passes = condorcet_winner(getScheme(scheme))
        case 'condorcet_loser':
            passes = condorcet_loser(getScheme(scheme))
        case 'majority':
            passes = majority(getScheme(scheme))
        case 'participation':
            passes = participation(getScheme(scheme))
        case _:
            print("Not yet implemented.")
            return
    print(f"{scheme} passes {criterion}: {passes}")

if __name__ == "__main__":
    main()