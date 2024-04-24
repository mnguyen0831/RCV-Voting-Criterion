# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme


# Eliminate candidate with the fewest votes
# If only one candidate remains, elect the candidate
# Repeat

def irv(ballots: list[Ballot]) -> Result:
    cur_ballots: list[Ballot] = ballots.copy()
    tallies: dict[Hashable, int] = {}
    dropped: list[Hashable] = []
    active_votes = 0
    for ballot in ballots:
        for candidate in ballot.ranking:
            if candidate not in tallies.keys():
                tallies[candidate] = 0
        tallies[ballot.ranking[0]] += ballot.tally
        active_votes += ballot.tally
    size_pool = len(tallies.keys())
    while len(dropped) < size_pool - 1:
        for candidate in tallies.keys():
            if tallies[candidate] > active_votes/2:
                return candidate, True
        min_votes: int = min(tallies.values())
        cur_dropped: list[Hashable] = []
        for key, val in tallies.items():
            if val == min_votes:
                cur_dropped.append(key)
            tallies[key] = 0
        if len(cur_dropped) > 1:
            return "<AMBIGUOUS>", False
        tallies.pop(cur_dropped[0])
        dropped.extend(cur_dropped)
        active_votes = 0
        for i in range(len(cur_ballots)):
            if cur_dropped[0] in cur_ballots[i].ranking:
                cur_rank: list[Hashable] = list(cur_ballots[i].ranking)
                cur_rank.remove(cur_dropped[0])
                cur: Ballot = Ballot(tuple(cur_rank), cur_ballots[i].tally)
                del cur_ballots[i]
                cur_ballots.insert(i, cur)
            if len(cur_ballots[i].ranking) > 0:
                tallies[cur_ballots[i].ranking[0]] += cur_ballots[i].tally
                active_votes += cur_ballots[i].tally
    winners: list[Hashable] = [candidate[0] for candidate in tallies.items() if candidate not in dropped]
    return winners[0], len(winners) == 1

scheme: Scheme = irv
name: str = "Instant Runoff Voting"