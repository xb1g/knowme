import { NextResponse } from "next/server";
import { readFileSync, writeFileSync, existsSync } from "fs";
import path from "path";

// GET — list user's GitHub repos + current selection from repos.yaml
export async function GET() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return NextResponse.json({ error: "GITHUB_TOKEN not set" }, { status: 500 });
  }

  // fetch repos from GitHub
  const res = await fetch("https://api.github.com/user/repos?per_page=50&sort=updated", {
    headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json" },
    cache: "no-store",
  });
  const ghRepos = await res.json();

  // load current repos.yaml to know which are selected
  const yamlPath = path.join(process.cwd(), "..", "repo_mesh", "config", "repos.yaml");
  let selectedIds: string[] = [];
  if (existsSync(yamlPath)) {
    const content = readFileSync(yamlPath, "utf-8");
    // parse simple yaml: find lines with "repo_id:" and "selected: true"
    const repoBlocks = content.split(/^  - /m).slice(1);
    for (const block of repoBlocks) {
      const idMatch = block.match(/repo_id:\s*["']?([^"'\n]+)["']?/);
      const selMatch = block.match(/selected:\s*(true|false)/);
      if (idMatch && selMatch?.[1] === "true") {
        selectedIds.push(idMatch[1].trim());
      }
    }
  }

  const repos = (Array.isArray(ghRepos) ? ghRepos : []).map((r: any) => ({
    repo_id: r.name,
    display_name: r.name,
    github_full_name: r.full_name,
    description: r.description ?? "",
    language: r.language ?? "",
    updated_at: r.updated_at,
    selected: selectedIds.includes(r.name),
  }));

  return NextResponse.json({ repos });
}

// POST — save selection to repos.yaml
export async function POST(req: Request) {
  const { selected_repos } = (await req.json()) as { selected_repos: string[] };
  const token = process.env.GITHUB_TOKEN;

  // fetch all repos to get full metadata
  const res = await fetch("https://api.github.com/user/repos?per_page=50&sort=updated", {
    headers: { Authorization: `Bearer ${token ?? ""}`, Accept: "application/vnd.github+json" },
    cache: "no-store",
  });
  const ghRepos = await res.json();

  // build repos.yaml content manually (no js-yaml dependency needed)
  const repoLines = (Array.isArray(ghRepos) ? ghRepos : []).map((r: any) => {
    const isSelected = selected_repos.includes(r.name);
    return [
      `  - repo_id: "${r.name}"`,
      `    display_name: "${r.name}"`,
      `    github_full_name: "${r.full_name}"`,
      `    local_path: "./workspace/${r.name}"`,
      `    selected: ${isSelected}`,
      `    read_only: true`,
    ].join("\n");
  });

  const yamlContent = "repos:\n" + repoLines.join("\n");
  const yamlPath = path.join(process.cwd(), "..", "repo_mesh", "config", "repos.yaml");
  writeFileSync(yamlPath, yamlContent, "utf-8");

  return NextResponse.json({ ok: true, updated: selected_repos.length });
}
