<!-- Banner (auto-updated every 6 hours by GitHub Actions) -->
<p align="center">
  <img src="./nyan-cat (fin).svg" width="820" alt="Welcome to Dayeon's Hub"/>
</p>

<br/>



---

## 🌌 About Me

- 🔭 Currently working on quantitative finance models, AI research (SPS), and global SDG platforms

- 🌱 Learning advanced ML, statistical inference, and system design for real-world impact

- 💬 Ask me about AI/ML, quant, research frameworks, or scaling ideas into products

- 📫 Reach me at dayeon603@gmail.com


# ── fetch 94**: Constant `commits` should be `COMMITS` (UPPER_CASE naming)
4. **Line 95**: Constant `prs_merged` should be `PRS_MERGED` (UPPER_CASE naming)

### Recommended Fix:

```python
# Line 73: Rename to GQL
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
"""

# Lines 87-95: Catch specific exceptions and rename variables
try:
    gdata = gh_graphql(GQL)["data"]["user"]
    contrib = gdata["contributionsCollection"]
    COMMITS = contrib["totalCommitContributions"]
    PRS_MERGED = gdata["pullRequests"]["totalCount"]
except (KeyError, TypeError) as e:  # Catch specific exceptions
    print(f"  GraphQL warn: {e} — falling back to 0")
    COMMITS = 0
    PRS_MERGED = 0

# Update references throughout the rest of the file
print(f"  commits:    {COMMITS}  (this year)")
print(f"  PRs merged: {PRS_MERGED}")

svg = replace_stat(svg, "commits",    f"{fmt(COMMITS)} commits",    "#58a6ff")
svg = replace_stat(svg, "PRs merged", f"{fmt(PRS_MERGED)} PRs",     "#3fb950")
