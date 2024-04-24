# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

# Run Borda count for all existing candidates
# Calculate the average number of points
# Eliminate all candidates which fall under the average
# Repeat until one candidate (the winner) remains
# I'm so sorry about my code, I'm too tired to make it cleaner

def nanson(ballots: list[Ballot]) -> Result:
    cur_ballots: list[Ballot] = ballots.copy()
    scores: dict[Hashable, int] = {}
    tallies: dict[Hashable, int] = {}
    dropped: list[Hashable] = []
    size: int = len(set(c for ballot in ballots for c in ballot.ranking))
    points: list[int] = [c for c in range(size - 1, -1, -1)]
    active_votes: int = 0
    for ballot in ballots:
        for i, candidate in enumerate(ballot.ranking):
            if candidate not in scores.keys():
                scores[candidate] = 0
                tallies[candidate] = 0
            scores[candidate] += points[i] * ballot.tally
        tallies[ballot.ranking[0]] += ballot.tally
        active_votes += ballot.tally
    size_pool = len(scores)
    while len(dropped) < size_pool - 1:
        totalScores = 0
        for candidate in scores.keys():
            totalScores += scores[candidate]
        average = totalScores/len(scores)
        if max(tallies.values()) > active_votes/2:
            winners: list[Hashable] = [
            candidate for candidate, score in tallies.items() if score == max(tallies.values())
            ]
            return winners[0], len(winners) == 1
        dropped = []
        for key, val in scores.items():
            if val <= average:
                dropped.append(key)
        if len(dropped) == len(scores):
            return [candidate[0] for candidate in scores.items()][0], len(scores.keys()) == 1
        for loser in dropped:
            del scores[loser]
            del tallies[loser]
        if len(dropped) == 0:
            return [candidate[0] for candidate in scores.items()][0], len(scores.keys()) == 1
        active_votes = 0
        for i in range(len(cur_ballots)):
            cur_rank: list[Hashable] = list(cur_ballots[i].ranking)
            for loser in dropped:
                if loser in cur_ballots[i].ranking:
                    cur_rank.remove(loser)
            cur: Ballot = Ballot(tuple(cur_rank), cur_ballots[i].tally)
            del cur_ballots[i]
            cur_ballots.insert(i, cur)
            if len(cur_ballots[i].ranking) > 0:
                tallies[cur_ballots[i].ranking[0]] += cur_ballots[i].tally
                active_votes += cur_ballots[i].tally
        tallies = {}
        size: int = len(set(c for ballot in cur_ballots for c in ballot.ranking))
        points: list[int] = [c for c in range(size - 1, -1, -1)]
        for ballot in cur_ballots:
            for i, candidate in enumerate(ballot.ranking):
                if candidate not in tallies.keys():
                    scores[candidate] = 0
                    tallies[candidate] = 0
                scores[candidate] += points[i] * ballot.tally
            if len(ballot.ranking) > 0:
                tallies[ballot.ranking[0]] += ballot.tally
    max_score: int = max(scores.values())
    winners: list[Hashable] = [candidate for candidate, score in scores.items() if score == max_score]
    return winners[0], len(winners) == 1

scheme: Scheme = nanson
name: str = "Nanson"