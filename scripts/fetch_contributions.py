"""Fetch the last year of contributions for the profile owner into data/contributions.json.

Runs inside the GitHub Action, which provides GITHUB_TOKEN and GITHUB_REPOSITORY_OWNER.
"""
import json
import os
import urllib.request
from pathlib import Path

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def main() -> None:
    login = os.environ.get("PROFILE_LOGIN") or os.environ["GITHUB_REPOSITORY_OWNER"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if "errors" in res:
        raise SystemExit(f"GraphQL error: {res['errors']}")
    cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        {"date": d["date"], "count": d["contributionCount"]}
        for w in cal["weeks"]
        for d in w["contributionDays"]
    ]
    out = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"login": login, "total": cal["totalContributions"], "days": days}, indent=1) + "\n")
    print(f"{len(days)} days, {cal['totalContributions']} contributions")


if __name__ == "__main__":
    main()
