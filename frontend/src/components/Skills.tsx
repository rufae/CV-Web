import React from 'react';
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Server, Brain, Settings, Layout, Download
} from 'lucide-react';
import { Button } from './ui/button';

export const Skills: React.FC = () => {
  const skillCategories = [
    {
      id: 1,
      title: "Frontend Development",
      icon: <Layout className="w-5 h-5" />,
      color: "text-blue-500",
      skills: [
        { name: "React", level: 90, icon: "⚛️" },
        { name: "Angular", level: 85, icon: "🅰️" },
        { name: "HTML/CSS", level: 95, icon: "🌐" },
        { name: "JavaScript", level: 90, icon: "🟨" },
        { name: "TypeScript", level: 85, icon: "🔷" },
        { name: "Tailwind CSS", level: 90, icon: "💨" }
      ]
    },
    {
      id: 2,
      title: "Backend Development",
      icon: <Server className="w-5 h-5" />,
      color: "text-green-500",
      skills: [
        { name: "Java", level: 90, icon: "☕" },
        { name: "Spring Boot", level: 85, icon: "🍃" },
        { name: "Node.js", level: 80, icon: "🟢" },
        { name: "Python", level: 75, icon: "🐍" },
        { name: "REST APIs", level: 90, icon: "🔗" },
        { name: "MySQL", level: 80, icon: "🗄️" }
      ]
    },
    {
      id: 3,
      title: "Tools & Technologies",
      icon: <Settings className="w-5 h-5" />,
      color: "text-purple-500",
      skills: [
        { name: "Git", level: 90, icon: "📝" },
        { name: "Docker", level: 70, icon: "🐳" },
        { name: "Networking", level: 75, icon: "🌐" },
        { name: "Linux", level: 70, icon: "🐧" },
        { name: "AWS", level: 60, icon: "☁️" },
        { name: "Figma", level: 75, icon: "🎨" }
      ]
    },
    {
      id: 4,
      title: "Learning & Emerging",
      icon: <Brain className="w-5 h-5" />,
      color: "text-orange-500",
      skills: [
        { name: "Artificial Intelligence", level: 60, icon: "🤖" },
        { name: "Machine Learning", level: 55, icon: "📊" },
        { name: "React Native", level: 70, icon: "📱" },
        { name: "GraphQL", level: 50, icon: "📈" },
        { name: "Kubernetes", level: 40, icon: "⚙️" },
        { name: "TensorFlow", level: 45, icon: "🧠" }
      ]
    }
  ];

  const getSkillLevelColor = (level: number) => {
    if (level >= 90) return "bg-green-500";
    if (level >= 80) return "bg-blue-500";
    if (level >= 70) return "bg-yellow-500";
    if (level >= 60) return "bg-orange-500";
    return "bg-red-500";
  };

  const getSkillLevelText = (level: number) => {
    if (level >= 90) return "Expert";
    if (level >= 80) return "Advanced";
    if (level >= 70) return "Intermediate";
    if (level >= 60) return "Learning";
    return "Beginner";
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
          <h2 className="mb-4">Habilidades</h2>
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
                          <Progress 
                            value={0} 
                            className="h-2"
                          />
                          <motion.div
                            className={`absolute top-0 left-0 h-2 rounded-full ${getSkillLevelColor(skill.level)}`}
                            initial={{ width: 0 }}
                            whileInView={{ width: `${skill.level}%` }}
                            viewport={{ once: true }}
                            transition={{ duration: 1, delay: skillIndex * 0.1, ease: "easeOut" }}
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
              <CardTitle className="text-center">Skills Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div className="space-y-2">
                  <div className="text-2xl">15+</div>
                  <div className="text-sm text-muted-foreground">Technologies</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">8+</div>
                  <div className="text-sm text-muted-foreground">Expert Level</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">3+</div>
                  <div className="text-sm text-muted-foreground">Learning AI/ML</div>
                </div>
                <div className="space-y-2">
                  <div className="text-2xl">24/7</div>
                  <div className="text-sm text-muted-foreground">Always Learning</div>
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
              <h3>Download My CV</h3>
              <p className="text-muted-foreground max-w-md">
                Get a detailed overview of my experience, education, and technical skills in PDF format.
              </p>
              <Button
                size="lg"
                variant="outline"
                className="border-accent text-accent hover:bg-accent hover:text-accent-foreground min-w-[200px]"
                asChild
              >
                <a href="/Curriculum vitae.pdf" download="Rafael_CV.pdf">
                  <Download className="w-4 h-4 mr-2" />
                  Download CV
                </a>
              </Button>

            </div>
          </Card>
        </motion.div>
      </div>
    </section>
  );
};