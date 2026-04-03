"""
generate_banner.py
──────────────────
Fetches live GitHub stats for a user and writes them into nyan-cat.svg.
Run by GitHub Actions on a schedule, or manually.

Requires env var: GITHUB_TOKEN (set as a repo secret)
Requires env var: GITHUB_USERNAME (set in the workflow)
"""

import os
import re
import json
import urllib.request
import urllib.error

# ── config ────────────────────────────────────────────────────────────────────
USERNAME = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
TOKEN    = os.environ.get("GITHUB_TOKEN", "")
SVG_IN   = "nyan-cat.svg"
SVG_OUT  = "nyan-cat.svg"   # overwrite in place

# ── helpers ───────────────────────────────────────────────────────────────────
def gh(path):
    """Call the GitHub REST API and return parsed JSON."""
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "nyan-banner-bot",
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def gh_graphql(query):
    """Call the GitHub GraphQL API."""
    url = "https://api.github.com/graphql"
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "nyan-banner-bot",
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def fmt(n):
    """Format a number with commas, e.g. 1234 → '1,234'."""
    return f"{n:,}"

# ── fetch stats ───────────────────────────────────────────────────────────────
print(f"Fetching stats for @{USERNAME} ...")

# 1. Basic user info (public repos, followers)
user = gh(f"/users/{USERNAME}")
public_repos = user["public_repos"]
followers    = user["followers"]

# 2. Total stars across all repos (paginated)
total_stars = 0
page = 1
while True:
    repos = gh(f"/users/{USERNAME}/repos?per_page=100&page={page}")
    if not repos:
        break
    total_stars += sum(r["stargazers_count"] for r in repos)
    if len(repos) < 100:
        break
    page += 1

# 3. Total commits + PRs merged via GraphQL (includes private if token has scope)
Rename to GQL
GQL = f"""
{{
  user(login: "{USERNAME}") {{
    contributionsCollection {{
      totalCommitContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
    }}
    pullRequests(states: MERGED) {{
      totalCount
    }}
  }}
}}
try:
    gdata = gh_graphql(gql)["data"]["user"]
    contrib = gdata["contributionsCollection"]
    commits    = contrib["totalCommitContributions"]
    prs_merged = gdata["pullRequests"]["totalCount"]
except Exception as e:
    print(f"  GraphQL warn: {e} — falling back to 0")
    commits    = 0
    prs_merged = 0

print(f"  repos:      {public_repos}")
print(f"  stars:      {total_stars}")
print(f"  followers:  {followers}")
print(f"  commits:    {commits}  (this year)")
print(f"  PRs merged: {prs_merged}")

# ── patch the SVG ─────────────────────────────────────────────────────────────
with open(SVG_IN, "r", encoding="utf-8") as f:
    svg = f.read()

def replace_stat(svg, placeholder, value, color):
    """
    Replace a stat text node.
    The SVG has lines like:
        <text ...>commits</text>
        <text ...>PRs merged</text>
        <text ...>repos</text>
    We replace the content with "1,234 commits" etc.
    We also inject the live number into the preceding <text> node.
    """
    # Replace pattern:  >NUMBER_OR_WORD placeholder</text>
    pattern = rf'(>{re.escape(placeholder)}<)'
    replacement = f'>{value}<'
    new_svg, n = re.subn(pattern, replacement, svg)
    if n:
        print(f"  patched '{placeholder}' → '{value}'")
    return new_svg

# Map placeholder labels to (value_string)
svg = replace_stat(svg, "commits",    f"{fmt(commits)} commits",    "#58a6ff")
svg = replace_stat(svg, "PRs merged", f"{fmt(prs_merged)} PRs",     "#3fb950")
svg = replace_stat(svg, "repos",      f"{fmt(public_repos)} repos", "#d2a8ff")

with open(SVG_OUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"✓ Written to {SVG_OUT}")
