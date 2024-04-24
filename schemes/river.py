# pyright: strict
from typing import Hashable

from scheme_types import Ballot, Result, Scheme

# Find pairwise results and convert to symmetric matrix
# Find the largest pairwise winner
# Draw a directed edge from the winner to the loser if:
#   It does not give an existing node multiple parents
#   No cycles are created
# Select the winner, which is the root node

def river(ballots: list[Ballot]) -> Result:
    pairwiseWinners: dict[tuple[Hashable, Hashable], int] = getPairwiseWinners(ballots)
    graph: dict[Hashable, list[Hashable]] = dict()
    numVals: int = len(pairwiseWinners.keys())
    start: Hashable
    end: Hashable
    while numVals > 0:
        maxMargin: list[tuple[Hashable, Hashable]] = [pairwise for pairwise, margin in pairwiseWinners.items() if margin == max(pairwiseWinners.values())]
        validEdges: list[tuple[Hashable, Hashable]] = list()
        for edge in maxMargin:
            start = edge[0]
            end = edge[1]
            multipleParents: bool = False
            for edges in graph.values():
                if end in edges:
                    multipleParents = True
                    break
            if not multipleParents and not cycle(start, end, graph):
                validEdges.append(edge)
            else:
                del pairwiseWinners[(start, end)]
        if len(validEdges) == 0:
            numVals = len(pairwiseWinners.keys())
            continue
        if len(validEdges) > 1:
            return -1, False
        start = validEdges[0][0]
        end = validEdges[0][1]
        if start not in graph.keys():
            graph[start] = list()
        graph[start].append(end)
        del pairwiseWinners[(start, end)]
        numVals = len(pairwiseWinners.keys())
    winners = findRoot(graph)
    return winners[0], len(winners) == 1

def findRoot(graph: dict[Hashable, list[Hashable]]) -> list[Hashable]:
    roots: list[Hashable] = list()
    for node in graph.keys():
        child: bool = False
        for children in graph.values():
            if node in children:
                child = True
                break
        if not child:
            roots.append(node)
    return roots

def cycle(start: Hashable, cur: Hashable, graph: dict[Hashable, list[Hashable]]) -> bool:
    if cur == start:
        return True
    if cur in graph.keys():
        for next in graph[cur]:
            if cycle(start, next, graph):
                return True
    return False

def getPairwiseWins(ballots: list[Ballot]) -> dict[tuple[Hashable, Hashable], int]:
    pairwiseWins: dict[tuple[Hashable, Hashable], int] = dict()
    candidates: list[Hashable] = list(set(c for ballot in ballots for c in ballot.ranking))
    for ballot in ballots:
        for candidateA in candidates:
            for j, candidateB in enumerate(ballot.ranking):
                if candidateA == candidateB:
                    continue
                if candidateA not in ballot.ranking:
                    if (candidateB, candidateA) not in pairwiseWins.keys():
                        pairwiseWins[(candidateB, candidateA)] = 0
                    pairwiseWins[(candidateB, candidateA)] += ballot.tally
                    continue
                i: int = ballot.ranking.index(candidateA)
                if i < j:
                    if (candidateA, candidateB) not in pairwiseWins.keys():
                        pairwiseWins[(candidateA, candidateB)] = 0
                    pairwiseWins[(candidateA, candidateB)] += ballot.tally
    return pairwiseWins

def getPairwiseWinners(ballots: list[Ballot]) -> dict[tuple[Hashable, Hashable], int]:
    pairwiseWins: dict[tuple[Hashable, Hashable], int] = getPairwiseWins(ballots)
    pairwiseWinners: dict[tuple[Hashable, Hashable], int] = dict()
    for x, y in pairwiseWins.keys():
        if (y,x) in pairwiseWins.keys():
            difference: int = pairwiseWins[(x,y)] - pairwiseWins[(y,x)]
            if difference >= 0:
                pairwiseWinners[(x,y)] = difference
        else:
            pairwiseWinners[(x,y)] = pairwiseWins[(x,y)]
    return pairwiseWinners

scheme: Scheme = river
name: str = "River"