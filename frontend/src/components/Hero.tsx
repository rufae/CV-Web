import React from 'react';
import { motion } from "framer-motion";
import { Button } from './ui/button';
import { Download, Eye, MessageSquare } from 'lucide-react';

export const Hero: React.FC = () => {
  const codeLines = [
    'const developer = new FullStack("Rafael");',
    'developer.setPassions(["Technology", "AI", "Football"]);',
    'developer.build(awesome_projects);',
    'if (developer.isReady()) { developer.launch(); }'
  ];

  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 2,
  }));

  return (
    <section id="hero" className="relative min-h-screen flex items-center justify-center overflow-hidden hero-gradient">
      {/* Animated Background Particles */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-1 h-1 bg-accent rounded-full opacity-60"
            style={{
              left: `${particle.x}%`,
              top: `${particle.y}%`,
            }}
            animate={{
              y: [0, -30, 0],
              opacity: [0.6, 1, 0.6],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              delay: particle.delay,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      {/* Floating Code Lines */}
      <div className="absolute inset-0 pointer-events-none">
        {codeLines.map((line, index) => (
          <motion.div
            key={index}
            className="absolute text-xs text-muted-foreground/40 font-mono"
            style={{
              left: `${10 + (index * 20)}%`,
              top: `${20 + (index * 15)}%`,
            }}
            initial={{ opacity: 0, x: -50 }}
            animate={{
              opacity: [0, 0.6, 0],
              x: [0, 100, 200],
            }}
            transition={{
              duration: 8,
              delay: index * 1.5,
              repeat: Infinity,
              ease: "linear",
            }}
          >
            {line}
          </motion.div>
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.h1 
            className="mb-6 leading-tight"
            style={{ fontSize: 'clamp(2.5rem, 8vw, 5rem)' }}
          >
            Hi, I'm{' '}
            <span className="text-gradient font-bold">Rafael</span>
            <br />
            <span className="block mt-2">
              Full Stack Developer passionate about{' '}
              <span className="text-accent">technology</span> and{' '}
              <span className="text-accent">AI</span>
            </span>
          </motion.h1>

          <motion.p
            className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            Building innovative web solutions with modern technologies and a passion for clean, efficient code.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <Button
              size="lg"
              className="bg-accent hover:bg-accent/90 text-accent-foreground glow-pulse min-w-[200px]"
              onClick={() => document.getElementById('projects')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <Eye className="w-4 h-4 mr-2" />
              View Projects
            </Button>
            
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

            
            <Button
              size="lg"
              variant="outline"
              className="min-w-[200px]"
              onClick={() => document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Contact
            </Button>
          </motion.div>
        </motion.div>
      </div>

      {/* Floating Geometric Shape */}
      <motion.div
        className="absolute top-20 right-20 w-20 h-20 border-2 border-accent rounded-lg opacity-20"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      />
      
      <motion.div
        className="absolute bottom-32 left-20 w-12 h-12 bg-accent rounded-full opacity-20"
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
      >
        <motion.div
          className="w-6 h-10 border-2 border-muted-foreground/50 rounded-full flex justify-center"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <motion.div
            className="w-1 h-3 bg-accent rounded-full mt-2"
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </motion.div>
      </motion.div>
    </section>
  );
};