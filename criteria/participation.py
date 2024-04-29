from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable | Ballot]]

# Generate election with NO condorcet winner
# Find scheme winner
# Find all candidates that win pairwise vs that winner
    # There must be at least one, since there is no condorcet winner
# Pick the candidate with the most pairwise wins from among that group
    # Add a ballot that ranks scheme winner > this candidate
    # Give it just enough votes to make that candidate condorcet winner
# Rerun the scheme with new set of ballots
# If there is a new winner, then the scheme failed

def participation(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable | Ballot]]:
    global failureSet
    failureSet = list()
    seed: int = sample
    election: list[Ballot]
    schemeWinner: Result
    pairwiseMatrix: dict[Hashable, dict[Hashable, int]]
    for s in range(seed):
        election = genOneElection(num_voters, num_candidates, num_unique_ballots, s)
        if condorcet(election)[1]:
            continue
        schemeWinner, hasWinner = scheme(election)
        if not hasWinner:
            continue
        pairwiseMatrix = pairwise(election)
        favored: Hashable = worstAlternative(pairwiseMatrix, schemeWinner)
        unfavored: Hashable = bestAlternative(pairwiseMatrix, schemeWinner, favored, num_voters)
        newRanking: tuple[Hashable] = tuple([favored, schemeWinner, unfavored])
        newTally: int = minVotes(pairwiseMatrix, unfavored)
        if newTally > num_voters/4:
            continue
        newBallot: Ballot = Ballot(newRanking, newTally)
        newElection: list[Ballot] = election.copy()
        newElection.append(newBallot)
        newSchemeWinner, hasWinner = scheme(newElection)
        if newSchemeWinner != favored and newSchemeWinner != schemeWinner and hasWinner:
            if electionNotInSet(failureSet, election):
                failureSet.append({'election': election, 'newElection': newElection, 'originalWinner': schemeWinner, 'newWinner': newSchemeWinner, 'newBallot': newBallot})
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
        print(f"New winner: {ex['newWinner']}")
        print(f"Add [Count: {ex['newBallot'].tally}, Ranking: {ex['newBallot'].ranking}]\n")

"""
    Outputs the condorcet winner, if there is one.
"""
def condorcet(ballots: list[Ballot]) -> Result:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    for candidateA in candidates:
        curWins = 1
        for candidateB in candidates:
            if candidateA == candidateB:
                continue
            curWins = 0
            for ballot in ballots:
                candidateAI = len(ballot.ranking) if candidateA not in ballot.ranking else ballot.ranking.index(candidateA)
                candidateBI = len(ballot.ranking) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                if candidateAI < candidateBI:
                    curWins += ballot.tally
                if candidateAI > candidateBI:
                    curWins -= ballot.tally
            if curWins <= 0:
                break
        if curWins > 0:
            return candidateA, True
    return -1, False

"""
    Outputs the pairwise win matrix.
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
def bestAlternative(matrix: dict[Hashable, dict[Hashable, int]], schemeWinner: Hashable, favored: Hashable, numVoters: int) -> Hashable:
    best: Hashable = schemeWinner
    curMax: int = numVoters
    for candidate in matrix[schemeWinner].keys():
        if candidate == favored:
            continue
        winMargin: int = matrix[schemeWinner][candidate] - matrix[candidate][schemeWinner]
        if curMax > winMargin:
            curMax = winMargin
            best = candidate
    return best

"""
    Given the pairwise win matrix, this will output the candidate with the most pairwise losses 
    against the scheme winner.
"""
def worstAlternative(matrix: dict[Hashable, dict[Hashable, int]], schemeWinner: Hashable) -> Hashable:
    worst: Hashable = schemeWinner
    curMax: int = 0
    for candidate in matrix[schemeWinner].keys():
        winMargin: int = matrix[schemeWinner][candidate] - matrix[candidate][schemeWinner]
        if curMax < winMargin:
            curMax = winMargin
            worst = candidate
    return worst

"""
    Given the pairwise matrix, this will output the minimum number of votes the 
    input candidate needs to become the condorcet winner.
"""
def minVotes(matrix: dict[Hashable, dict[Hashable, int]], alternative: Hashable) -> int:
    votes: int = 0
    for candidate in matrix[alternative].keys():
        winMargin: int = matrix[candidate][alternative] - matrix[alternative][candidate]
        votes = max(votes, winMargin)
    return votes + 1