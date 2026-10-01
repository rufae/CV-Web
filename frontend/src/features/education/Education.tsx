import { BookOpen, GraduationCap, Languages, ScrollText } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { Badge } from '@/shared/ui/badge';
import { Card } from '@/shared/ui/card';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

export function Education() {
  const { t } = useI18n();
  const education = t.education;

  return (
    <Section id="education" tone="subtle">
      <Reveal>
        <SectionHeader eyebrow={education.eyebrow} title={education.title} lead={education.lead} />
      </Reveal>

      <Reveal>
        <Card className="p-6 hover:border-accent/40 lg:p-8">
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{education.masterTag}</Badge>
            <span className="mono-label text-muted-foreground">{education.masterPeriod}</span>
          </div>
          <h3 className="mt-3 text-2xl font-bold leading-tight">{education.masterTitle}</h3>
          <p className="mt-1 text-muted-foreground">{education.masterCenter}</p>

          <div className="mt-6">
            <p className="eyebrow mb-2 flex items-center gap-2">
              <ScrollText className="h-4 w-4" aria-hidden="true" />
              {education.tfmTitle}
            </p>
            <p className="max-w-[80ch] text-sm text-muted-foreground">{education.tfmText}</p>
          </div>

          <div className="mt-8">
            <p className="eyebrow mb-3">{education.subjectsTitle}</p>
            <dl className="gap-x-8 md:columns-2">
              {education.subjects.map((subject) => (
                <div key={subject.name} className="mb-3 break-inside-avoid">
                  <dt className="text-sm font-medium text-foreground">{subject.name}</dt>
                  <dd className="text-sm text-muted-foreground">{subject.detail}</dd>
                </div>
              ))}
            </dl>
          </div>

          <div className="mt-8">
            <p className="eyebrow mb-1">{education.theoryTitle}</p>
            <p className="mb-3 text-sm text-muted-foreground">{education.theoryIntro}</p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[480px] border-collapse text-left text-sm">
                <caption className="sr-only">{education.theoryTitle}</caption>
                <thead>
                  <tr className="border-b border-border">
                    <th scope="col" className="py-2 pr-6 font-medium text-muted-foreground">
                      {education.theoryConcept}
                    </th>
                    <th scope="col" className="py-2 font-medium text-muted-foreground">
                      {education.theoryApplication}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {education.theory.map((row) => (
                    <tr key={row.concept} className="border-b border-border last:border-0">
                      <th scope="row" className="py-3 pr-6 font-normal text-foreground">
                        {row.concept}
                      </th>
                      <td className="py-3 text-muted-foreground">
                        <a href={row.href} className="text-accent-strong hover:underline">
                          {row.application}
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </Reveal>

      <div className="mt-6 grid gap-6 md:grid-cols-3">
        <Reveal>
          <Card className="h-full p-6">
            <h3 className="flex items-center gap-2 text-base font-semibold">
              <GraduationCap className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {education.cfgsTitle}
            </h3>
            <p className="mono-label mt-3 text-muted-foreground">{education.cfgsCenter}</p>
            <p className="mt-2 text-sm text-muted-foreground">{education.cfgsText}</p>
          </Card>
        </Reveal>

        <Reveal delay={0.06}>
          <Card className="h-full p-6">
            <h3 className="flex items-center gap-2 text-base font-semibold">
              <BookOpen className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {education.certificationsTitle}
            </h3>
            <ul className="mt-3 space-y-2">
              {education.certifications.map((certification) => (
                <li
                  key={certification}
                  className="flex items-start gap-2 text-sm text-muted-foreground"
                >
                  <span
                    className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-accent"
                    aria-hidden="true"
                  />
                  {certification}
                </li>
              ))}
            </ul>
          </Card>
        </Reveal>

        <Reveal delay={0.12}>
          <Card className="h-full p-6">
            <h3 className="flex items-center gap-2 text-base font-semibold">
              <Languages className="h-5 w-5 text-accent-strong" aria-hidden="true" />
              {education.languagesTitle}
            </h3>
            <ul className="mt-3 flex flex-wrap gap-2">
              {education.languages.map((language) => (
                <li key={language}>
                  <Badge variant="outline">{language}</Badge>
                </li>
              ))}
            </ul>
          </Card>
        </Reveal>
      </div>
    </Section>
  );
}
