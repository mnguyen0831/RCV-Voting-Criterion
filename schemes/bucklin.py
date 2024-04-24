# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme


# Tally up all first place votes
# If there's a majority winner, pick them
# If not, then add the second place votes to the tally
# Repeat with nth place votes until a majority is found
# If there's a ballot with no nth place votes, ignore it
# If there's no majority winner by the end, the candidate with most votes wins
# If a majority is found, and it's a tie, report tie

def bucklin(ballots: list[Ballot]) -> Result:
    scores: dict[Hashable, int] = {}
    numActiveVotes = 0
    round = 0
    maxSize = 0
    majority: list[Hashable] = []
    winners: list[Hashable] = []
    for ballot in ballots:
        if len(ballot.ranking) > maxSize:
            maxSize = len(ballot.ranking)
        for candidate in ballot.ranking:
            scores[candidate] = 0
        numActiveVotes += ballot.tally
    majorityThreshold = numActiveVotes // 2
    while len(majority) == 0 and round < maxSize:
        for ballot in ballots:
            if len(ballot.ranking) > round:
                scores[ballot.ranking[round]] += ballot.tally
        for candidate in scores.keys():
            if scores[candidate] > majorityThreshold:
                majority.append(candidate)
        round += 1
    mostVotes = max(scores.values())
    if len(majority) > 0:
        for candidate in majority:
            if scores[candidate] == mostVotes:
                winners.append(candidate)
    else:
        for candidate in scores.keys():
            if scores[candidate] == mostVotes:
                winners.append(candidate)
    return winners[0], len(winners) == 1

scheme: Scheme = bucklin
name: str = "Bucklin"