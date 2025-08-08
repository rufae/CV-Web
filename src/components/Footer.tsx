import React from 'react';
import { motion } from "framer-motion";
import { Github, Linkedin, Mail, Heart, ArrowUp } from 'lucide-react';
import { Button } from './ui/button';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  const socialLinks = [
    {
      name: "GitHub",
      icon: <Github className="w-4 h-4" />,
      url: "https://github.com/rafael"
    },
    {
      name: "LinkedIn",
      icon: <Linkedin className="w-4 h-4" />,
      url: "https://www.linkedin.com/in/rafael-castaño-blanca/"
    },
    {
      name: "Email",
      icon: <Mail className="w-4 h-4" />,
      url: "mailto:rafaelcastanoblanca1805@gmail.com"
    }
  ];

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  return (
    <footer className="bg-card border-t border-border">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Back to Top Button */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Button
            variant="outline"
            size="sm"
            onClick={scrollToTop}
            className="rounded-full hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            <ArrowUp className="w-4 h-4 mr-1" />
            Volver arriba
          </Button>
        </motion.div>

        {/* Main Footer Content */}
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          {/* Brand Section */}
          <motion.div
            className="text-center md:text-left"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <div className="space-y-3">
              <h3 className="text-gradient">Rafael</h3>
              <p className="text-muted-foreground">
                Full Stack Developer apasionado por crear soluciones innovadoras con tecnologías modernas.
              </p>
            </div>
          </motion.div>

          {/* Quick Links */}
          <motion.div
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <h4 className="mb-4">Enlaces rápidos</h4>
            <div className="space-y-2">
              {['Sobre mí', 'Experiencia', 'Proyectos', 'Habilidades', 'Contacto'].map((link, index) => (
                <motion.a
                  key={link}
                  href={`#${['about', 'experience', 'projects', 'skills', 'contact'][index]}`}
                  className="block text-sm text-muted-foreground hover:text-accent transition-colors"
                  whileHover={{ x: 2 }}
                  transition={{ type: "spring", stiffness: 400, damping: 10 }}
                >
                  {link}
                </motion.a>
              ))}
            </div>
          </motion.div>

          {/* Social Links */}
          <motion.div
            className="text-center md:text-right"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <h4 className="mb-4">Sígueme</h4>
            <div className="flex justify-center md:justify-end gap-3">
              {socialLinks.map((social, index) => (
                <motion.a
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 bg-accent/10 text-muted-foreground hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: 10 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.1 }}
                >
                  {social.icon}
                </motion.a>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Divider */}
        <div className="border-t border-border mb-6" />

        {/* Copyright */}
        <motion.div
          className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="flex items-center gap-1">
            © {currentYear} Rafael. Todos los derechos reservados.
          </div>
          
          <div className="flex items-center gap-1">
            Hecho con
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
            >
              <Heart className="w-4 h-4 text-red-500 fill-current" />
            </motion.div>
            y mucho ☕ en Sevilla, España
          </div>
        </motion.div>

        {/* Additional Tech Info */}
        <motion.div
          className="mt-6 pt-6 border-t border-border text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.5 }}
        >
          <p className="text-xs text-muted-foreground">
            Construido con React, TypeScript, Tailwind CSS y Motion • 
            Alojado en Vercel • 
            <span className="text-accent"> Siempre en evolución</span>
          </p>
        </motion.div>
      </div>
    </footer>
  );
};