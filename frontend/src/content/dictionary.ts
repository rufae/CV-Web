import type { Lang } from './types';

export type { Lang };

export interface MetricDef {
  label: string;
  note: string;
}

export interface CaseResult {
  value: string;
  label: string;
  source?: string;
}

export interface CaseStudy {
  id: string;
  type: string;
  title: string;
  problem: string;
  built: string[];
  results: CaseResult[];
  decisions: string[];
  learnings: string[];
  stack: string[];
  repo?: string;
  demo?: string;
  diagram: 'rag' | 'twin' | 'pyme' | 'agents';
  /** Pregunta sugerida para el asistente (CTA en la tarjeta). */
  ask?: string;
  featured?: boolean;
  pending?: boolean;
}

export interface StackGroup {
  title: string;
  daily: string[];
  projects: string[];
}

export interface NowSection {
  title: string;
  workingTitle: string;
  working: { name: string; detail: string }[];
  learningTitle: string;
  learning: string[];
  improving: string;
}

export interface TheoryRow {
  concept: string;
  application: string;
  href: string;
}

export interface SubjectRow {
  name: string;
  detail: string;
}

export interface ExperienceRole {
  title: string;
  period: string;
  tag: string;
  summary: string;
  bullets: string[];
  stack: string[];
}

export interface Dictionary {
  common: {
    skipToContent: string;
    backToTop: string;
    copy: string;
    copied: string;
    downloadCv: string;
    viewProjects: string;
    contact: string;
    pending: string;
    externalLink: string;
    source: string;
    openCase: string;
    closeCase: string;
  };
  header: {
    role: string;
    openMenu: string;
    closeMenu: string;
    menu: string;
    about: string;
    themeToDark: string;
    themeToLight: string;
    language: string;
    nav: {
      projects: string;
      lab: string;
      experience: string;
      education: string;
      stack: string;
      contact: string;
    };
  };
  hero: {
    status: string;
    location: string;
    titleBefore: string;
    titleAccent: string;
    titleAfter: string;
    lead: string;
    ctaTalk: string;
    ctaProjects: string;
    ctaCv: string;
    stackLabel: string;
    consoleTitle: string;
    consoleDisclaimer: string;
    challengeLink: string;
    metricsLabel: string;
  };
  metrics: {
    recall: string;
    refusal: string;
    leaks: string;
    latency: string;
    latencyNote: string;
    dataset: string;
    methodology: string;
    injection: string;
  };
  projects: {
    eyebrow: string;
    title: string;
    lead: string;
    problemLabel: string;
    builtLabel: string;
    resultsLabel: string;
    decisionsLabel: string;
    learningsLabel: string;
    stackLabel: string;
    repo: string;
    demo: string;
    askAssistant: string;
    synthetic: string;
    items: CaseStudy[];
  };
  aiLab: {
    eyebrow: string;
    title: string;
    lead: string;
    architectureTitle: string;
    diagramAlt: string;
    steps: [string, string, string, string];
    /** Especificaciones tecnicas de la arquitectura desplegada. */
    specs: string[];
    statusTitle: string;
    online: string;
    degraded: string;
    offline: string;
    tier: string;
    lastChecked: string;
    lastKnown: string;
    checking: string;
    p50: string;
    p95: string;
    noData: string;
    evalTitle: string;
    tableMetric: string;
    tableValue: string;
    tableThreshold: string;
    tableStatus: string;
    pass: string;
    fail: string;
    reportFooter: string;
    methodology: string;
    repo: string;
    guardsTitle: string;
    canSeeTitle: string;
    canSeeText: string;
    wontDoTitle: string;
    wontDoText: string;
    challengeTitle: string;
    challengeText: string;
    challengePrompts: [string, string, string];
  };
  experience: {
    eyebrow: string;
    title: string;
    company: string;
    location: string;
    roles: ExperienceRole[];
  };
  education: {
    eyebrow: string;
    title: string;
    lead: string;
    masterTag: string;
    masterTitle: string;
    masterCenter: string;
    masterPeriod: string;
    subjectsTitle: string;
    subjects: SubjectRow[];
    tfmTitle: string;
    tfmText: string;
    theoryTitle: string;
    theoryIntro: string;
    theoryConcept: string;
    theoryApplication: string;
    theory: TheoryRow[];
    cfgsTitle: string;
    cfgsCenter: string;
    cfgsText: string;
    certificationsTitle: string;
    certifications: string[];
    languagesTitle: string;
    languages: string[];
  };
  stack: {
    eyebrow: string;
    title: string;
    lead: string;
    levels: [string, string];
    evidence: string;
    empty: string;
    groups: StackGroup[];
    now: NowSection;
  };
  about: {
    eyebrow: string;
    title: string;
    paragraph1: string;
    paragraph2: string;
    finalLine: string;
    photoAlt: string;
  };
  contact: {
    eyebrow: string;
    title: string;
    lead: string;
    formTitle: string;
    name: string;
    namePlaceholder: string;
    email: string;
    emailPlaceholder: string;
    message: string;
    messagePlaceholder: string;
    send: string;
    sending: string;
    availabilityTitle: string;
    availabilityText: string;
    linksTitle: string;
    copyEmail: string;
    sent: string;
    validationName: string;
    validationEmail: string;
    validationMessage: string;
    error: string;
    rateLimited: string;
    dailyBudget: string;
  };
  privacy: {
    title: string;
    intro: string;
    blocks: { title: string; text: string }[];
    noThirdParties: string;
    rightsTitle: string;
    rightsText: string;
  };
  footer: {
    tagline: string;
    about: string;
    linksTitle: string;
    followTitle: string;
    builtWith: string;
    selfHosted: string;
  };
  chat: {
    title: string;
    disclaimer: string;
    starters: [string, string, string, string, string];
    startersLabel: string;
    inputPlaceholder: string;
    send: string;
    stop: string;
    copy: string;
    useful: string;
    notUseful: string;
    newConversation: string;
    close: string;
    open: string;
    retry: string;
    limit: string;
    limitRetry: string;
    offline: string;
    degraded: string;
    refused: string;
    contact: string;
    sources: string;
    empty: string;
    teaser: string;
    providerTooltip: string;
    providerGpu: string;
    providerCpu: string;
  };
}
