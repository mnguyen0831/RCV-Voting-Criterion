from typing import Hashable
from common.types import Ballot, Result, Scheme
from criterion_util import genOneElection

failureSet: list[dict[str, list[Ballot] | Hashable]]

def condorcet_loser(scheme: Scheme) -> bool:
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
                    expected = condorcet(election)    
                    if len(election) == 1 and len(election[0].ranking) == 1:
                        continue 
                    if expected[1]:
                        actual = scheme(election)
                        if expected[0] == actual[0] and actual[1]:
                            if electionNotInSet(election):
                                failureSet.append({'election': election, 'winner': actual[0]})
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
        print(f"Expected loser: {fail['winner']}\n")

def ballotToStr(ballots: list[Ballot]) -> None:
    for ballot in ballots:
        print(f"Count: {ballot.tally}, Ranking: {ballot.ranking}")

def condorcet(ballots: list[Ballot]) -> Result:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    for candidateA in candidates:
        curLosses = 1
        for candidateB in candidates:
            if candidateA == candidateB:
                continue
            curLosses = 0
            for ballot in ballots:
                candidateAI = len(ballot.ranking) if candidateA not in ballot.ranking else ballot.ranking.index(candidateA)
                candidateBI = len(ballot.ranking) if candidateB not in ballot.ranking else ballot.ranking.index(candidateB)
                if candidateAI > candidateBI:
                    curLosses += ballot.tally
                if candidateAI < candidateBI:
                    curLosses -= ballot.tally
            if curLosses <= 0:
                break
        if curLosses > 0:
            return candidateA, True
    return -1, False