import { ShieldCheck } from 'lucide-react';

import { useI18n } from '@/shared/lib/i18n';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';

const CONTACT_EMAIL = 'rafaelcastanoblanca1805@gmail.com';

interface PrivacyContent {
  title: string;
  intro: string;
  aiTitle: string;
  aiText: string;
  dataTitle: string;
  dataText: string;
  retentionTitle: string;
  retentionText: string;
  cookiesTitle: string;
  cookiesText: string;
  rightsTitle: string;
  rightsText: string;
}

const CONTENT: Record<'es' | 'en', PrivacyContent> = {
  es: {
    title: 'Privacidad',
    intro:
      'Esta web es un portfolio personal. No hay cookies de seguimiento ni publicidad, por eso no verás banners de consentimiento.',
    aiTitle: 'Asistente de IA',
    aiText:
      'El asistente solo responde con información pública del portfolio (notas de la carpeta Public con cv_public). No se almacenan tus conversaciones en el servidor. El feedback es anónimo: guarda únicamente la valoración (👍/👎) y metadatos técnicos, nunca la pregunta ni tu IP.',
    dataTitle: 'Formulario de contacto',
    dataText:
      'Si me escribes, trato tu nombre, email y mensaje con la única finalidad de responder a tu consulta. No se usan para marketing ni se ceden a terceros.',
    retentionTitle: 'Conservación',
    retentionText:
      'Los mensajes de contacto se conservan un máximo de 12 meses. El feedback anónimo se conserva para mejorar el asistente. Puedes pedir su supresión escribiendo al email de contacto.',
    cookiesTitle: 'Cookies y analítica',
    cookiesText:
      'No se usan cookies de terceros ni analítica con seguimiento. El tema (claro/oscuro) y tus preferencias se guardan solo en tu navegador.',
    rightsTitle: 'Tus derechos (RGPD)',
    rightsText:
      'Puedes ejercer tus derechos de acceso, rectificación, supresión y oposición escribiendo a',
  },
  en: {
    title: 'Privacy',
    intro:
      'This site is a personal portfolio. There are no tracking cookies or ads, so you will not see consent banners.',
    aiTitle: 'AI assistant',
    aiText:
      'The assistant only answers with public portfolio information (notes in the Public folder with cv_public). Your conversations are not stored on the server. Feedback is anonymous: it only stores the rating (👍/👎) and technical metadata, never the question or your IP.',
    dataTitle: 'Contact form',
    dataText:
      'If you write to me, I process your name, email and message only to reply to your enquiry. They are not used for marketing or shared with third parties.',
    retentionTitle: 'Retention',
    retentionText:
      'Contact messages are kept for a maximum of 12 months. Anonymous feedback is kept to improve the assistant. You can request deletion by emailing the contact address.',
    cookiesTitle: 'Cookies and analytics',
    cookiesText:
      'No third-party cookies or tracking analytics are used. Theme (light/dark) and your preferences are stored only in your browser.',
    rightsTitle: 'Your rights (GDPR)',
    rightsText:
      'You can exercise your rights of access, rectification, erasure and objection by writing to',
  },
};

export function Privacy() {
  const { lang } = useI18n();
  const t = CONTENT[lang];

  return (
    <section id="privacy" className="px-6 py-20">
      <div className="mx-auto max-w-4xl">
        <div className="mb-12 text-center">
          <h2 className="mb-4">{t.title}</h2>
          <div className="mx-auto h-1 w-20 rounded-full bg-accent" />
          <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">{t.intro}</p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {[t.aiTitle, t.dataTitle, t.retentionTitle, t.cookiesTitle].map((title, index) => (
            <Card key={title}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <ShieldCheck className="h-4 w-4 text-accent" />
                  {title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {[t.aiText, t.dataText, t.retentionText, t.cookiesText][index]}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        <p className="mt-8 text-center text-sm text-muted-foreground">
          <span className="font-medium text-foreground">{t.rightsTitle}:</span> {t.rightsText}{' '}
          <a href={`mailto:${CONTACT_EMAIL}`} className="text-accent underline">
            {CONTACT_EMAIL}
          </a>
        </p>
      </div>
    </section>
  );
}
