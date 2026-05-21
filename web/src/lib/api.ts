// SkillForge API client
// Uses fetch to the skillforge-api backend, falls back to hardcoded mock data

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SkillPermission {
  tool: string;
  risk: 'low' | 'medium' | 'high' | 'critical';
  description?: string;
}

export interface Skill {
  name: string;
  version: string;
  author: string;
  description: string;
  tags: string[];
  security_score: number;
  validation_score: number;
  downloads: number;
  permissions: SkillPermission[];
  install_command?: string;
  repository?: string;
  created_at?: string;
  updated_at?: string;
  category?: string;
  homepage?: string;
  license?: string;
}

export interface SkillsResponse {
  skills: Skill[];
  total: number;
  page: number;
  limit: number;
}

export interface SkillResponse {
  skill: Skill;
}

// Hardcoded fallback skills
const MOCK_SKILLS: Skill[] = [
  {
    name: 'github-code-review',
    version: '2.1.0',
    author: 'skillforge-core',
    description:
      'Automated code review skill that analyzes pull requests for code quality, security vulnerabilities, and best practices. Integrates with GitHub Actions for seamless CI/CD pipelines. Supports configurable rulesets and AI-powered suggestions.',
    tags: ['github', 'code-review', 'security', 'ci-cd', 'automation'],
    security_score: 92,
    validation_score: 88,
    downloads: 15420,
    permissions: [
      { tool: 'github.pull_requests.read', risk: 'low', description: 'Read PR data' },
      { tool: 'github.pull_requests.comment', risk: 'medium', description: 'Post review comments' },
      { tool: 'github.repos.read', risk: 'low', description: 'Read repository metadata' },
      { tool: 'code_analysis.run', risk: 'low', description: 'Run linting and SAST' },
    ],
    install_command: 'skillforge install github-code-review',
    repository: 'https://github.com/munnmajithia/skillforge-skills',
    created_at: '2025-11-15T09:00:00Z',
    updated_at: '2026-05-10T14:30:00Z',
    category: 'CI/CD',
    license: 'MIT',
    homepage: 'https://skillforge.dev/skills/github-code-review',
  },
  {
    name: 'linear-issue-manager',
    version: '1.4.0',
    author: 'skillforge-community',
    description:
      'Intelligent issue management for Linear. Auto-triage, sprint planning assistance, dependency tracking, and cross-team coordination. Features natural language issue creation and smart label suggestions based on issue content.',
    tags: ['linear', 'project-management', 'issues', 'agile', 'automation'],
    security_score: 85,
    validation_score: 91,
    downloads: 8920,
    permissions: [
      { tool: 'linear.issues.read', risk: 'low', description: 'Read Linear issues' },
      { tool: 'linear.issues.write', risk: 'medium', description: 'Create and update issues' },
      { tool: 'linear.teams.read', risk: 'low', description: 'Read team data' },
      { tool: 'linear.sprints.read', risk: 'low', description: 'Read sprint data' },
    ],
    install_command: 'skillforge install linear-issue-manager',
    repository: 'https://github.com/skillforge-community/linear-issue-manager',
    created_at: '2025-12-20T10:00:00Z',
    updated_at: '2026-04-28T08:15:00Z',
    category: 'Project Management',
    license: 'Apache-2.0',
    homepage: 'https://skillforge.dev/skills/linear-issue-manager',
  },
  {
    name: 'postgres-schema-explorer',
    version: '3.0.1',
    author: 'skillforge-data',
    description:
      'Deep database introspection skill for PostgreSQL. Visualizes schema relationships, generates migration plans, detects performance bottlenecks, and suggests index optimizations. Supports multi-tenant database architectures and connection pooling configurations.',
    tags: ['postgres', 'database', 'schema', 'optimization', 'data'],
    security_score: 78,
    validation_score: 94,
    downloads: 6230,
    permissions: [
      { tool: 'database.schema.read', risk: 'medium', description: 'Read schema metadata' },
      { tool: 'database.query.run', risk: 'high', description: 'Execute EXPLAIN queries' },
      { tool: 'database.metrics.read', risk: 'low', description: 'Read performance metrics' },
      { tool: 'filesystem.read', risk: 'low', description: 'Read migration files' },
    ],
    install_command: 'skillforge install postgres-schema-explorer',
    repository: 'https://github.com/skillforge-data/postgres-schema-explorer',
    created_at: '2026-01-10T16:00:00Z',
    updated_at: '2026-05-18T11:45:00Z',
    category: 'Databases',
    license: 'MIT',
    homepage: 'https://skillforge.dev/skills/postgres-schema-explorer',
  },
];

export async function fetchSkills(params?: {
  search?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}): Promise<SkillsResponse> {
  try {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.set('search', params.search);
    if (params?.tags?.length) searchParams.set('tags', params.tags.join(','));
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.limit) searchParams.set('limit', String(params.limit));

    const url = `${API_BASE}/api/v1/skills?${searchParams.toString()}`;
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    // Fallback to mock data with filtering
    let filtered = [...MOCK_SKILLS];
    if (params?.search) {
      const q = params.search.toLowerCase();
      filtered = filtered.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.tags.some((t) => t.toLowerCase().includes(q))
      );
    }
    if (params?.tags?.length) {
      filtered = filtered.filter((s) =>
        params.tags!.some((t) => s.tags.includes(t))
      );
    }
    return {
      skills: filtered,
      total: filtered.length,
      page: params?.page || 1,
      limit: params?.limit || 20,
    };
  }
}

export async function fetchSkill(name: string): Promise<SkillResponse | null> {
  try {
    const url = `${API_BASE}/api/v1/skills/${encodeURIComponent(name)}`;
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    const skill = MOCK_SKILLS.find((s) => s.name === name);
    if (!skill) return null;
    return { skill };
  }
}

export async function fetchAllTags(): Promise<string[]> {
  try {
    const url = `${API_BASE}/api/v1/tags`;
    const res = await fetch(url, { next: { revalidate: 300 } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch {
    // Extract unique tags from mock skills
    const tagSet = new Set<string>();
    MOCK_SKILLS.forEach((s) => s.tags.forEach((t) => tagSet.add(t)));
    return Array.from(tagSet).sort();
  }
}
