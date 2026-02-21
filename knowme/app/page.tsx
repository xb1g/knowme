import { readFileSync, existsSync } from "fs";
import path from "path";
import { GitBranch, Layers, Target, Sparkles, Star, BookOpen, Zap } from "lucide-react";

interface RepoProfile {
  repo_id: string;
  skills: string[];
  intentions: string[];
  interests: string[];
  evidence_ids: string[];
}

interface Consensus {
  shared_skills: string[];
  shared_intentions: string[];
  interest_map: Record<string, string[]>;
  repo_count: number;
}

interface MeshData {
  repo_count: number;
  profiles: RepoProfile[];
  consensus: Consensus;
}

function loadMeshData(): MeshData | null {
  const jsonPath = path.join(process.cwd(), "..", "repo_mesh", "output", "latest_profile.json");
  if (!existsSync(jsonPath)) return null;
  return JSON.parse(readFileSync(jsonPath, "utf-8"));
}

const REPO_COLORS = [
  { bg: "bg-[oklch(0.25_0.08_264)]", border: "border-[oklch(0.45_0.18_264)]", dot: "bg-[oklch(0.65_0.22_264)]", tag: "bg-[oklch(0.3_0.1_264)] text-[oklch(0.85_0.12_264)]" },
  { bg: "bg-[oklch(0.25_0.08_162)]", border: "border-[oklch(0.45_0.15_162)]", dot: "bg-[oklch(0.65_0.18_162)]", tag: "bg-[oklch(0.3_0.1_162)] text-[oklch(0.85_0.12_162)]" },
  { bg: "bg-[oklch(0.25_0.08_70)]",  border: "border-[oklch(0.5_0.18_70)]",   dot: "bg-[oklch(0.7_0.2_70)]",   tag: "bg-[oklch(0.3_0.1_70)] text-[oklch(0.88_0.15_70)]" },
  { bg: "bg-[oklch(0.25_0.08_304)]", border: "border-[oklch(0.45_0.18_304)]", dot: "bg-[oklch(0.65_0.22_304)]", tag: "bg-[oklch(0.3_0.1_304)] text-[oklch(0.85_0.12_304)]" },
];

function Tag({ label, className }: { label: string; className: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}

function EmptySlot() {
  return (
    <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-white/5 text-white/25 italic">
      none detected
    </span>
  );
}

function Section({ icon, label, items, tagClass }: { icon: React.ReactNode; label: string; items: string[]; tagClass: string }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1.5 text-white/50">
        {icon}
        <span className="text-xs font-semibold uppercase tracking-widest">{label}</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {items.length > 0
          ? items.map((item) => <Tag key={item} label={item} className={tagClass} />)
          : <EmptySlot />}
      </div>
    </div>
  );
}

export default function Home() {
  const data = loadMeshData();

  if (!data) {
    return (
      <div className="dark flex min-h-screen items-center justify-center bg-background text-foreground">
        <div className="text-center space-y-3">
          <p className="text-4xl">⚠️</p>
          <p className="text-lg font-semibold">No mesh data found</p>
          <p className="text-sm text-muted-foreground font-mono">
            Run: <code>python -m repo_mesh.cli --repos repo_mesh/config/repos.yaml --out repo_mesh/output/latest_profile.json</code>
          </p>
        </div>
      </div>
    );
  }

  const { profiles, consensus } = data;

  return (
    <div className="dark min-h-screen bg-background text-foreground">
      {/* Subtle grid bg */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          backgroundImage: "linear-gradient(oklch(1 0 0 / 3%) 1px, transparent 1px), linear-gradient(90deg, oklch(1 0 0 / 3%) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      <div className="relative max-w-5xl mx-auto px-6 py-12 space-y-10">

        {/* Header */}
        <header className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-white/40 text-xs font-mono uppercase tracking-widest mb-2">
              <span className="inline-block w-4 h-px bg-white/30" />
              human-centered agent mesh
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white">
              KnowMe <span className="text-white/30">·</span>{" "}
              <span className="text-white/70">Repo Mesh</span>
            </h1>
            <p className="text-sm text-white/40 font-mono">
              {data.repo_count} repo{data.repo_count !== 1 ? "s" : ""} analyzed · read-only · on-demand
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-mono text-white/50">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            latest run
          </div>
        </header>

        {/* Consensus Panel */}
        <section className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 space-y-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-400" />
            <h2 className="text-sm font-bold uppercase tracking-widest text-white/60">Consensus</h2>
            <span className="ml-auto text-xs font-mono text-white/30">
              across {data.repo_count} repos
            </span>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            {/* Shared Skills */}
            <div className="space-y-3">
              <div className="flex items-center gap-1.5 text-white/40">
                <Zap className="h-3.5 w-3.5" />
                <span className="text-xs font-semibold uppercase tracking-widest">Shared Skills</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {consensus.shared_skills.length > 0
                  ? consensus.shared_skills.map((s) => (
                      <Tag key={s} label={s} className="bg-amber-500/15 text-amber-300" />
                    ))
                  : <EmptySlot />}
              </div>
            </div>

            {/* Shared Intentions */}
            <div className="space-y-3">
              <div className="flex items-center gap-1.5 text-white/40">
                <Target className="h-3.5 w-3.5" />
                <span className="text-xs font-semibold uppercase tracking-widest">Shared Intentions</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {consensus.shared_intentions.length > 0
                  ? consensus.shared_intentions.map((s) => (
                      <Tag key={s} label={s} className="bg-sky-500/15 text-sky-300" />
                    ))
                  : <EmptySlot />}
              </div>
            </div>

            {/* Interest Map */}
            <div className="space-y-3">
              <div className="flex items-center gap-1.5 text-white/40">
                <Star className="h-3.5 w-3.5" />
                <span className="text-xs font-semibold uppercase tracking-widest">Interest Map</span>
              </div>
              <div className="space-y-2">
                {Object.keys(consensus.interest_map).length > 0
                  ? Object.entries(consensus.interest_map).map(([interest, repos]) => (
                      <div key={interest} className="space-y-1">
                        <Tag label={interest} className="bg-violet-500/15 text-violet-300" />
                        <div className="flex flex-wrap gap-1 pl-1">
                          {repos.map((r) => (
                            <span key={r} className="text-[10px] font-mono text-white/30">{r}</span>
                          ))}
                        </div>
                      </div>
                    ))
                  : <EmptySlot />}
              </div>
            </div>
          </div>
        </section>

        {/* Repo Cards */}
        <section className="space-y-4">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-white/40" />
            <h2 className="text-sm font-bold uppercase tracking-widest text-white/60">Per-Repo Profiles</h2>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {profiles.map((profile, i) => {
              const color = REPO_COLORS[i % REPO_COLORS.length];
              return (
                <div
                  key={profile.repo_id}
                  className={`rounded-2xl border ${color.border}/40 ${color.bg} p-5 space-y-4 transition-all duration-200 hover:border-opacity-80`}
                >
                  {/* Card header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`h-2.5 w-2.5 rounded-full ${color.dot}`} />
                      <span className="font-semibold text-white font-mono text-sm">{profile.repo_id}</span>
                    </div>
                    <div className="flex items-center gap-1 text-white/30 text-xs font-mono">
                      <GitBranch className="h-3 w-3" />
                      {profile.evidence_ids.length} evidence
                    </div>
                  </div>

                  <div className="space-y-3">
                    <Section
                      icon={<Zap className="h-3 w-3" />}
                      label="Skills"
                      items={profile.skills}
                      tagClass={color.tag}
                    />
                    <Section
                      icon={<Target className="h-3 w-3" />}
                      label="Intentions"
                      items={profile.intentions}
                      tagClass={color.tag}
                    />
                    <Section
                      icon={<BookOpen className="h-3 w-3" />}
                      label="Interests"
                      items={profile.interests}
                      tagClass={color.tag}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Footer */}
        <footer className="flex items-center justify-between border-t border-white/5 pt-6 text-xs font-mono text-white/20">
          <span>repo_mesh · read-only · derived signals only</span>
          <span>xb1g/knowme</span>
        </footer>
      </div>
    </div>
  );
}
