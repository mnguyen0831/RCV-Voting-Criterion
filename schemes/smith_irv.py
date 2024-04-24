# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

def smith_irv(ballots: list[Ballot]) -> Result:
    smithSet: list[Hashable] = smith(ballots)
    if len(smithSet) == 1:
        return smithSet[0], True
    while len(smithSet) > 1:
        tallies: dict[Hashable, int] = dict()
        for ballot in ballots:
            for candidate in ballot.ranking:
                if candidate in smithSet:
                    if candidate not in tallies.keys():
                        tallies[candidate] = 0
                    tallies[candidate] += ballot.tally
                    break
        minScore: int = min(tallies.values())
        drop: list[Hashable] = [
            candidate for candidate, score in tallies.items() if score == minScore
        ]
        if len(drop) > 1:
            return -1, False
        if len(drop) == 0:
            return -3, False
        smithSet.remove(drop[0])
    return smithSet[0], len(smithSet) == 1

def smith(ballots: list[Ballot]) -> list[Hashable]:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    copelandScores: dict[Hashable, int] = copelandScore(ballots)
    smithSet: list[Hashable] = [
        candidate for candidate, score in copelandScores.items() if score == max(copelandScores.values())
    ]
    lenSmith: int = len(smithSet)
    cur: int = 0
    while cur != lenSmith:
        lenSmith = len(smithSet)
        additions: list[Hashable] = list()
        for candidateA in smithSet:
            for candidateB in candidates:
                if candidateB in smithSet:
                    continue
                curWins = 0
                for ballot in ballots:
                    candidateAI = len(ballot.ranking) if candidateA not in ballot.ranking else ballot.ranking.index(candidateA)
                    candidateBI = len(ballot.ranking) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                    if candidateAI > candidateBI:
                        curWins += ballot.tally
                    if candidateAI < candidateBI:
                        curWins -= ballot.tally
                if curWins == 0:
                    additions.append(candidateB)
                elif curWins > 0:
                    additions.append(candidateB)
        smithSet.extend(additions)
        cur = len(smithSet)
    return smithSet

def copelandScore(ballots: list[Ballot]) -> dict[Hashable, int]:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    scores: dict[Hashable, int] = dict()
    for candidateA in candidates:
        for candidateB in candidates:
            if candidateA == candidateB:
                continue
            curWins: int = 0
            for ballot in ballots:
                candidateAI = len(ballot.ranking) if candidateA not in ballot.ranking else ballot.ranking.index(candidateA)
                candidateBI = len(ballot.ranking) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                if candidateAI < candidateBI:
                    curWins += ballot.tally
                if candidateAI > candidateBI:
                    curWins -= ballot.tally
            if candidateA not in scores.keys():
                scores[candidateA] = 0
            if curWins == 0:
                scores[candidateA] += 1
            elif curWins > 0:
                scores[candidateA] += 2
    return scores

scheme: Scheme = smith_irv
name: str = "Smith IRV"