from typing import Hashable
from common.types import Ballot, Result, Scheme
from criterion_util import genOneElection

failureSet: list[dict[str, list[Ballot] | Hashable]]

def condorcet_winner(scheme: Scheme) -> bool:
    global failureSet
    failureSet = list()
    seed: int = 5
    numVoters: int = 1000
    numCandidates: int = 6
    maxUniqueRankings: int = 10
    maxRankingLen: int = 6
    election: list[Ballot]
    expected: Result
    actual: Result
    for s in range(seed):
        for v in range(1, numVoters):
            for c in range(1, numCandidates):
                for ur in range(1, maxUniqueRankings):
                    for rl in range(1, maxRankingLen):
                        election = genOneElection(v, c, ur, rl, 1, s)
                        expected = condorcet(election)                    
                        if expected[1]:
                            actual = scheme(election)
                            if expected[0] != actual[0] or not actual[1]:
                                if electionNotInSet(election):
                                    failureSet.append({'election': election, 'ewinner': expected[0], 'awinner': actual[0]})
                                if len(failureSet) > 10:
                                    printOutException()
                                    return False
    printOutException()
    return True

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

def condorcet(ballots: list[Ballot]) -> Result:
    candidates: set[Hashable] = set(c for ballot in ballots for c in ballot.ranking)
    for candidateA in candidates:
        curWins = 1
        for candidateB in candidates:
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
    return -1, False