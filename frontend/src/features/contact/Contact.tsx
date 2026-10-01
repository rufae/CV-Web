import { useState } from 'react';
import { Check, Copy, Github, Linkedin, Mail, Send } from 'lucide-react';
import { toast } from 'sonner';

import { ApiError, sendContactForm } from '@/shared/api/client';
import { useI18n } from '@/shared/lib/i18n';
import { Badge } from '@/shared/ui/badge';
import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { Input } from '@/shared/ui/input';
import { Label } from '@/shared/ui/label';
import { Reveal } from '@/shared/ui/reveal';
import { Section, SectionHeader } from '@/shared/ui/section';
import { StatusPill } from '@/shared/ui/status-pill';
import { Textarea } from '@/shared/ui/textarea';

import { validateForm, type ValidationError } from './validation';

const EMAIL = 'rafaelcastanoblanca1805@gmail.com';
const MAX_MESSAGE = 2000;

export function Contact() {
  const { t } = useI18n();
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [honeypot, setHoneypot] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const error: ValidationError | null = validateForm(formData);
    if (error !== null) {
      const messages: Record<ValidationError, string> = {
        name: t.contact.validationName,
        email: t.contact.validationEmail,
        message: t.contact.validationMessage,
      };
      toast.error(messages[error]);
      return;
    }

    setIsSubmitting(true);

    try {
      await sendContactForm({ ...formData, honeypot });
      toast.success(t.contact.sent);
      setFormData({ name: '', email: '', message: '' });
      setHoneypot('');
    } catch (err) {
      if (err instanceof ApiError && err.code === 'rate_limited') {
        toast.error(t.contact.rateLimited.replace('{seconds}', String(err.retryAfter ?? 0)));
      } else if (err instanceof ApiError && err.code === 'daily_budget_exhausted') {
        toast.error(t.contact.dailyBudget);
      } else {
        toast.error(t.contact.error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const copyEmail = async () => {
    try {
      await navigator.clipboard.writeText(EMAIL);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // sin permiso de portapapeles
    }
  };

  return (
    <Section id="contact">
      <Reveal>
        <SectionHeader eyebrow={t.contact.eyebrow} title={t.contact.title} lead={t.contact.lead} />
      </Reveal>

      <div className="grid gap-8 lg:grid-cols-12">
        <Reveal className="lg:col-span-7">
          <Card className="p-6">
            <h3 className="text-xl font-semibold">{t.contact.formTitle}</h3>
            <form onSubmit={handleSubmit} className="mt-6 space-y-5" noValidate>
              <div className="space-y-2">
                <Label htmlFor="name">{t.contact.name}</Label>
                <Input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder={t.contact.namePlaceholder}
                  autoComplete="name"
                  required
                  maxLength={100}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">{t.contact.email}</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder={t.contact.emailPlaceholder}
                  autoComplete="email"
                  required
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="message">{t.contact.message}</Label>
                  <span id="message-counter" className="mono-label text-muted-foreground">
                    {formData.message.length}/{MAX_MESSAGE}
                  </span>
                </div>
                <Textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  placeholder={t.contact.messagePlaceholder}
                  rows={6}
                  required
                  maxLength={MAX_MESSAGE}
                  aria-describedby="message-counter"
                />
              </div>

              <div aria-hidden="true" className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
                <label htmlFor="website">No rellenar este campo</label>
                <input
                  id="website"
                  name="website"
                  type="text"
                  tabIndex={-1}
                  autoComplete="off"
                  value={honeypot}
                  onChange={(event) => setHoneypot(event.target.value)}
                />
              </div>

              <Button type="submit" size="lg" disabled={isSubmitting} className="w-full">
                {isSubmitting ? (
                  <>
                    <span
                      className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
                      aria-hidden="true"
                    />
                    {t.contact.sending}
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    {t.contact.send}
                  </>
                )}
              </Button>
            </form>
          </Card>
        </Reveal>

        <div className="space-y-6 lg:col-span-5">
          <Reveal delay={0.06}>
            <Card className="border-success/30 bg-success/5 p-6">
              <StatusPill tone="success" label={t.contact.availabilityTitle} pulse />
              <p className="mt-3 text-sm text-muted-foreground">{t.contact.availabilityText}</p>
            </Card>
          </Reveal>

          <Reveal delay={0.12}>
            <Card className="p-6">
              <h3 className="text-xl font-semibold">{t.contact.linksTitle}</h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="https://github.com/rufae"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex min-h-11 items-center gap-3 rounded-md border border-border px-3 text-sm font-medium transition-colors hover:border-accent/40 hover:bg-surface-subtle"
                  >
                    <Github className="h-4 w-4" aria-hidden="true" />
                    GitHub
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.linkedin.com/in/rafael-casta%C3%B1o-blanca/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex min-h-11 items-center gap-3 rounded-md border border-border px-3 text-sm font-medium transition-colors hover:border-accent/40 hover:bg-surface-subtle"
                  >
                    <Linkedin className="h-4 w-4" aria-hidden="true" />
                    LinkedIn
                  </a>
                </li>
                <li className="flex items-center gap-2">
                  <span className="flex min-h-11 flex-1 items-center gap-3 rounded-md border border-border px-3 text-sm">
                    <Mail className="h-4 w-4 shrink-0" aria-hidden="true" />
                    <span className="truncate">Email</span>
                  </span>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => void copyEmail()}
                    aria-label={t.contact.copyEmail}
                  >
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    {copied ? t.common.copied : t.common.copy}
                  </Button>
                </li>
              </ul>
              <p aria-live="polite" className="sr-only">
                {copied ? t.common.copied : ''}
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                <Badge variant="secondary">GitHub · rufae</Badge>
                <Badge variant="secondary">LinkedIn · Rafael Castaño</Badge>
              </div>
            </Card>
          </Reveal>
        </div>
      </div>
    </Section>
  );
}
