import schemes.baldwin as baldwin
import schemes.black as black
import schemes.borda as borda
import schemes.bucklin as bucklin
import schemes.coombs as coombs
import schemes.copeland as copeland
import schemes.irv as irv
import schemes.minimax as minimax
import schemes.nanson as nanson
import schemes.river as river
import schemes.rouse as rouse
import schemes.schulze as schulze
import schemes.smith_irv as smith_irv

from scheme_types import Ballot, Scheme

import random
import itertools
import math
from typing import Hashable

num_voters: int
num_candidates: int
max_unique_rankings: int
max_ranking_length: int
min_ranking_length: int
total_possible_unique_ballots: int

def getScheme(scheme: str) -> Scheme:
    match scheme:
        case 'baldwin':
            return baldwin.scheme
        case 'black':
            return black.scheme
        case 'borda':
            return borda.scheme
        case 'bucklin':
            return bucklin.scheme
        case 'coombs':
            return coombs.scheme
        case 'copeland':
            return copeland.scheme
        case 'irv':
            return irv.scheme
        case 'minimax':
            return minimax.scheme
        case 'nanson':
            return nanson.scheme
        case 'river':
            return river.scheme
        case 'rouse':
            return rouse.scheme
        case 'schulze':
            return schulze.scheme
        case 'smith_irv':
            return smith_irv.scheme
        case _:
            scheme = 'borda'
            return borda.scheme

def genOneElection(voters: int, candidates: int, maxUR: int, seed: int = 1, maxRL: int = -1, minRL: int = -1) -> list[Ballot]:
    global num_voters, num_candidates, max_unique_rankings, max_ranking_length, min_ranking_length
    num_voters = voters
    num_candidates = candidates
    max_unique_rankings = maxUR
    max_ranking_length = maxRL if maxRL != -1 else candidates
    min_ranking_length = minRL if minRL != -1 else 1
    random.seed(seed)
    validateParams()
    return genElection()

def validateParams() -> None:
    global num_voters, num_candidates, max_unique_rankings, max_ranking_length, min_ranking_length, total_possible_unique_ballots
    if min_ranking_length > num_candidates or min_ranking_length < 0:
        min_ranking_length = num_candidates
    if max_ranking_length > num_candidates or max_ranking_length < 1 or max_ranking_length < min_ranking_length:
        max_ranking_length = num_candidates
    total_possible_unique_ballots = validateNumUnique()
    if max_unique_rankings < 1 or max_unique_rankings > total_possible_unique_ballots:
        max_unique_rankings = total_possible_unique_ballots if total_possible_unique_ballots < num_voters else num_voters
    elif max_unique_rankings > num_voters:
        max_unique_rankings = num_voters

def validateNumUnique() -> int:
    global num_candidates, max_ranking_length
    return math.factorial(num_candidates) // math.factorial(num_candidates - max_ranking_length) + validateNumUniqueHelper(max_ranking_length - 1)

def validateNumUniqueHelper(cur : int) -> int:
    global num_candidates, min_ranking_length
    if cur < min_ranking_length:
        return 0
    return math.factorial(num_candidates) // math.factorial(num_candidates - cur) + validateNumUniqueHelper(cur - 1)

def genBallot() -> tuple[int, ...]:
    global max_ranking_length, min_ranking_length, num_candidates
    ranking_length = random.randint(min_ranking_length, max_ranking_length)
    return tuple(random.sample(range(num_candidates), ranking_length))

def selUniqueBallots(num_unique : int) -> list[dict[str, tuple[int, ...] | int]]:
    global max_ranking_length, min_ranking_length, num_candidates
    permutations: list[tuple[int, ...]] = list()
    ballots: list[dict[str, tuple[int, ...] | int]] = list()
    for ranking_length in range(min_ranking_length, max_ranking_length + 1):
        permutations.extend(list(itertools.permutations(range(num_candidates), ranking_length)))
    selectedBallots: list[int] = random.sample(range(len(permutations)), num_unique)
    for i in selectedBallots:
        ballots.append({"ranking" : permutations[i], "count" : 0})
    return ballots

def genUniqueBallots() -> list[dict[str, tuple[int, ...] | int]]:
    global max_unique_rankings, total_possible_unique_ballots
    num_unique = random.randint(1, max_unique_rankings)
    if num_unique > total_possible_unique_ballots % 3:
        return selUniqueBallots(num_unique)
    ballots: list[dict[str, tuple[int, ...] | int]] = []
    unique_ballots: list[tuple[int, ...]] = []
    for _ in range(num_unique):
        cur: tuple[int, ...] = genBallot()
        while any(cur == bal for bal in unique_ballots):
            cur = genBallot()
        unique_ballots.append(cur)
        ballots.append({"ranking" : cur, "count" : 0})
    return ballots      

def genElection() -> list[Ballot]:
    global num_voters
    election: list[dict[str, tuple[int, ...] | int]] = genUniqueBallots()
    if len(election) == 1:
        election[0]["count"] = num_voters
        return convertElection(election)
    elif len(election) == 2:
        first_votes = random.randint(1, num_voters - 1)
        election[0]["count"] = first_votes
        election[1]["count"] = num_voters - first_votes
        return convertElection(election)
    bounds: list[int] = list()
    for _ in range(len(election) - 1):
        cur = random.randint(1, num_voters - 1)
        while cur in bounds:
            cur = random.randint(1, num_voters - 1)
        bounds.append(cur)
    bounds.sort()
    i = 0
    for ballot in election:
        if i == 0:
            ballot["count"] = bounds[i]
        elif i == len(election) - 1:
            ballot["count"] = num_voters - bounds[i - 1]
        else:
            ballot["count"] = bounds[i] - bounds[i - 1]
        i = i + 1
    return convertElection(election)  

def convertElection(election: list[dict[str, tuple[int, ...] | int]]) -> list[Ballot]:
    converted: list[Ballot] = list()
    for ballot in election:
        converted.append(Ballot(ballot["ranking"], ballot["count"])) # Split election into a ranking and count list
    return converted

def electionNotInSet(failureSet: list[dict[str, list[Ballot] | Hashable]], election: list[Ballot]) -> bool:
    for e in failureSet:
        for sb in e['election']:
            numSame: int = 0
            for nb in election:
                if sb.ranking == nb.ranking:
                    numSame += 1
            if numSame == len(election):
                return False
    return True

def ballotToStr(ballots: list[Ballot]) -> None:
    print('-----------------------------------------------')
    for ballot in ballots:
        print(f"Count: {ballot.tally}, Ranking: {ballot.ranking}")
    print('-----------------------------------------------')