import React from 'react';
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Building2, Calendar, MapPin, Users, Code, Network } from 'lucide-react';

export const Experience: React.FC = () => {
  const experiences = [
    {
      id: 1,
      title: "Full Stack Developer",
      company: "AePTIC",
      location: "Seville, Spain",
      period: "June 2025 - Present",
      type: "Full-time",
      description: "Desarrollando aplicaciones web/android/ios completas utilizando tecnologías modernas. Trabajando tanto en frontend como backend, implementando APIs RESTful y colaborando en equipos ágiles.",
      responsibilities: [
        "Desarrollo backend/frontend con Django",
        "Desarrollo backend con FastAPI",
        "Implementación de APIs RESTful",
        "Tareas de networking y configuración de servidores",
        "Colaboración en equipos multidisciplinarios",
        "Mantenimiento y optimización de aplicaciones"
      ],
      technologies: ["Python", "Django", "Kotlin", "Dart", "Android Studio", "Flutter", "MySQL", "PostgreSQL", "Git", "Docker"],
      icon: <Building2 className="w-5 h-5" />
    },
    {
      id: 2,
      title: "Mobile App Developer",
      company: "AePTIC",
      location: "Seville, Spain",
      period: "March 2025 - June 2025",
      type: "Internship",
      description: "Prácticas profesionales como parte del programa CFGS DAM. Trabajé en proyectos reales bajo la supervisión de desarrolladores senior, aprendiendo buenas prácticas de desarrollo.",
      responsibilities: [
        "Desarrollo de una aplicación Android funcional y optimizada",
        "Implementación del backend utilizando Node.js y Express",
        "Ejecución de pruebas y depuración para garantizar la calidad de la aplicación",
        "Redacción de documentación técnica del proyecto",
        "Participación activa en la presentación final de la aplicación, destacando por la calidad de mi trabajo"
      ],
      technologies: ["Python", "Django", "Kotlin", "Dart", "Android Studio", "Flutter", "MySQL", "PostgreSQL", "Git"],
      icon: <Code className="w-5 h-5" />
    }
  ];

  return (
    <section id="experience" className="py-20 px-6 bg-muted/20">
      <div className="max-w-4xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-4">Experiencia</h2>
          <div className="w-20 h-1 bg-accent mx-auto rounded-full" />
        </motion.div>

        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-accent/30 hidden md:block" />

          <div className="space-y-12">
            {experiences.map((exp, index) => (
              <motion.div
                key={exp.id}
                className="relative"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
              >
                {/* Timeline Dot */}
                <div className="absolute left-6 w-4 h-4 bg-accent rounded-full border-4 border-background z-10 hidden md:block" />
                
                <div className="md:ml-20">
                  <Card className="hover:shadow-lg transition-all duration-300 group">
                    <CardHeader>
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex items-start space-x-4">
                          <div className="p-2 bg-accent/10 rounded-lg text-accent group-hover:bg-accent group-hover:text-accent-foreground transition-colors">
                            {exp.icon}
                          </div>
                          <div>
                            <CardTitle className="flex items-center gap-2">
                              {exp.title}
                              <Badge variant={exp.type === 'Full-time' ? 'default' : 'secondary'}>
                                {exp.type}
                              </Badge>
                            </CardTitle>
                            <p className="text-accent font-medium">{exp.company}</p>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground mt-2">
                              <div className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {exp.period}
                              </div>
                              <div className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {exp.location}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <p className="text-muted-foreground mb-6">{exp.description}</p>
                      
                      <div className="mb-6">
                        <h5 className="font-medium mb-3 flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          Responsabilidades
                        </h5>
                        <ul className="space-y-2">
                          {exp.responsibilities.map((resp, idx) => (
                            <motion.li
                              key={idx}
                              className="flex items-start gap-2 text-sm text-muted-foreground"
                              initial={{ opacity: 0, x: -10 }}
                              whileInView={{ opacity: 1, x: 0 }}
                              viewport={{ once: true }}
                              transition={{ duration: 0.4, delay: idx * 0.05 }}
                            >
                              <div className="w-1.5 h-1.5 bg-accent rounded-full mt-2 flex-shrink-0" />
                              {resp}
                            </motion.li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-medium mb-3 flex items-center gap-2">
                          <Network className="w-4 h-4" />
                          Tecnologías utilizadas
                        </h5>
                        <div className="flex flex-wrap gap-2">
                          {exp.technologies.map((tech, idx) => (
                            <motion.div
                              key={tech}
                              initial={{ opacity: 0, scale: 0.8 }}
                              whileInView={{ opacity: 1, scale: 1 }}
                              viewport={{ once: true }}
                              transition={{ duration: 0.3, delay: idx * 0.05 }}
                            >
                              <Badge variant="outline" className="hover:bg-accent hover:text-accent-foreground transition-colors">
                                {tech}
                              </Badge>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Current Status */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-600 rounded-full border border-green-500/20">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm font-medium">Currently employed and loving it!</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};