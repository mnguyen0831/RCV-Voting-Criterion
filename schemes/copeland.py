# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

# Tally up the amount of pairwise wins each candidate gets
# Each win is worth 2 points, while each tie is worth 1
# The candidate with the most points wins

def copeland(ballots: list[Ballot]) -> Result:
    candidates: dict[Hashable, int] = {}
    for ballot in ballots:
        for candidate in ballot.ranking:
            if candidate not in candidates.keys():
                candidates[candidate] = 0
    for candidateA in candidates.keys():
        for candidateB in candidates.keys():
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
            if curWins == 0:
                candidates[candidateA] += 1
            elif curWins > 0:
                candidates[candidateA] += 2
    max_score: int = max(candidates.values())
    winners: list[Hashable] = [
        candidate for candidate, score in candidates.items() if score == max_score
    ]
    return winners[0], len(winners) == 1

scheme: Scheme = copeland
name: str = "Copeland"