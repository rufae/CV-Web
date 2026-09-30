/** Tipos compartidos con el contrato de `docs/api.md`. */

export const MAX_MESSAGE_CHARS = 500;

export type Lang = 'es' | 'en';
export type Tier = 'gpu' | 'cpu';

export interface ChatTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  history?: ChatTurn[];
  lang?: Lang;
}

export interface MetaData {
  message_id: string;
  prompt_version: string;
  tier: Tier;
}

export interface SourceItem {
  n: number;
  title: string;
  section: string;
}

export interface SourcesData {
  sources: SourceItem[];
}

export interface TokenData {
  t: string;
}

export type RefusalReason = 'no_context' | 'off_topic' | 'injection';

export interface RefusalData {
  reason: RefusalReason;
  message: string;
}

export interface DoneData {
  first_token_ms: number | null;
  total_ms: number;
}

export type StreamErrorCode =
  | 'rate_limited'
  | 'daily_budget_exhausted'
  | 'provider_unavailable'
  | 'first_token_timeout'
  | 'output_blocked'
  | 'internal';

export interface ErrorData {
  code: StreamErrorCode;
  message: string;
  retry_after_s: number | null;
}

export type ServerEvent =
  | { event: 'meta'; data: MetaData }
  | { event: 'sources'; data: SourcesData }
  | { event: 'token'; data: TokenData }
  | { event: 'refusal'; data: RefusalData }
  | { event: 'done'; data: DoneData }
  | { event: 'error'; data: ErrorData };

export interface ContactPayload {
  name: string;
  email: string;
  message: string;
}

export interface ContactResponse {
  status: string;
}

export interface FeedbackPayload {
  message_id: string;
  rating: 'up' | 'down';
  comment?: string;
  prompt_version?: string;
  sources?: number[];
  tier?: Tier;
  refused?: boolean;
}

export interface ApiStatus {
  llm: 'online' | 'degraded' | 'offline';
  tier: Tier;
}
