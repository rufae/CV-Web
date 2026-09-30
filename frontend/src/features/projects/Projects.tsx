import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { Badge } from '@/shared/ui/badge';
import { ImageWithFallback } from '@/shared/figma/ImageWithFallback';
import { Github, ExternalLink, Brain, Globe, Server } from 'lucide-react';

interface Project {
  id: number;
  name: string;
  description: string;
  image: string;
  technologies: string[];
  githubUrl: string;
  liveUrl?: string;
  type: string;
  icon: React.ReactNode;
}

export const Projects: React.FC = () => {
  const projects: Project[] = [
    {
      id: 1,
      name: 'Rafita',
      description:
        'Asistente con RAG sobre mi Segundo Cerebro (Obsidian): recuperación semántica con bge-m3 y Chroma y generación con LLM local.',
      image: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=600&h=300&fit=crop',
      technologies: ['Python', 'RAG', 'Chroma', 'Ollama', 'bge-m3'],
      githubUrl: 'https://github.com/rufae',
      type: 'AI/ML',
      icon: <Brain className="w-5 h-5" />,
    },
    {
      id: 2,
      name: 'CV Web',
      description:
        'Este portfolio: SPA en React con chatbot IA y formulario de contacto sobre una API FastAPI, con despliegue self-hosted.',
      image: 'https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=600&h=300&fit=crop',
      technologies: ['React', 'TypeScript', 'FastAPI', 'Python', 'Tailwind CSS'],
      githubUrl: 'https://github.com/rufae/CV-Web',
      type: 'Full Stack',
      icon: <Globe className="w-5 h-5" />,
    },
    {
      id: 3,
      name: 'Infraestructura IA híbrida',
      description:
        'Laboratorio doméstico: nodo HP para aplicaciones, torre GPU y nodo Dell con Ollama para inferencia, unidos por Tailscale.',
      image: 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=300&fit=crop',
      technologies: ['Linux', 'Ollama', 'Docker', 'Tailscale', 'Networking'],
      githubUrl: 'https://github.com/rufae',
      type: 'Infra',
      icon: <Server className="w-5 h-5" />,
    },
  ];

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Full Stack':
        return 'bg-accent text-accent-foreground';
      case 'AI/ML':
        return 'bg-purple-500 text-white';
      case 'Infra':
        return 'bg-green-500 text-white';
      default:
        return 'bg-secondary text-secondary-foreground';
    }
  };

  return (
    <section id="projects" className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="mb-4">Proyectos</h2>
          <div className="w-20 h-1 bg-accent mx-auto rounded-full" />
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            Una selección de proyectos en los que he trabajado, demostrando mis habilidades en
            desarrollo full stack, inteligencia artificial y tecnologías modernas.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {projects.map((project, index) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <Card className="group hover:shadow-xl transition-all duration-300 overflow-hidden">
                <div className="relative overflow-hidden">
                  <ImageWithFallback
                    src={project.image}
                    alt={project.name}
                    className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => window.open(project.githubUrl, '_blank')}
                      >
                        <Github className="w-4 h-4 mr-1" />
                        Code
                      </Button>
                      {project.liveUrl && (
                        <Button size="sm" onClick={() => window.open(project.liveUrl, '_blank')}>
                          <ExternalLink className="w-4 h-4 mr-1" />
                          Demo
                        </Button>
                      )}
                    </div>
                  </div>
                  <div className="absolute top-4 left-4">
                    <Badge className={getTypeColor(project.type)}>{project.type}</Badge>
                  </div>
                </div>

                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="p-2 bg-accent/10 rounded-lg text-accent">{project.icon}</div>
                    {project.name}
                  </CardTitle>
                </CardHeader>

                <CardContent>
                  <p className="text-muted-foreground mb-4 line-clamp-3">{project.description}</p>

                  <div className="space-y-4">
                    <div>
                      <h5 className="font-medium mb-2">Stack Tecnológico</h5>
                      <div className="flex flex-wrap gap-2">
                        {project.technologies.map((tech, idx) => (
                          <motion.div
                            key={tech}
                            initial={{ opacity: 0, scale: 0.8 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.2, delay: idx * 0.05 }}
                          >
                            <Badge variant="outline" className="text-xs">
                              {tech}
                            </Badge>
                          </motion.div>
                        ))}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => window.open(project.githubUrl, '_blank')}
                      >
                        <Github className="w-4 h-4 mr-1" />
                        View on GitHub
                      </Button>
                      {project.liveUrl && (
                        <Button
                          size="sm"
                          className="flex-1 bg-accent hover:bg-accent/90"
                          onClick={() => window.open(project.liveUrl, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4 mr-1" />
                          Live Demo
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <motion.div
          className="text-center mt-12"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <Button
            variant="outline"
            size="lg"
            onClick={() => window.open('https://github.com/rufae', '_blank')}
          >
            <Github className="w-4 h-4 mr-2" />
            Ver más proyectos en GitHub
          </Button>
        </motion.div>
      </div>
    </section>
  );
};
