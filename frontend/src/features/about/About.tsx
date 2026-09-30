import React from 'react';
import { motion } from 'framer-motion';
import { useI18n } from '@/shared/lib/i18n';

import { FACTS } from '@/content/facts';
import { Card, CardContent } from '@/shared/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar';
import { Code2, Gamepad2, Brain, Coffee, Music, Trophy } from 'lucide-react';

export const About: React.FC = () => {
  const { t } = useI18n();
  const funFactStyles = [
    { icon: <Gamepad2 className="w-4 h-4" />, color: 'bg-green-500' },
    { icon: <Brain className="w-4 h-4" />, color: 'bg-accent' },
    { icon: <Coffee className="w-4 h-4" />, color: 'bg-amber-500' },
    { icon: <Music className="w-4 h-4" />, color: 'bg-purple-500' },
    { icon: <Code2 className="w-4 h-4" />, color: 'bg-emerald-500' },
    { icon: <Trophy className="w-4 h-4" />, color: 'bg-orange-500' },
  ];
  const funFacts = funFactStyles.map((style, index) => ({
    ...style,
    text: t.about.facts[index],
  }));

  return (
    <section id="about" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-4">{t.about.title}</h2>
          <div className="w-20 h-1 bg-accent mx-auto rounded-full" />
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Avatar and Basic Info */}
          <motion.div
            className="text-center lg:text-left"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex justify-center lg:justify-start mb-8">
              <motion.div
                className="relative"
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <Avatar className="w-40 h-40 border-4 border-accent/20">
                  <AvatarImage src="/RAFAEL.png" alt="Rafael" />
                  <AvatarFallback className="text-2xl bg-accent text-accent-foreground">
                    RA
                  </AvatarFallback>
                </Avatar>
                <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 border-4 border-background rounded-full" />
              </motion.div>
            </div>

            <motion.div
              className="space-y-4"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <h3 className="text-2xl">Rafael</h3>
              <p className="text-accent">
                {FACTS.profile.role} • {FACTS.profile.location}
              </p>
              <p className="text-muted-foreground leading-relaxed">{FACTS.profile.summary}</p>
            </motion.div>
          </motion.div>

          {/* Fun Facts */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className="p-6">
              <CardContent className="p-0">
                <h4 className="mb-6 text-center">{t.about.funFactsTitle}</h4>
                <div className="grid grid-cols-2 gap-4">
                  {funFacts.map((fact, index) => (
                    <motion.div
                      key={index}
                      className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/10 transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: index * 0.1 }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className={`p-2 rounded-full text-white ${fact.color}`}>{fact.icon}</div>
                      <span className="text-sm font-medium">{fact.text}</span>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Additional Stats */}
            <motion.div
              className="grid grid-cols-3 gap-4 mt-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              <Card className="p-4 text-center hover:shadow-lg transition-shadow">
                <div className="text-2xl mb-2">2+</div>
                <div className="text-sm text-muted-foreground">{t.about.yearsLearning}</div>
              </Card>
              <Card className="p-4 text-center hover:shadow-lg transition-shadow">
                <div className="text-2xl mb-2">10+</div>
                <div className="text-sm text-muted-foreground">{t.about.projectsBuilt}</div>
              </Card>
              <Card className="p-4 text-center hover:shadow-lg transition-shadow">
                <div className="text-2xl mb-2">5+</div>
                <div className="text-sm text-muted-foreground">{t.about.technologies}</div>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
