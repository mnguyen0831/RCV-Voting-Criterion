from typing import Hashable
from scheme_types import Ballot, Result, Scheme
from util import genOneElection, electionNotInSet, ballotToStr

failureSet: list[dict[str, list[Ballot] | Hashable | Ballot]]

# Generate election with NO condorcet winner
# Find scheme winner
# Find all candidates that win pairwise vs that winner
#   There must be at least one, since there is no condorcet winner
# Pick the candidate with the most pairwise wins from among that group
# Pick the candidate with the most pairwise losses against the best alternative
# Create a new ballot from one that ranks the worst alternative first
#   Rank the original winner first, maintaining the relative original order
#   Shift votes from that original ballot 
# Rerun the scheme with new set of ballots
# If there is a new winner, then the scheme failed

def monotonicity(scheme: Scheme, num_candidates: int, num_voters: int, num_unique_ballots: int, all_found: bool, sample: int) -> list[dict[str, list[Ballot] | Hashable | Ballot]]:
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
        favored: Hashable = bestAlternative(pairwiseMatrix, schemeWinner, num_voters)
        unfavored: Hashable = worstAlternative(pairwiseMatrix, favored)
        max = pairwiseMatrix[favored][schemeWinner] - pairwiseMatrix[schemeWinner][favored] - 1
        if max <= 0:
            continue
        invalidElection: bool = True
        lostVotes: Ballot = Ballot(tuple([-1]), 0)
        newTally: int = 0
        for ballot in election:
            if unfavored in ballot.ranking and favored in ballot.ranking and schemeWinner in ballot.ranking:
                unfavoredI = ballot.ranking.index(unfavored)
                favoredI = ballot.ranking.index(favored)
                winnerI = ballot.ranking.index(schemeWinner)
                if unfavoredI > winnerI and winnerI > favoredI and ballot.tally >= max:
                    lostVotes = Ballot(ballot.ranking, ballot.tally)
                    newTally = ballot.tally - max
                    invalidElection = False
                    break
            elif unfavored in ballot.ranking and schemeWinner in ballot.ranking:
                unfavoredI = ballot.ranking.index(unfavored)
                winnerI = ballot.ranking.index(schemeWinner)
                if unfavoredI > winnerI and ballot.tally >= max:
                    newTally = ballot.tally - max
                    lostVotes = Ballot(ballot.ranking, newTally)
                    invalidElection = False
                    break
        if invalidElection:
            continue
        newRanking: list[Hashable] = [schemeWinner]
        newRanking.extend(list(lostVotes.ranking)[:lostVotes.ranking.index(schemeWinner)])
        newRanking.extend(list(lostVotes.ranking)[lostVotes.ranking.index(schemeWinner) + 1:])
        gainedVotes: Ballot = Ballot(tuple(newRanking), max)
        newElection: list[Ballot] = [gainedVotes]
        for ballot in election:
            if ballot.ranking == lostVotes.ranking:
                newElection.append(lostVotes)
            else:
                newElection.append(ballot)
        newSchemeWinner, hasWinner = scheme(newElection)
        if newSchemeWinner != schemeWinner:
            if electionNotInSet(failureSet, election):
                failureSet.append({'newElection': newElection, 'election': election, 'originalWinner': schemeWinner, 'newWinner': newSchemeWinner, 'votesTaken': max, 'lostVotes': lostVotes, 'gainedVotes': gainedVotes})
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
        print(f"Votes shifted: {ex['votesTaken']}")
        print(f"Lost votes: {ex['lostVotes'].ranking}")
        print(f"Gained votes: {ex['gainedVotes'].ranking}\n")

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
def bestAlternative(matrix: dict[Hashable, dict[Hashable, int]], schemeWinner: Hashable, numVoters: int) -> Hashable:
    best: Hashable = schemeWinner
    curMax: int = numVoters
    for candidate in matrix[schemeWinner].keys():
        winMargin: int = matrix[schemeWinner][candidate] - matrix[candidate][schemeWinner]
        if curMax > winMargin:
            curMax = winMargin
            best = candidate
    return best

"""
    Given the pairwise win matrix, this will output the candidate with the most pairwise losses 
    against the scheme winner.
"""
def worstAlternative(matrix: dict[Hashable, dict[Hashable, int]], favored: Hashable) -> Hashable:
    worst: Hashable = favored
    curMax: int = 0
    for candidate in matrix[favored].keys():
        winMargin: int = matrix[favored][candidate] - matrix[candidate][favored]
        if curMax < winMargin:
            curMax = winMargin
            worst = candidate
    return worst