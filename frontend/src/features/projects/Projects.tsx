import { useI18n } from '@/shared/lib/i18n';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

import { CaseStudyCard } from './CaseStudyCard';

export function Projects() {
  const { t } = useI18n();
  const [featured, ...rest] = t.projects.items;

  return (
    <Section id="projects">
      <Reveal>
        <SectionHeader
          eyebrow={t.projects.eyebrow}
          title={t.projects.title}
          lead={t.projects.lead}
        />
      </Reveal>

      <Reveal>
        <CaseStudyCard study={featured} featured />
      </Reveal>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {rest.map((study, index) => (
          <Reveal key={study.id} delay={Math.min(index, 3) * 0.06}>
            <CaseStudyCard study={study} />
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
