---
title: Datos del portfolio
cv_public: true
tags: [portfolio, facts]
updated: 2026-09-30
lang: es
facts:
  profile:
    name: Rafael Castaño
    role: Full Stack Developer
    location: Sevilla, España
    summary: >-
      Desarrollador Full Stack de Sevilla (España), titulado en Desarrollo de
      Aplicaciones Multiplataforma (DAM). Trabaja en AePTIC desarrollando
      aplicaciones web y móviles, y mantiene un laboratorio doméstico con
      modelos de IA locales.
  experience:
    - company: AePTIC
      role: Full Stack Developer
      period: junio 2025 - actualidad
      location: Sevilla, España
      type: Full-time
      description: >-
        Desarrollo de aplicaciones web, Android e iOS con tecnologías modernas,
        APIs RESTful y colaboración en equipos ágiles.
      responsibilities:
        - Desarrollo backend/frontend con Django y FastAPI
        - Implementación de APIs RESTful
        - Networking y configuración de servidores
        - Mantenimiento y optimización de aplicaciones
      technologies: [Python, Django, FastAPI, Kotlin, Dart, Flutter, MySQL, PostgreSQL, Git, Docker]
    - company: AePTIC
      role: Mobile App Developer
      period: marzo 2025 - junio 2025
      location: Sevilla, España
      type: Prácticas
      description: >-
        Prácticas del CFGS DAM: desarrollo de una aplicación Android y su
        backend, pruebas, depuración y documentación técnica.
      responsibilities:
        - Desarrollo de una aplicación Android funcional y optimizada
        - Backend con Node.js y Express
        - Pruebas, depuración y documentación técnica
      technologies: [Kotlin, Android Studio, Node.js, Express, MySQL, Git]
  projects:
    - name: Rafita
      description: >-
        Asistente personal con RAG sobre el Segundo Cerebro (Obsidian):
        recuperación semántica con bge-m3 y Chroma y generación con LLM local.
      technologies: [Python, RAG, Chroma, Ollama, bge-m3]
      url: https://github.com/rufae
      type: AI/ML
    - name: CV Web
      description: >-
        Este portfolio: SPA en React con chatbot IA y formulario de contacto
        sobre una API FastAPI, con despliegue self-hosted.
      technologies: [React, TypeScript, FastAPI, Python, Tailwind CSS]
      url: https://github.com/rufae/CV-Web
      type: Full Stack
    - name: Infraestructura IA híbrida
      description: >-
        Laboratorio doméstico: nodo HP para aplicaciones, torre GPU y nodo Dell
        con Ollama para inferencia, unidos por Tailscale.
      technologies: [Linux, Ollama, Docker, Tailscale, Networking]
      url: https://github.com/rufae
      type: Infra
  skills:
    - title: Frontend Development
      skills:
        - { name: React, level: 90 }
        - { name: Angular, level: 85 }
        - { name: HTML/CSS, level: 95 }
        - { name: JavaScript, level: 90 }
        - { name: TypeScript, level: 85 }
        - { name: Tailwind CSS, level: 90 }
    - title: Backend Development
      skills:
        - { name: Java, level: 90 }
        - { name: Spring Boot, level: 85 }
        - { name: Node.js, level: 80 }
        - { name: Python, level: 75 }
        - { name: REST APIs, level: 90 }
        - { name: MySQL, level: 80 }
    - title: Tools & Technologies
      skills:
        - { name: Git, level: 90 }
        - { name: Docker, level: 70 }
        - { name: Networking, level: 75 }
        - { name: Linux, level: 70 }
        - { name: AWS, level: 60 }
        - { name: Figma, level: 75 }
    - title: Learning & Emerging
      skills:
        - { name: Artificial Intelligence, level: 60 }
        - { name: Machine Learning, level: 55 }
        - { name: React Native, level: 70 }
        - { name: GraphQL, level: 50 }
        - { name: Kubernetes, level: 40 }
        - { name: TensorFlow, level: 45 }
  certifications:
    - Cursos de IA y machine learning (OpenWebinars, Nuclio Digital School)
    - React avanzado y Spring Boot (OpenWebinars)
    - Flutter y Docker (OpenWebinars)
  languages:
    - Español nativo
    - Inglés técnico
---

# Datos del portfolio

Nota canónica del contenido del portfolio: su frontmatter `facts` alimenta la web
y su texto alimenta al asistente (RAG). Si cambias algo aquí, regenera
`facts.json` con `scripts/build_facts.py` y ejecuta `eval/check_consistency.py`.

Rafael Castaño es un desarrollador Full Stack de Sevilla que trabaja en AePTIC
desde junio de 2025. Sus proyectos destacados son Rafita (RAG con bge-m3,
Chroma y Ollama), CV Web (React + FastAPI) y la Infraestructura IA híbrida de
su laboratorio doméstico (nodo HP, torre GPU, nodo Dell y Tailscale).
