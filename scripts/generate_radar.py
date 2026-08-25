import os
import math
import requests

def get_stats():
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Authorization": f"bearer {token}"} if token else {}
    
    # Defaults based on GitHub activity
    commits_pct = 78
    pr_pct = 15
    reviews_pct = 5
    issues_pct = 2

    # Query GitHub GraphQL API if token is available
    if token:
        query = """
        {
          user(login: "raphgm") {
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              totalIssueContributions
            }
          }
        }
        """
        try:
            resp = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", {}).get("user", {}).get("contributionsCollection", {})
                c = data.get("totalCommitContributions", 0)
                pr = data.get("totalPullRequestContributions", 0)
                rev = data.get("totalPullRequestReviewContributions", 0)
                iss = data.get("totalIssueContributions", 0)
                total = c + pr + rev + iss
                if total > 0:
                    commits_pct = round((c / total) * 100)
                    pr_pct = round((pr / total) * 100)
                    reviews_pct = round((rev / total) * 100)
                    issues_pct = round((iss / total) * 100)
        except Exception as e:
            print("GraphQL query error, using defaults:", e)

    return commits_pct, pr_pct, reviews_pct, issues_pct

def generate_svg(commits_pct, pr_pct, reviews_pct, issues_pct):
    cx, cy, r = 250, 160, 100
    
    top_v = max(0.08, reviews_pct / 100.0)
    right_v = max(0.08, issues_pct / 100.0)
    bottom_v = max(0.08, pr_pct / 100.0)
    left_v = max(0.08, commits_pct / 100.0)

    top_y = cy - (r * top_v)
    right_x = cx + (r * right_v)
    bottom_y = cy + (r * bottom_v)
    left_x = cx - (r * left_v)

    points = f"{left_x:.1f},{cy:.1f} {cx:.1f},{top_y:.1f} {right_x:.1f},{cy:.1f} {cx:.1f},{bottom_y:.1f}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="550" height="320" viewBox="0 0 550 320">
  <rect width="100%" height="100%" rx="14" fill="#1a1b26" stroke="#24283b" stroke-width="1.5"/>
  <text x="275" y="32" fill="#7aa2f7" font-family="-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif" font-size="16" font-weight="bold" text-anchor="middle">GitHub Activity Overview</text>
  
  <!-- Axes -->
  <line x1="{cx-r}" y1="{cy}" x2="{cx+r}" y2="{cy}" stroke="#414868" stroke-width="1.5"/>
  <line x1="{cx}" y1="{cy-r}" x2="{cx}" y2="{cy+r}" stroke="#414868" stroke-width="1.5"/>

  <!-- Grid Rings -->
  <circle cx="{cx}" cy="{cy}" r="{r*0.25}" fill="none" stroke="#24283b" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="{cx}" cy="{cy}" r="{r*0.5}" fill="none" stroke="#24283b" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="{cx}" cy="{cy}" r="{r*0.75}" fill="none" stroke="#24283b" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#414868" stroke-width="1"/>

  <!-- Polygon -->
  <polygon points="{points}" fill="#9ece6a" fill-opacity="0.38" stroke="#9ece6a" stroke-width="2.5"/>
  <circle cx="{left_x:.1f}" cy="{cy}" r="4.5" fill="#9ece6a"/>
  <circle cx="{cx}" cy="{top_y:.1f}" r="4.5" fill="#9ece6a"/>
  <circle cx="{right_x:.1f}" cy="{cy}" r="4.5" fill="#9ece6a"/>
  <circle cx="{cx}" cy="{bottom_y:.1f}" r="4.5" fill="#9ece6a"/>

  <!-- Axis Labels -->
  <text x="{cx-r-12}" y="{cy+4}" fill="#c0caf5" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="end">{commits_pct}% Commits</text>
  <text x="{cx}" y="{cy-r-12}" fill="#c0caf5" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">{reviews_pct}% Code review</text>
  <text x="{cx+r+12}" y="{cy+4}" fill="#c0caf5" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="start">{issues_pct}% Issues</text>
  <text x="{cx}" y="{cy+r+22}" fill="#c0caf5" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle">{pr_pct}% Pull requests</text>
</svg>"""
    return svg

if __name__ == "__main__":
    c, pr, rev, iss = get_stats()
    svg_content = generate_svg(c, pr, rev, iss)
    output_path = "profile-radar.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {output_path} successfully!")
