# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

def schulze(ballots: list[Ballot]) -> Result:
    strongestPath: dict[tuple[Hashable, Hashable], int] = getStrongestPath(ballots)
    candidates: list[Hashable] = list((set(c for ballot in ballots for c in ballot.ranking)))
    pairwiseMatrix: dict[Hashable, int] = dict()
    for i in candidates:
        for j in candidates:
            if i != j:
                if strongestPath[(i,j)] > strongestPath[(j,i)]:
                    if i not in pairwiseMatrix.keys():
                        pairwiseMatrix[i] = 0
                    pairwiseMatrix[i] += 1
    if len(pairwiseMatrix.keys()) < 1:
        return -1, False
    max_score: int = max(pairwiseMatrix.values())
    if max_score < len(candidates) - 1:
        return -1, False
    winners: list[Hashable] = [candidate for candidate, score in pairwiseMatrix.items() if score == max_score]
    return winners[0], len(winners) == 1

def getPreferences(ballots: list[Ballot]) -> dict[tuple[Hashable, Hashable], int]:
    preferences: dict[tuple[Hashable, Hashable], int] = dict()
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    for ballot in ballots:
        for candidateA in candidates:
            for j, candidateB in enumerate(ballot.ranking):
                if candidateA == candidateB:
                    continue
                if candidateA not in ballot.ranking:
                    if (candidateB, candidateA) not in preferences.keys():
                        preferences[(candidateB, candidateA)] = 0
                    preferences[(candidateB, candidateA)] += ballot.tally
                    continue
                i: int = ballot.ranking.index(candidateA)
                if i < j:
                    if (candidateA, candidateB) not in preferences.keys():
                        preferences[(candidateA, candidateB)] = 0
                    preferences[(candidateA, candidateB)] += ballot.tally
    return preferences

def getStrongestPath(ballots: list[Ballot]):
    pairwiseTallies: dict[tuple[Hashable, Hashable], int] = getPreferences(ballots)
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    strongestPath: dict[tuple[Hashable, Hashable], int] = dict()
    for i in candidates:
        for j in candidates:
            if i != j:
                if (i,j) not in pairwiseTallies.keys():
                    pairwiseTallies[(i,j)] = 0
                if (j,i) not in pairwiseTallies.keys():
                    pairwiseTallies[(j,i)] = 0
                if pairwiseTallies[(i,j)] > pairwiseTallies[(j,i)]:
                    strongestPath[(i,j)] = pairwiseTallies[(i,j)]
                else:
                    strongestPath[(i,j)] = 0
    for i in candidates:
        for j in candidates:
            if i != j:
                for k in candidates:
                    if i != k and j != k:
                        strongestPath[(j,k)] = max(strongestPath[(j,k)], min(strongestPath[(j,i)], strongestPath[(i,k)]))
    return strongestPath

scheme: Scheme = schulze
name: str = "Schulze"