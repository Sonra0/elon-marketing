const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export function getJwt(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("elon_jwt");
}

export function setJwt(jwt: string) {
  window.localStorage.setItem("elon_jwt", jwt);
}

export function clearJwt() {
  window.localStorage.removeItem("elon_jwt");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const jwt = getJwt();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined),
  };
  if (jwt) headers["Authorization"] = `Bearer ${jwt}`;
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export type CreateTenantOut = {
  tenant_id: string; user_id: string; jwt: string;
  telegram_link_token: string; telegram_link_command: string;
};

export async function createTenant(name: string): Promise<CreateTenantOut> {
  const res = await fetch(`${BASE}/tenants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}: ${await res.text()}`);
  return res.json();
}

export function oauthStartUrl(provider: "meta" | "tiktok"): string {
  const jwt = getJwt();
  return `${BASE}/oauth/${provider}/start?token=${encodeURIComponent(jwt || "")}`;
}

export function apiBase(): string {
  return BASE;
}

export const api = {
  me: () => request<{ user_id: string; tenant_id: string; role: string;
                       telegram_linked: boolean; whatsapp_linked: boolean }>("/tenants/me"),
  spend: () => request<{ tenant_id: string; period_usd: number; budget_usd: number; pct_of_budget: number }>("/admin/spend"),
  connectors: () => request<Array<{ platform: string; handle: string | null; status: string }>>("/admin/connectors"),
  posts: (state?: string) => request<Array<Post>>(`/posts${state ? `?state=${state}` : ""}`),
  decide: (id: string, decision: "approve" | "reject", notes?: string) =>
    request<Post>(`/posts/${id}/decide`, { method: "POST", body: JSON.stringify({ decision, notes }) }),
  brand: () => request<Brand | null>("/posts/_brand"),
  draft: (instructions: string, platform?: string) =>
    request<{ task_id: string }>(`/agent/draft`, {
      method: "POST", body: JSON.stringify({ instructions, platform }),
    }),
  ingest: (website_url?: string, notes?: string) =>
    request<{ task_id: string }>(`/agent/ingest`, {
      method: "POST", body: JSON.stringify({ website_url, notes }),
    }),
};

export type Post = {
  id: string; platform: string; state: string;
  idea: string; hook: string; caption: string; cta: string;
  score_json: { impact?: number; effort?: number; risk?: number };
  requires_human_review: boolean;
  scheduled_at: string | null; published_at: string | null;
  external_post_id: string | null; created_at: string;
};

export type Brand = {
  version: number;
  voice_json: any; visual_json: any; offering_json: any;
  audience_json: any; positioning_json: any;
  pillars_json: Array<{ id: string; name: string; description: string; weight?: number }>;
  forbidden_json: any;
};
