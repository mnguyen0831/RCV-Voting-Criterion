# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

def minimax(ballots: list[Ballot]) -> Result:
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    pairwiseMatrix: dict[Hashable, dict[Hashable, int]] = pairwise(ballots)
    maxLoss: dict[Hashable, int] = dict()
    for candidateA in candidates:
        for candidateB in candidates:
            if candidateA == candidateB:
                continue
            loss: int = pairwiseMatrix[candidateB][candidateA]
            if candidateA not in maxLoss.keys():
                maxLoss[candidateA] = loss
            if maxLoss[candidateA] < loss:
                maxLoss[candidateA] = loss
    winners: list[Hashable] = [
        candidate for candidate, loss in maxLoss.items() if loss == min(maxLoss.values())
    ]
    return winners[0], len(winners) == 1

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

scheme: Scheme = minimax
name: str = "Minimax"