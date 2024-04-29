# RCV-Voting-Criterion
Generates examples of elections that cause the input scheme to fail the input criterion.
## How to use the validator
In the folder containing criterion.py, run the command:
```
    python criterion.py --scheme [scheme] --criterion [criterion]
```
### Flags
The only two flags that are 'necessary' are --scheme and --criterion. However, if they're
unused, criterion.py will default to testing Borda against Condorcet Winner.
#### --scheme [scheme]
Expects the name of a RCV voting scheme that exists in the schemes folder.

#### --criterion [criterion]
Expects the name of a RCV voting criterion that exists in the criteria folder.

#### --realistic
This sets the number of candidates to 7, the number of voters to 10 million, and the 
number of unique ballots to 10. These numbers are roughly based on the 2022 California
General Election.

#### --num-candidates [num_candidates]
Sets the number of candidates used. By default, the number of candidates is 4.

#### --num-voters [num_voters]
Sets the number of voters used. By default, the number of voters is 20.

#### --num-unique-ballots [num_unique_ballots]
Sets the number of unique ballots used. By default, the number of candidates is 5.

#### --all
Generates and checks the entire sample size, rather than stopping after an example is 
found.

#### --sample [sample]
The number of elections to generate and check. By default, the number is 100,000.

## Criterion
### General 
For all of these criteria, the expected winner was first determined, and then compared to
the actual winner. If there was a mismatch, the election was an example of a failure.

#### condorcet_loser
The candidate that lost to every other candidate pairwise should not be the winner.

#### condorcet_winner
The candidate that won to every other candidate pairwise should be the winner.

#### majority 
The candidate preferred by the majority of voters should be the winner.

#### reversal
If everyone's preferences were reversed, the candidate who initially won should not still
be the winner.

### later_no_harm
Omitting later preferences should not cause a more preferred candidate to lose to a less
preferred candidate.

#### General Approach
In an election with no condorcet winner, the actual winner should have one candidate that
beats them pairwise. If the winner changes to a preferred candidate as a result of 
removing all later preferences from ballots by voters who prefer the candidate with the 
most pairwise wins against the actual winner to the actual winner, then the scheme does 
not pass this criterion.

### later_no_help
Recording later preferences should should not cause a more preferred candidate to win 
against a less preferred candidate.

#### General Approach
In an election with no condorcet winner, the actual winner should have one candidate that
beats them pairwise. If the winner changes to a preferred candidate as a result of 
completing all incomplete ballots by voters who prefer the candidate with the 
most pairwise wins against the actual winner to the actual winner, then the scheme does 
not pass this criterion.

### monotonicity
If voters were to shift support to the winning candidate, that should not cause the 
candidate to lose.

#### General Approach
If enough voters who prefer a candidate that has the least chance of winning an election 
shift their support towards the actual winner, while maintaining the order of their 
relative preferences, they may shift support away from a candidate that would beat the
actual winner's strongest challenger, causing that challenger to win overall. 

### participation
Voters should not be able to elect a more preferred candidate by not participating in the
election.

#### General Approach
If enough voters who prefer the winner to a candidate who beats the winner pairwise 
choose to participate when they initially didn't, the candidate they prefer less will 
have more to gain from their participation than the actual winner, causing the less
preferred candidate to win.