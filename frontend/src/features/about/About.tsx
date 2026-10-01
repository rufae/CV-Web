import { useI18n } from '@/shared/lib/i18n';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

export function About() {
  const { t } = useI18n();

  return (
    <Section id="about" tone="subtle" width="narrow">
      <Reveal>
        <SectionHeader eyebrow={t.about.eyebrow} title={t.about.title} />
      </Reveal>

      <div className="grid items-start gap-8 md:grid-cols-12">
        <Reveal className="md:col-span-4">
          <img
            src="/RAFAEL.png"
            alt={t.about.photoAlt}
            width={160}
            height={160}
            className="h-40 w-40 rounded-xl border border-border object-cover"
          />
        </Reveal>

        <Reveal delay={0.06} className="md:col-span-8">
          <div className="space-y-4 text-lg leading-relaxed text-muted-foreground">
            <p>{t.about.paragraph1}</p>
            <p>{t.about.paragraph2}</p>
          </div>
          <p className="mt-6 text-sm text-muted-foreground">{t.about.finalLine}</p>
        </Reveal>
      </div>
    </Section>
  );
}
