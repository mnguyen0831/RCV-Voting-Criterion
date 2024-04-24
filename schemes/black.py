# pyright: strict
from collections import Counter
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

# Search for Condorcet winner
# If not, then get the Borda winner

def black(ballots: list[Ballot]) -> Result:
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    scores: Counter[Hashable] = Counter()
    for ballot in ballots:
        for i, candidate in enumerate(ballot.ranking):
            scores[candidate] += points[i] * ballot.tally
    for candidateA in scores.keys():
        curWins = 1
        for candidateB in scores.keys():
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
    max_score: int = max(scores.values())
    winners: list[Hashable] = [
        candidate for candidate, score in scores.items() if score == max_score
    ]
    return winners[0], len(winners) == 1

scheme: Scheme = black
name: str = "Black"