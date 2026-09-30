import type { Lang } from './types';

export type { Lang };

export interface Dictionary {
  nav: {
    home: string;
    about: string;
    experience: string;
    projects: string;
    skills: string;
    contact: string;
    lab: string;
  };
  hero: {
    greeting: string;
    passion: string;
    subtitle: string;
    viewProjects: string;
    downloadCv: string;
    contact: string;
  };
  about: {
    title: string;
    role: string;
    funFactsTitle: string;
    facts: [string, string, string, string, string, string];
    yearsLearning: string;
    projectsBuilt: string;
    technologies: string;
  };
  experience: {
    title: string;
    responsibilities: string;
    technologies: string;
    current: string;
  };
  projects: {
    title: string;
    subtitle: string;
    stackTitle: string;
    viewGithub: string;
    liveDemo: string;
    viewMore: string;
  };
  skills: {
    title: string;
    subtitle: string;
    overviewTitle: string;
    technologies: string;
    expertLevel: string;
    learningAi: string;
    alwaysLearning: string;
    downloadTitle: string;
    downloadText: string;
    download: string;
    levels: {
      expert: string;
      advanced: string;
      intermediate: string;
      learning: string;
      beginner: string;
    };
  };
  contact: {
    title: string;
    subtitle: string;
    formTitle: string;
    name: string;
    namePlaceholder: string;
    email: string;
    emailPlaceholder: string;
    message: string;
    messagePlaceholder: string;
    send: string;
    sending: string;
    infoTitle: string;
    locationLabel: string;
    locationValue: string;
    socialTitle: string;
    availableTitle: string;
    availableText: string;
    sent: string;
  };
  footer: {
    tagline: string;
    quickLinks: string;
    follow: string;
    rights: string;
    madeWith: string;
    alwaysEvolving: string;
    builtWith: string;
  };
  aiLab: {
    title: string;
    subtitle: string;
    statusTitle: string;
    online: string;
    degraded: string;
    offline: string;
    metricsTitle: string;
    recall: string;
    refusal: string;
    leaks: string;
    model: string;
    privacyTitle: string;
    privacyText: string;
    linksTitle: string;
    repo: string;
    evaluation: string;
    diagramAlt: string;
  };
  chat: {
    title: string;
    disclaimer: string;
    starters: [string, string, string, string];
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
  };
}
