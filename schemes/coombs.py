# pyright: strict
from typing import Hashable
from fractions import Fraction

from scheme_types import Ballot, Result, Scheme

def coombs(ballots: list[Ballot]) -> Result:
    majorityWin: Result = majority(ballots)
    if majorityWin[1]:
        return majorityWin
    cur_ballots: list[Ballot] = ballots.copy()
    tallies: dict[Hashable, float] = tally(False, ballots)
    while len(tallies.keys()) > 1:
        min_score = max(tallies.values())
        dropped: list[Hashable] = [candidate for candidate, score in tallies.items() if score == min_score]
        if len(dropped) > 1:
            return dropped[0], len(tallies.keys()) == 1
        if len(dropped) == 0:
            return -1, False
        del tallies[dropped[0]]
        cur_ballots = delete_loser(cur_ballots, dropped[0])
        majorityWin = majority(cur_ballots)
        if majorityWin[1]:
            return majorityWin
        tallies = tally(False, cur_ballots)
    max_score: float = max(tallies.values())
    winners: list[Hashable] = [candidate for candidate, score in tallies.items() if score == max_score]
    return winners[0], len(winners) == 1

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

def tally(first: bool, ballots: list[Ballot]) -> dict[Hashable, float]:
    if not first:
        return tallyLast(ballots)
    tallies: dict[Hashable, float] = dict()
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            if ballot.ranking[0] not in tallies.keys():
                tallies[ballot.ranking[0]] = 0
            tallies[ballot.ranking[0]] += ballot.tally
    return tallies

def tallyLast(ballots:list[Ballot]) -> dict[Hashable, float]:
    tallies: dict[Hashable, Fraction] = dict()
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    for ballot in ballots:
        if len(ballot.ranking) == len(candidates):
            if ballot.ranking[-1] not in tallies.keys():
                tallies[ballot.ranking[-1]] = Fraction(0)
            tallies[ballot.ranking[-1]] += ballot.tally
        elif len(ballot.ranking) > 0:
            multiplier: Fraction = Fraction(1, len(candidates) - len(ballot.ranking))
            for candidate in candidates:
                if candidate not in ballot.ranking:
                    if candidate not in tallies.keys():
                        tallies[candidate] = Fraction(0)
                    tallies[candidate] += ballot.tally * multiplier
    newTallies: dict[Hashable, float] = dict()
    for k, v in tallies.items():
        newTallies[k] = float(v)
    return newTallies

def majority(ballots: list[Ballot]) -> Result:
    tallies: dict[Hashable, float] = tally(True, ballots)
    active_votes = 0
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            active_votes += ballot.tally
    if max(tallies.values()) > active_votes//2:
        winners: list[Hashable] = [candidate for candidate, score in tallies.items() if score == max(tallies.values())]
        return list(winners)[0], len(winners) == 1
    return -1, False 

scheme: Scheme = coombs
name: str = "Coombs"