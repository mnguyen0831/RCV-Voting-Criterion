import argparse
import json

from typing import Hashable
from util import getScheme
from scheme_types import Ballot

from criteria.condorcet_loser import condorcet_loser
from criteria.condorcet_winner import condorcet_winner
from criteria.later_no_harm import later_no_harm
from criteria.later_no_help import later_no_help
from criteria.majority import majority
from criteria.monotonicity import monotonicity
from criteria.participation import participation
from criteria.reversal import reversal

scheme: str
criterion: str
realistic: bool
simple: bool
out: bool
num_candidates: int
num_voters: int
num_unique_ballots: int
all_found: bool
sample: int

def main() -> None:
    getInput()
    testCriterion()

def getInput() -> None:
    global scheme, criterion, realistic, out, num_candidates, num_voters, num_unique_ballots, all_found, sample
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--scheme', type=str, default='borda', help='The desired scheme')
    parser.add_argument('--criterion', type=str, default='condorcet_winner', help='The desired criterion')
    parser.add_argument('--realistic', action='store_true', help='Uses realistic numbers (Numbers from 2022 CA General Election)')
    parser.add_argument('--out', action='store_true', help='Writes the election or elections found to [criterion]_[scheme].json')
    parser.add_argument('--num-candidates', type=int, default=4, help='Sets the number of candidates')
    parser.add_argument('--num-voters', type=int, default=20, help='Sets the number of voters')
    parser.add_argument('--num-unique-ballots',type=int, default=5, help='Sets the number of unique ballots')
    parser.add_argument('--all', action='store_true', help='Checks all of the elections generated rather than stopping once one is found')
    parser.add_argument('--sample', type=int, default=100000, help='The number of elections to generate for testing')
    args = parser.parse_args()
    scheme = args.scheme
    criterion = args.criterion
    realistic = args.realistic
    out = args.out
    num_candidates = args.num_candidates
    num_voters = args.num_voters
    num_unique_ballots = args.num_unique_ballots
    all_found = args.all
    sample = args.sample
    if realistic:
        num_candidates = 7
        num_voters = 10000000
        num_unique_ballots = 10


def testCriterion() -> None:
    global criterion, scheme, num_candidates, num_voters, num_unique_ballots, out, all_found, sample
    found: list[dict[str, list[Ballot] | Hashable | Ballot]]
    match criterion:
        case 'condorcet_loser':
            found = condorcet_loser(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'condorcet_winner':
            found = condorcet_winner(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'later_no_harm':
            found = later_no_harm(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'later_no_help':
            found = later_no_help(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'majority':
            found = majority(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'monotonicity':
            found = monotonicity(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'participation':
            found = participation(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case 'reversal':
            found = reversal(getScheme(scheme), num_candidates, num_voters, num_unique_ballots, all_found, sample)
        case _:
            print("Not yet implemented.")
            return
    print(f"Found exceptions for {criterion} in {scheme}: {len(found) > 0}")
    if out:
        with open(f'{criterion}_{scheme}.json', 'w') as json_file:
            json.dump(found, json_file)

if __name__ == "__main__":
    main()