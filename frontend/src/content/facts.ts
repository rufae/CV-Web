import raw from './facts.json';

export interface ProfileFact {
  name: string;
  role: string;
  location: string;
  summary: string;
}

export interface ExperienceFact {
  company: string;
  role: string;
  period: string;
  location: string;
  type: string;
  description: string;
  responsibilities: string[];
  technologies: string[];
}

export interface ProjectFact {
  name: string;
  description: string;
  technologies: string[];
  url: string;
  type: string;
}

export interface SkillFact {
  name: string;
  level: number;
}

export interface SkillCategoryFact {
  title: string;
  skills: SkillFact[];
}

export interface Facts {
  generated_at: string;
  profile: ProfileFact;
  experience: ExperienceFact[];
  projects: ProjectFact[];
  skills: SkillCategoryFact[];
  certifications: string[];
  languages: string[];
}

/** Fuente única de verdad: generada desde el vault público (ADR-0004). */
export const FACTS = raw as Facts;
