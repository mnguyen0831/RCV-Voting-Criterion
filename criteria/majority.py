from typing import Hashable
from common.types import Ballot, Result, Scheme
from criterion_util import genOneElection

failureSet: list[dict[str, list[Ballot] | Hashable]]

def majority(scheme: Scheme) -> bool:
    global failureSet
    failureSet = list()
    seed: int = 5
    numVoters: int = 1000
    numCandidates: int = 6
    maxUniqueRankings: int = 10
    election: list[Ballot]
    expected: Result
    actual: Result
    for s in range(seed):
        for v in range(10, numVoters):
            for c in range(2, numCandidates):
                for ur in range(3, maxUniqueRankings):
                    election = genOneElection(v, c, ur, c, 1, s)
                    expected = majorityWin(election)    
                    if expected[1]:
                        actual = scheme(election)
                        if expected[0] != actual[0] and actual[1]:
                            if electionNotInSet(election):
                                failureSet.append({'election': election, 'ewinner': expected[0], 'awinner': actual[0]})
                            if len(failureSet) > 10:
                                printOutException()
                                return False
    printOutException()
    return len(failureSet) == 0

def electionNotInSet(election: list[Ballot]) -> bool:
    global failureSet
    for e in failureSet:
        for sb in e['election']:
            numSame: int = 0
            for nb in election:
                if sb.ranking == nb.ranking:
                    numSame += 1
            if numSame == len(election):
                return False
    return True

def printOutException() -> None:
    global failureSet
    for fail in failureSet:
        ballotToStr(fail['election'])
        print(f"Expected winner: {fail['ewinner']}, Actual winner: {fail['awinner']}\n")

def ballotToStr(ballots: list[Ballot]) -> None:
    for ballot in ballots:
        print(f"Count: {ballot.tally}, Ranking: {ballot.ranking}")

def tally(ballots: list[Ballot]) -> dict[Hashable, int]:
    tallies: dict[Hashable,int] = dict()
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            if ballot.ranking[0] not in tallies.keys():
                tallies[ballot.ranking[0]] = 0
            tallies[ballot.ranking[0]] += ballot.tally
    return tallies

def majorityWin(ballots: list[Ballot]) -> Result:
    tallies: dict[Hashable, int] = tally(ballots)
    active_votes = 0
    for ballot in ballots:
        if len(ballot.ranking) > 0:
            active_votes += ballot.tally
    if max(tallies.values()) > active_votes // 2:
        winners: list[Hashable] = [candidate for candidate, score in tallies.items() if score == max(tallies.values())]
        return list(winners)[0], len(winners) == 1
    return -1, False 