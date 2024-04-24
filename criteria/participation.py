from typing import Hashable
from common.types import Ballot, Result, Scheme
from criterion_util import genOneElection

failureSet: list[list[Ballot]]

# Generate election with NO condorcet winner
# Find scheme winner
# Find all candidates that win pairwise vs that winner
    # There must be at least one, since there is no condorcet winner
# Pick the candidate with the most pairwise wins from among that group
    # Add a ballot that ranks scheme winner > this candidate
    # Give it just enough votes to make that candidate condorcet winner
# Rerun the scheme with new set of ballots
# If there is a new winner, then the scheme failed
# May also need to be tweaked for IRV in particular
    # I need to figure out how to ensure this test catches ALL possible schemes

def participation(scheme: Scheme) -> bool:
    global failureSet
    failureSet = list()
    seed: int = 5
    numVoters: int = 1000
    numCandidates: int = 6
    maxUniqueRankings: int = 6
    election: list[Ballot]
    schemeWinner: Result
    pairwiseMatrix: dict[Hashable, dict[Hashable, int]]
    for s in range(seed):
        for v in range(10, numVoters):
            for c in range(2, numCandidates):
                for ur in range(2, maxUniqueRankings):
                    election = genOneElection(v, c, ur, c, 1, s)
                    if condorcet(election)[1]:
                        continue
                    schemeWinner, hasWinner = scheme(election) # doesn't skip if tie
                    if not hasWinner:
                        continue
                    pairwiseMatrix = pairwise(election)
                    bestCandidate: Hashable = bestAlternative(pairwiseMatrix, schemeWinner)
                    newRanking: tuple[Hashable] = tuple([schemeWinner, bestCandidate])
                    newTally: int = minVotes(pairwiseMatrix, bestCandidate)
                    newBallot: Ballot = Ballot(newRanking, newTally)
                    newElection: list[Ballot] = election.copy()
                    newElection.append(newBallot)
                    newSchemeWinner, hasWinner = scheme(newElection)
                    if newSchemeWinner != schemeWinner:
                        printOutException(election, schemeWinner, newSchemeWinner, newBallot)
                        return False
    return True

def electionNotInSet(election: list[Ballot]) -> bool:
    global failureSet
    for e in failureSet:
        for b in e:
            numSame: int = 0
            for nb in election:
                if b.ranking == nb.ranking:
                    numSame += 1
            if numSame == len(election):
                return False
    return True

def printOutException(election: list[Ballot], schemeWinner: Hashable, newWinner: Hashable, ballot: Ballot) -> None:
    ballotToStr(election)
    print(f"Original winner: {schemeWinner}")
    print(f"Add [Count: {ballot.tally}, Ranking: {ballot.ranking}]")
    print(f"New winner: {newWinner}")

def ballotToStr(ballots: list[Ballot]) -> None:
    for ballot in ballots:
        print(f"[Count: {ballot.tally}, Ranking: {ballot.ranking}]")

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

def bestAlternative(matrix: dict[Hashable, dict[Hashable, int]], schemeWinner: Hashable) -> Hashable:
    best: Hashable = schemeWinner
    curMax: int = 0
    for candidate in matrix[schemeWinner].keys():
        winMargin: int = matrix[candidate][schemeWinner] - matrix[schemeWinner][candidate]
        if curMax < winMargin:
            curMax = winMargin
            best = candidate
    return best

def minVotes(matrix: dict[Hashable, dict[Hashable, int]], alternative: Hashable) -> int:
    votes: int = 0
    for candidate in matrix[alternative].keys():
        winMargin: int = matrix[candidate][alternative] - matrix[alternative][candidate]
        votes = max(votes, winMargin)
    return votes + 1