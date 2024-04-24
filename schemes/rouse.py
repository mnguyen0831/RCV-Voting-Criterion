# pyright: strict
from typing import Hashable
from fractions import Fraction

from scheme_types import Ballot, Result, Scheme

def rouse(ballots:list[Ballot]) -> Result:
    cur_ballots: list[Ballot] = ballots.copy()
    scores: dict[Hashable, float] = borda(ballots)
    while len(scores.keys()) > 1:
        rouse_ballots: list[Ballot] = cur_ballots.copy()
        while len(scores.keys()) > 1:
            max_score = max(scores.values())
            drop = [
                candidate for candidate, score in scores.items() if score == max_score
                ]
            if len(drop) != 1:
                return -1, False
            for candidate in drop:
                rouse_ballots = delete_loser(rouse_ballots, candidate)
            scores = borda(rouse_ballots)
        if len(scores.keys()) != 1:
            return -1, False
        for loser in scores.keys():
            cur_ballots = delete_loser(cur_ballots, loser)
        scores = borda(cur_ballots)
    winners = list(scores.keys())
    return winners[0], len(winners) == 1

def borda(ballots: list[Ballot]) -> dict[Hashable, float]:
    scores: dict[Hashable, Fraction] = dict()
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    for ballot in ballots:
        if len(ballot.ranking) == len(candidates):
            for i in range(len(ballot.ranking)):
                if ballot.ranking[i] not in scores.keys():
                    scores[ballot.ranking[i]] = Fraction(0)
                scores[ballot.ranking[i]] += ballot.tally * points[i]
        elif len(ballot.ranking) > 0:
            multiplier: Fraction = Fraction(1, len(candidates) - len(ballot.ranking))
            leftoverPoints: int = 0
            for pointCount in points[len(ballot.ranking):]:
                leftoverPoints += pointCount
            for candidate in candidates:
                if candidate not in scores.keys():
                        scores[candidate] = Fraction(0)
                if candidate not in ballot.ranking:
                    scores[candidate] += ballot.tally * multiplier * leftoverPoints
                else:
                    scores[candidate] += ballot.tally * points[ballot.ranking.index(candidate)]
    newScores: dict[Hashable, float] = dict()
    for k, v in scores.items():
        newScores[k] = float(v)
    return newScores

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

scheme: Scheme = rouse
name: str = "Rouse"