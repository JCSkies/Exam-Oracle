# 1) main.py

The sole purpose main is to orchestrate the request cycle. The cycle is broken down into 5 steps:

a) verify webhook secret
b) handle merge requests
c) find/fetch MR changes
d) analyze risk (using a helper class)
e) post/update a comment

The main class is made simple (not smart/ML) to ensure stability and delegates the operations to separate classes.

# 2) gitlab_client.py

(Used in 3rd step of main.py pipeline)

This is a supporting class

Obtains MR
Finds changes
Obtains/creates/updates MR notes

Follows Single Responsibility Principle; only does operations pertaining to the MR.
Methods are used in main.py
Makes changes easier

# 3) risk_engine.py

(Used in 4th step of main.py pipeline)

Finds risk level from path (RiskResult)

Scores 0-10 and sees if it the MR changes are low/medium/high risk and returns reasons why they are that risk

Returns a class RiskResult(...) since returning the whole class means it is well-defined and returns exactly as intended.

Why not dictionary? Dctionary/tuple makes it harder to extend/no structure guarantee.
Typos may occur, no type guarantee, no auto-complete help.


# 4) reporter.py


(Used in 5th step of main.py pipeline)

Forms the report as a comment series based on the result from risk_engine.py

Upserts risk comment (if one exists, update it. if not, create a new one)

# 5) models.py  

(Usedw in 2nd step of main.py pipeline)

Pulls ONLY what we need from the GitLab webhook 

Defines what we need from a MergeRequest with action as open/update/merge/close as the main ones we'll use (discards other action types in main.py)

# g6) config.py 

Makes sure obtaining GITLAB webhook secrets and configs are only done from a single class (Single Responsibility Principle). 

Ensures that obtaining the GitLab token is not written everywhere.


# -----

Main takeaway: main.py is the pipeline for the backend; the other classes are supporting classes that have a single responsibility to ensure changes/updates to any part of the code is only done in a single class (does not affect the rest).