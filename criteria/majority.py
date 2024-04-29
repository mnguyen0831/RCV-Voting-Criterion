from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable]]

def majority(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable]]:
    global failureSet
    failureSet = list()
    seed: int = sample
    election: list[Ballot]
    expected: Result
    actual: Result
    for s in range(seed):
        election = genOneElection(num_voters, num_candidates, num_unique_ballots, s)
        expected = majorityWin(election)    
        if expected[1]:
            actual = scheme(election)
            if expected[0] != actual[0] and actual[1]:
                if electionNotInSet(failureSet, election):
                    failureSet.append({'election': election, 'ewinner': expected[0], 'awinner': actual[0]})
                if not all_found:
                    printOutException()
                    return failureSet
    printOutException()
    return failureSet

def printOutException() -> None:
    global failureSet
    for fail in failureSet:
        ballotToStr(fail['election'])
        print(f"Expected winner: {fail['ewinner']}, Actual winner: {fail['awinner']}\n")

"""
    Tallies up the first place votes for every candidate.
"""
def tally(ballots: list[Ballot]) -> dict[Hashable, int]:
    tallies: dict[Hashable,int] = dict()
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            if ballot.ranking[0] not in tallies.keys():
                tallies[ballot.ranking[0]] = 0
            tallies[ballot.ranking[0]] += ballot.tally
    return tallies

"""
    Outputs the majority winner, if there is one.
"""
def majorityWin(ballots: list[Ballot]) -> Result:
    tallies: dict[Hashable, int] = tally(ballots)
    active_votes = 0
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            active_votes += ballot.tally
    if max(tallies.values()) > active_votes // 2:
        winners: list[Hashable] = [candidate for candidate, score in tallies.items() if score == max(tallies.values())]
        return list(winners)[0], len(winners) == 1
    return -1, False 