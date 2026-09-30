"""Exact, owner-approved basic problem exclusions; never match by algorithm name."""
from pathlib import PurePosixPath


def excluded_driver(driver, policy):
    path = PurePosixPath(driver)
    if len(path.parts) != 3 or path.parts[0] != 'verify':
        return False
    judge = path.parts[1]
    problem = path.name.split('.')[0]
    return any(row['judge'] == judge and row['problem'] == problem
               for row in policy['problems'])
