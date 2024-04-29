from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable]]

def condorcet_loser(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable]]:
    global failureSet
    failureSet = list()
    seed: int = sample
    election: list[Ballot]
    expected: Result
    actual: Result
    for s in range(seed):
        election = genOneElection(num_voters, num_candidates, num_unique_ballots, s)
        expected = condorcet_losses(election)    
        if len(election) == 1 and len(election[0].ranking) == 1:
            continue 
        if expected[1]:
            actual = scheme(election)
            if expected[0] == actual[0] and actual[1]:
                if electionNotInSet(failureSet, election):
                    failureSet.append({'election': election, 'winner': actual[0]})
                if not all_found:
                    printOutException()
                    return failureSet
    printOutException()
    return failureSet

def printOutException() -> None:
    global failureSet
    for fail in failureSet:
        ballotToStr(fail['election'])
        print(f"Expected loser: {fail['winner']}\n")

"""
    Outputs the Condorcet loser, if there is one.
"""
def condorcet_losses(ballots: list[Ballot]) -> Result:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    for candidateA in candidates:
        curLosses = 1
        for candidateB in candidates:
            if candidateA == candidateB:
                continue
            curLosses = 0
            for ballot in ballots:
                candidateAI = len(ballot.ranking) if candidateA not in ballot.ranking else ballot.ranking.index(candidateA)
                candidateBI = len(ballot.ranking) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                if candidateAI > candidateBI:
                    curLosses += ballot.tally
                if candidateAI < candidateBI:
                    curLosses -= ballot.tally
            if curLosses <= 0:
                break
        if curLosses > 0:
            return candidateA, True
    return -1, False