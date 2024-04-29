from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable]]

def reversal(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable]]:
    global failureSet
    failureSet = list()
    seed: int = sample
    election: list[Ballot]
    expected: Result
    actual: Result
    for s in range(seed):
        election = genOneElection(num_voters, num_candidates, num_unique_ballots, s)
        expected = scheme(election)
        if len(election) == 1 and len(election[0].ranking) == 1:
            continue 
        if not expected[1]:
            continue
        revElection = reverseBallots(election)
        actual = scheme(revElection)
        if expected[0] == actual[0] and actual[1]:
            if electionNotInSet(failureSet, election):
                failureSet.append({'election': election, 'reversed': revElection, 'winner': actual[0]})
            if not all_found:
                printOutException()
                return failureSet
    printOutException()
    return failureSet

def printOutException() -> None:
    global failureSet
    for fail in failureSet:
        print("Original Election:")
        ballotToStr(fail['election'])
        print("Reversed Election:")
        ballotToStr(fail['reversed'])
        print(f"Expected loser: {fail['winner']}\n")

"""
    Reverses the ballots.
"""
def reverseBallots(ballots: list[Ballot]) -> list[Ballot]:
    rev: list[Ballot] = list()
    for ballot in ballots:
        revBal = list(ballot.ranking)
        revBal.reverse()
        rev.append(Ballot(tuple(revBal), ballot.tally))
    return rev