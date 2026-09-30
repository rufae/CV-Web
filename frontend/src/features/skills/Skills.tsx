import React from 'react';
import { motion } from 'framer-motion';
import { useI18n } from '@/shared/lib/i18n';

import { FACTS } from '@/content/facts';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
import { Progress } from '@/shared/ui/progress';
import { Server, Brain, Settings, Layout, Download } from 'lucide-react';
import { Button } from '@/shared/ui/button';

const CATEGORY_STYLES = [
  { icon: <Layout className="w-5 h-5" />, color: 'text-blue-500' },
  { icon: <Server className="w-5 h-5" />, color: 'text-green-500' },
  { icon: <Settings className="w-5 h-5" />, color: 'text-purple-500' },
  { icon: <Brain className="w-5 h-5" />, color: 'text-orange-500' },
];

const SKILL_EMOJI: Record<string, string> = {
  React: '⚛️',
  Angular: '🅰️',
  'HTML/CSS': '🌐',
  JavaScript: '🟨',
  TypeScript: '🔷',
  'Tailwind CSS': '💨',
  Java: '☕',
  'Spring Boot': '🍃',
  'Node.js': '🟢',
  Python: '🐍',
  'REST APIs': '🔗',
  MySQL: '🗄️',
  Git: '📝',
  Docker: '🐳',
  Networking: '🌐',
  Linux: '🐧',
  AWS: '☁️',
  Figma: '🎨',
  'Artificial Intelligence': '🤖',
  'Machine Learning': '📊',
  'React Native': '📱',
  GraphQL: '📈',
  Kubernetes: '⚙️',
  TensorFlow: '🧠',
};

export const Skills: React.FC = () => {
  const { t } = useI18n();
  const skillCategories = FACTS.skills.map((category, index) => ({
    id: index + 1,
    title: category.title,
    icon: CATEGORY_STYLES[index]?.icon ?? <Layout className="w-5 h-5" />,
    color: CATEGORY_STYLES[index]?.color ?? 'text-accent',
    skills: category.skills.map((skill) => ({
      name: skill.name,
      level: skill.level,
      icon: SKILL_EMOJI[skill.name] ?? '',
    })),
  }));

  const getSkillLevelColor = (level: number) => {
    if (level >= 90) return 'bg-green-500';
    if (level >= 80) return 'bg-blue-500';
    if (level >= 70) return 'bg-yellow-500';
    if (level >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getSkillLevelText = (level: number) => {
    if (level >= 90) return t.skills.levels.expert;
    if (level >= 80) return t.skills.levels.advanced;
    if (level >= 70) return t.skills.levels.intermediate;
    if (level >= 60) return t.skills.levels.learning;
    return t.skills.levels.beginner;
  };

  return (
    <section id="skills" className="py-20 px-6 bg-muted/20">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-4">{t.skills.title}</h2>
          <div className="w-20 h-1 bg-accent mx-auto rounded-full" />
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            Mis competencias técnicas organizadas por categoría, desde desarrollo frontend y backend
            hasta tecnologías emergentes y herramientas especializadas.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {skillCategories.map((category, categoryIndex) => (
            <motion.div
              key={category.id}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: categoryIndex * 0.1 }}
            >
              <Card className="h-full hover:shadow-lg transition-all duration-300">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-accent/10 ${category.color}`}>
                      {category.icon}
                    </div>
                    {category.title}
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <div className="space-y-6">
                    {category.skills.map((skill, skillIndex) => (
                      <motion.div
                        key={skill.name}
                        className="space-y-2"
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: skillIndex * 0.05 }}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{skill.icon}</span>
                            <span className="font-medium">{skill.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant="outline"
                              className={`text-xs ${getSkillLevelColor(skill.level).replace('bg-', 'border-')}`}
                            >
                              {getSkillLevelText(skill.level)}
                            </Badge>
                            <span className="text-sm text-muted-foreground">{skill.level}%</span>
                          </div>
                        </div>

                        <div className="relative">
                          <Progress value={0} className="h-2" />
                          <motion.div
                            className={`absolute top-0 left-0 h-2 rounded-full ${getSkillLevelColor(skill.level)}`}
                            initial={{ width: 0 }}
                            whileInView={{ width: `${skill.level}%` }}
                            viewport={{ once: true }}
                            transition={{ duration: 1, delay: skillIndex * 0.1, ease: 'easeOut' }}
                          />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Additional Skills Summary */}
        <motion.div
          className="mt-12"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-center">{t.skills.overviewTitle}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div className="space-y-2">
                  <div className="text-2xl">15+</div>
                  <div className="text-sm text-muted-foreground">{t.skills.technologies}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">8+</div>
                  <div className="text-sm text-muted-foreground">{t.skills.expertLevel}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">3+</div>
                  <div className="text-sm text-muted-foreground">{t.skills.learningAi}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">24/7</div>
                  <div className="text-sm text-muted-foreground">{t.skills.alwaysLearning}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* CV Download Section */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Card className="inline-block p-8">
            <div className="space-y-4">
              <div className="text-6xl">📄</div>
              <h3>{t.skills.downloadTitle}</h3>
              <p className="text-muted-foreground max-w-md">
                Get a detailed overview of my experience, education, and technical skills in PDF
                format.
              </p>
              <Button
                size="lg"
                variant="outline"
                className="border-accent text-accent hover:bg-accent hover:text-accent-foreground min-w-[200px]"
                asChild
              >
                <a href="/curriculum-vitae.pdf" download="Rafael_CV.pdf">
                  <Download className="w-4 h-4 mr-2" />
                  {t.skills.download}
                </a>
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};
