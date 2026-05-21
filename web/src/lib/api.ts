// SkillForge API client — talks to the real Railway backend

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://skillforge-production-9dba.up.railway.app'
    : 'http://localhost:8000');

// — Types matching the real SkillForge API responses —

interface ApiSkillPermissionTool {
  name: string;
  description: string;
  risk: 'low' | 'medium' | 'high' | 'critical';
  data_access?: unknown[];
}

interface ApiSkillManifest {
  name: string;
  version: string;
  description: string;
  author: string;
  license: string;
  mcp_server?: string;
  permissions?: { tools?: ApiSkillPermissionTool[] };
  security?: {
    prompt_injection_surface?: string;
    secrets_required?: string[];
    network_egress?: string[];
  };
  tags?: string[];
  homepage?: string | null;
  repository?: string | null;
  icon?: string | null;
}

interface ApiSkill {
  id: number;
  name: string;
  version: string;
  description: string;
  author: string;
  tags: string[];
  manifest: ApiSkillManifest;
  body?: string;
  download_count: number;
  validation_score: number | null;
  security_score: number | null;
  created_at: string;
  updated_at: string;
}

interface ApiSkillsListResponse {
  items: ApiSkill[];
  total: number;
  page: number;
  page_size: number;
}

// — Cleaned-up types for the frontend —

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

// — Transform helpers —

function mapApiSkill(api: ApiSkill): Skill {
  const perms: SkillPermission[] =
    api.manifest?.permissions?.tools?.map((t) => ({
      tool: t.name,
      risk: t.risk,
      description: t.description,
    })) ?? [];

  return {
    name: api.name,
    version: api.version,
    author: api.author,
    description: api.description,
    tags: api.tags ?? [],
    security_score: Math.round((api.security_score ?? 0) * 100),
    validation_score: Math.round((api.validation_score ?? 0) * 100),
    downloads: api.download_count ?? 0,
    permissions: perms,
    install_command: `skillforge install ${api.name}`,
    repository: api.manifest?.repository ?? undefined,
    created_at: api.created_at,
    updated_at: api.updated_at,
    category: api.tags?.[0] ?? undefined,
    license: api.manifest?.license,
    homepage: api.manifest?.homepage ?? undefined,
  };
}

// — API functions —

export async function fetchSkills(params?: {
  search?: string;
  tags?: string[];
  page?: number;
  limit?: number;
}): Promise<SkillsResponse> {
  try {
    let url: string;
    if (params?.search) {
      url = `${API_BASE}/search?q=${encodeURIComponent(params.search)}&page=${params.page ?? 1}&page_size=${params.limit ?? 20}`;
    } else {
      url = `${API_BASE}/skills?page=${params.page ?? 1}&page_size=${params.limit ?? 20}`;
      if (params?.tags?.length) {
        url += `&tag=${encodeURIComponent(params.tags[0])}`;
      }
    }

    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data: ApiSkillsListResponse = await res.json();

    return {
      skills: data.items.map(mapApiSkill),
      total: data.total,
      page: data.page,
      limit: data.page_size,
    };
  } catch (err) {
    console.warn('SkillForge API unreachable, using empty result:', err);
    return { skills: [], total: 0, page: 1, limit: 20 };
  }
}

export async function fetchSkill(name: string): Promise<SkillResponse | null> {
  try {
    // Search the API by name (API uses numeric IDs, not name-based routes)
    const url = `${API_BASE}/search?q=${encodeURIComponent(name)}&page_size=100`;
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data: ApiSkillsListResponse = await res.json();

    const match = data.items.find(
      (s) => s.name.toLowerCase() === name.toLowerCase()
    );
    if (!match) return null;

    return { skill: mapApiSkill(match) };
  } catch {
    return null;
  }
}

export async function fetchAllTags(): Promise<string[]> {
  try {
    // Fetch all skills and extract unique tags
    const url = `${API_BASE}/skills?page_size=100`;
    const res = await fetch(url, { next: { revalidate: 300 } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data: ApiSkillsListResponse = await res.json();

    const tagSet = new Set<string>();
    data.items.forEach((s) => s.tags?.forEach((t) => tagSet.add(t)));
    return Array.from(tagSet).sort();
  } catch {
    return [];
  }
}
