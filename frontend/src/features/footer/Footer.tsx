import { ArrowUp, Check, Github, Linkedin, Mail } from 'lucide-react';
import { useState } from 'react';

import { useI18n } from '@/shared/lib/i18n';
import { Button } from '@/shared/ui/button';

const EMAIL = 'rafaelcastanoblanca1805@gmail.com';

export function Footer() {
  const { t } = useI18n();
  const currentYear = new Date().getFullYear();
  const [copied, setCopied] = useState(false);

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(EMAIL);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // sin permiso de portapapeles
    }
  };

  const links = [
    { label: t.header.nav.projects, href: '#projects' },
    { label: t.header.nav.lab, href: '#ai-lab' },
    { label: t.footer.about, href: '#about' },
    { label: t.privacy.title, href: '#privacy' },
  ];

  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto max-w-[1120px] px-5 py-12 md:px-6">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div className="max-w-sm">
            <p className="text-base font-semibold">Rafael Castaño</p>
            <p className="mt-1 text-sm text-muted-foreground">{t.footer.tagline}</p>
          </div>

          <nav aria-label={t.footer.linksTitle}>
            <p className="eyebrow mb-3">{t.footer.linksTitle}</p>
            <ul className="flex flex-wrap gap-x-5 gap-y-2">
              {links.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-muted-foreground transition-colors hover:text-accent-strong"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <p className="eyebrow mb-3">{t.footer.followTitle}</p>
            <div className="flex items-center gap-2">
              <a
                href="https://github.com/rufae"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                className="inline-flex size-10 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:border-accent/40 hover:text-accent-strong"
              >
                <Github className="h-4 w-4" />
              </a>
              <a
                href="https://www.linkedin.com/in/rafael-casta%C3%B1o-blanca/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="LinkedIn"
                className="inline-flex size-10 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:border-accent/40 hover:text-accent-strong"
              >
                <Linkedin className="h-4 w-4" />
              </a>
              <button
                type="button"
                onClick={() => void copyEmail()}
                aria-label={t.contact.copyEmail}
                className="inline-flex size-10 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:border-accent/40 hover:text-accent-strong"
              >
                {copied ? <Check className="h-4 w-4" /> : <Mail className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-4 border-t border-border pt-6 md:flex-row md:items-center md:justify-between">
          <p className="font-mono text-xs text-muted-foreground">
            © {currentYear} Rafael Castaño · {t.footer.builtWith} · {t.footer.selfHosted}
          </p>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
          >
            <ArrowUp className="h-4 w-4" />
            {t.common.backToTop}
          </Button>
        </div>
      </div>
    </footer>
  );
}
