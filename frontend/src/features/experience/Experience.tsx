import { Building2, MapPin } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { Badge } from '@/shared/ui/badge';
import { Card } from '@/shared/ui/card';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

export function Experience() {
  const { t } = useI18n();

  return (
    <Section id="experience" width="narrow">
      <Reveal>
        <SectionHeader eyebrow={t.experience.eyebrow} title={t.experience.title} />
      </Reveal>

      <Reveal>
        <div className="mb-8 flex flex-wrap items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-lg bg-accent-soft text-accent-strong">
            <Building2 className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <p className="text-lg font-semibold leading-tight">{t.experience.company}</p>
            <p className="flex items-center gap-1.5 text-sm text-muted-foreground">
              <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
              {t.experience.location}
            </p>
          </div>
        </div>
      </Reveal>

      <div className="relative">
        <div
          aria-hidden="true"
          className="absolute bottom-0 left-[5px] top-0 w-px bg-border md:left-[5px]"
        />

        <ol className="space-y-8">
          {t.experience.roles.map((role, index) => (
            <li key={role.title} className="relative pl-8">
              <span
                aria-hidden="true"
                className="absolute left-0 top-1.5 h-3 w-3 rounded-full bg-accent ring-4 ring-background"
              />
              <Reveal delay={Math.min(index, 3) * 0.06}>
                <Card className="p-6">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="text-xl font-semibold">{role.title}</h3>
                    <Badge variant="secondary">{role.tag}</Badge>
                  </div>
                  <p className="mono-label mt-2 text-muted-foreground">{role.period}</p>
                  <p className="mt-3 text-muted-foreground">{role.summary}</p>

                  <ul className="mt-4 space-y-1.5">
                    {role.bullets.map((bullet) => (
                      <li
                        key={bullet}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <span
                          className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                          aria-hidden="true"
                        />
                        {bullet}
                      </li>
                    ))}
                  </ul>

                  <ul className="mt-4 flex flex-wrap gap-2">
                    {role.stack.map((tech) => (
                      <li key={tech}>
                        <Badge variant="outline">{tech}</Badge>
                      </li>
                    ))}
                  </ul>
                </Card>
              </Reveal>
            </li>
          ))}
        </ol>
      </div>
    </Section>
  );
}
