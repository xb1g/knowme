"use client";

import { useEffect, useState } from "react";
import { GitFork, Clock, RefreshCw, CheckSquare2, Square } from "lucide-react";
import { useRouter } from "next/navigation";

interface GhRepo {
  repo_id: string;
  display_name: string;
  github_full_name: string;
  description: string;
  language: string;
  updated_at: string;
  selected: boolean;
}

const LANG_COLORS: Record<string, string> = {
  TypeScript: "bg-blue-500/20 text-blue-300",
  JavaScript: "bg-yellow-500/20 text-yellow-300",
  Python: "bg-green-500/20 text-green-300",
  Jupyter: "bg-orange-500/20 text-orange-300",
  default: "bg-white/10 text-white/50",
};

export function RepoSelector() {
  const router = useRouter();
  const [repos, setRepos] = useState<GhRepo[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/repos")
      .then((r) => r.json())
      .then((data) => {
        setRepos(data.repos ?? []);
        setSelected(
          new Set(
            (data.repos ?? [])
              .filter((r: GhRepo) => r.selected)
              .map((r: GhRepo) => r.repo_id)
          )
        );
      })
      .catch(() => setError("Failed to load repos"))
      .finally(() => setLoading(false));
  }, []);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  async function analyze() {
    setSaving(true);
    await fetch("/api/repos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected_repos: [...selected] }),
    });
    setSaving(false);
    router.refresh();
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-white/30 text-sm py-4">
        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
        Loading your repos…
      </div>
    );
  }

  if (error) {
    return <p className="text-red-400 text-sm py-4">{error}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {repos.map((repo) => {
          const isSelected = selected.has(repo.repo_id);
          const langClass = LANG_COLORS[repo.language] ?? LANG_COLORS.default;
          return (
            <button
              key={repo.repo_id}
              onClick={() => toggle(repo.repo_id)}
              className={`text-left rounded-xl border p-4 transition-all duration-150 space-y-2 ${
                isSelected
                  ? "border-white/30 bg-white/8 ring-1 ring-white/20"
                  : "border-white/8 bg-white/[0.02] hover:border-white/15 hover:bg-white/5"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitFork className="h-3.5 w-3.5 text-white/40" />
                  <span className="text-sm font-semibold text-white font-mono">
                    {repo.display_name}
                  </span>
                </div>
                {isSelected ? (
                  <CheckSquare2 className="h-4 w-4 text-emerald-400 shrink-0" />
                ) : (
                  <Square className="h-4 w-4 text-white/20 shrink-0" />
                )}
              </div>
              {repo.description && (
                <p className="text-xs text-white/40 leading-relaxed line-clamp-2">
                  {repo.description}
                </p>
              )}
              <div className="flex items-center gap-2">
                {repo.language && (
                  <span
                    className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${langClass}`}
                  >
                    {repo.language}
                  </span>
                )}
                <span className="flex items-center gap-1 text-[10px] text-white/25 font-mono ml-auto">
                  <Clock className="h-2.5 w-2.5" />
                  {new Date(repo.updated_at).toLocaleDateString()}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex items-center justify-between pt-2">
        <p className="text-xs text-white/30 font-mono">
          {selected.size} repo{selected.size !== 1 ? "s" : ""} selected
        </p>
        <button
          onClick={analyze}
          disabled={saving || selected.size === 0}
          className="flex items-center gap-2 rounded-full bg-white/10 hover:bg-white/15 disabled:opacity-40 disabled:cursor-not-allowed px-5 py-2 text-sm font-semibold text-white transition-colors"
        >
          {saving && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
          {saving ? "Saving…" : "Save Selection"}
        </button>
      </div>
    </div>
  );
}
