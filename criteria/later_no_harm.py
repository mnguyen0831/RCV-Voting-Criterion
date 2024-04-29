from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable]]

# Generate election
# Find Scheme winner
# Find pairwise runner-up
# Remove all later preferences from ballots with the runner-up preferred over the actual winner
# Rerun the election and check if the runner-up wins

def later_no_harm(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable]]:
    global failureSet
    failureSet = list()
    seed: int = sample
    election: list[Ballot]
    schemeWinner: Result
    pairwiseMatrix: dict[Hashable, dict[Hashable, int]]
    for s in range(seed):
        election = genOneElection(num_voters, num_candidates, num_unique_ballots, s)
        schemeWinner, hasWinner = scheme(election)
        if not hasWinner:
            continue
        pairwiseMatrix = pairwise(election)
        if len(pairwiseMatrix.keys()) == 0:
            continue
        runnerUp: Hashable = bestAlternative(pairwiseMatrix, schemeWinner, num_voters)
        newElection: list[Ballot] = list()
        for ballot in election:
            if schemeWinner in ballot.ranking and runnerUp in ballot.ranking and ballot.ranking.index(schemeWinner) > ballot.ranking.index(runnerUp):
                newBallot: Ballot = Ballot(tuple(list(ballot.ranking)[:ballot.ranking.index(runnerUp) + 1]), ballot.tally)
                newElection.append(newBallot)
            else:
                newElection.append(ballot)
        newSchemeWinner, hasWinner = scheme(newElection)
        if newSchemeWinner == runnerUp:
            if electionNotInSet(failureSet, election):
                failureSet.append({'election': election, 'newElection': newElection, 'originalWinner': schemeWinner, 'newWinner': newSchemeWinner})
            if not all_found:
                printOutException()
                return failureSet
    printOutException()
    return failureSet

def printOutException() -> None:
    global failureSet
    for ex in failureSet:
        print("Original election:")
        ballotToStr(ex['election'])
        print(f"Original winner: {ex['originalWinner']}")
        print("New election:")
        ballotToStr(ex['newElection'])
        print(f"New winner: {ex['newWinner']}\n")

"""
    Given the pairwise win matrix, this will output the candidate with the most pairwise
    wins agains the scheme winner.
"""
def pairwise(ballots: list[Ballot]) -> dict[Hashable, dict[Hashable, int]]:
    pairwiseMatrix: dict[Hashable, dict[Hashable, int]] = dict()
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    for ballot in ballots:
        for candidateA in candidates:
            for candidateB in candidates:
                if candidateA == candidateB:
                    continue
                if candidateA not in pairwiseMatrix.keys():
                    pairwiseMatrix[candidateA] = dict()
                if candidateB not in pairwiseMatrix[candidateA].keys():
                    pairwiseMatrix[candidateA][candidateB] = 0
                if candidateA not in ballot.ranking:
                    if candidateB not in ballot.ranking:
                        pairwiseMatrix[candidateA][candidateB] += ballot.tally
                    continue
                i: int = ballot.ranking.index(candidateA)
                j: int = len(candidates) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                if i < j:
                    pairwiseMatrix[candidateA][candidateB] += 2 * ballot.tally
    return pairwiseMatrix

"""
    Given the pairwise win matrix, this will output the candidate with the most pairwise
    wins agains the scheme winner.
"""
def bestAlternative(matrix: dict[Hashable, dict[Hashable, int]], schemeWinner: Hashable, numVoters: int) -> Hashable:
    best: Hashable = schemeWinner
    curMax: int = numVoters
    for candidate in matrix[schemeWinner].keys():
        winMargin: int = matrix[schemeWinner][candidate] - matrix[candidate][schemeWinner]
        if curMax > winMargin:
            curMax = winMargin
            best = candidate
    return best