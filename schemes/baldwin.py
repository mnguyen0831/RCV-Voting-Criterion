# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

# Run Borda count for all existing candidates
# Eliminate the candidate with the lowest borda score
# Repeat until last remaining candidate

def baldwin(ballots: list[Ballot]) -> Result:
    cur_ballots: list[Ballot] = ballots.copy()
    scores: dict[Hashable, int] = borda(ballots)
    dropped: list[Hashable] = list()
    while len(scores.keys()) > 1:
        min_score = min(scores.values())
        dropped = [candidate for candidate, score in scores.items() if score == min_score]
        if len(dropped) > 1:
            return dropped[0], len(scores.keys()) == 1
        if len(dropped) == 0:
            return -1, False
        del scores[dropped[0]]
        cur_ballots = delete_loser(cur_ballots, dropped[0])
        scores = borda(cur_ballots)
    max_score: int = max(scores.values())
    winners: list[Hashable] = [candidate for candidate, score in scores.items() if score == max_score]
    return winners[0], len(winners) == 1

def borda(ballots: list[Ballot]) -> dict[Hashable, int]:
    scores: dict[Hashable, int] = dict()
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    for ballot in ballots:
        for i, candidate in enumerate(ballot.ranking):
            if candidate not in scores.keys():
                scores[candidate] = 0
            scores[candidate] += points[i] * ballot.tally
    return scores

def delete_loser(ballots: list[Ballot], loser: Hashable) -> list[Ballot]:
    cur_ballots: list[Ballot] = ballots.copy()
    for i in range(len(ballots)):
            cur_rank: list[Hashable] = list(cur_ballots[i].ranking)
            if loser in cur_ballots[i].ranking:
                cur_rank.remove(loser)
            cur: Ballot = Ballot(tuple(cur_rank), cur_ballots[i].tally)
            del cur_ballots[i]
            cur_ballots.insert(i, cur)
    return cur_ballots

scheme: Scheme = baldwin
name: str = "Baldwin"