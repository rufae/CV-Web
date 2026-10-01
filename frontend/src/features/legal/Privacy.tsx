import { ShieldCheck } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { Card } from '@/shared/ui/card';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';

const CONTACT_EMAIL = 'rafaelcastanoblanca1805@gmail.com';

export function Privacy() {
  const { t } = useI18n();

  return (
    <Section id="privacy" width="narrow">
      <Reveal>
        <SectionHeader eyebrow={t.privacy.title} title={t.privacy.title} lead={t.privacy.intro} />
      </Reveal>

      <div className="grid gap-6 md:grid-cols-2">
        {t.privacy.blocks.map((block, index) => (
          <Reveal key={block.title} delay={Math.min(index, 3) * 0.06}>
            <Card className="h-full p-6">
              <h3 className="flex items-center gap-2 text-base font-semibold">
                <ShieldCheck className="h-4 w-4 text-accent-strong" aria-hidden="true" />
                {block.title}
              </h3>
              <p className="mt-3 text-sm text-muted-foreground">{block.text}</p>
            </Card>
          </Reveal>
        ))}
      </div>

      <Reveal delay={0.12}>
        <p className="mt-6 rounded-xl border border-border bg-surface-subtle p-4 text-sm text-muted-foreground">
          {t.privacy.noThirdParties}
        </p>
      </Reveal>

      <p className="mt-8 text-sm text-muted-foreground">
        <span className="font-medium text-foreground">{t.privacy.rightsTitle}:</span>{' '}
        {t.privacy.rightsText}{' '}
        <a href={`mailto:${CONTACT_EMAIL}`} className="text-accent-strong underline">
          {CONTACT_EMAIL}
        </a>
      </p>
    </Section>
  );
}
