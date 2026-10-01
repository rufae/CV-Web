# PROMPT MEGA-DETALLADO PARA FIGMA MAKE — Reconstruir "CVWEB" al 100 %

> **Instrucción global para Figma Make:** Reconstruye desde cero, pixel a pixel, un portfolio web de una sola página (SPA) completo, responsive, con modo claro/oscuro, animaciones de entrada y un widget de chat flotante. Sigue este documento como especificación única de verdad. No inventes nada que no esté aquí: si un valor no aparece, usa el valor por defecto de Tailwind v3 indicado en las tablas. Trabaja en desktop-first con breakpoints reales y entrega TODAS las pantallas listadas en §14.

---

## 0. RESUMEN DEL PRODUCTO

- **Nombre:** Portfolio personal de Rafael Castaño — "CV Web"
- **Tipo:** Landing page de una sola página con navegación ancla + widget de chat IA flotante + formulario de contacto.
- **Idiomas:** ES (por defecto) y EN, con toggle. Todo el contenido se duplica en ambos idiomas.
- **Temas:** Claro y Oscuro, con toggle persistente.
- **Estética:** Limpia, minimalista, técnica. Fondo blanco/negro, acento azul Dodger Blue `#1E90FF`, tarjetas con bordes finos grises, radios pequeños (5–10.5 px), glassmorphism sutil en la navegación, degradado azul muy tenue en el hero, animaciones de entrada suaves al hacer scroll (fade + slide), sin letter-spacing, tipografía Inter a 14 px base.
- **Stack visual a imitar:** React + Tailwind CSS v3 + Framer Motion + Lucide icons + Radix UI (Card/Badge/Button estilo shadcn/ui).

---

## 1. ESTRUCTURA DE PÁGINA (orden del DOM)

```
Página completa (bg = background, color = foreground, min-height 100vh)
├── 1. Controles fijos arriba-derecha (z-index 50): toggle idioma ES/EN + toggle tema
├── 2. Nav fija centrada arriba (z-index 40): píldora con 7 enlaces ancla
├── 3. <main>
│     ├── SECCIÓN 1: Hero          (#hero)
│     ├── SECCIÓN 2: Sobre mí      (#about)
│     ├── SECCIÓN 3: Experiencia   (#experience)
│     ├── SECCIÓN 4: Proyectos     (#projects)
│     ├── SECCIÓN 5: Habilidades   (#skills)
│     ├── SECCIÓN 6: AI Lab        (#ai-lab)
│     ├── SECCIÓN 7: Contacto      (#contact)
│     └── SECCIÓN 8: Privacidad    (#privacy)   ← NO está en el nav
├── 4. Footer
├── 5. Widget de Chat flotante (launcher + panel), z-index 50
└── 6. Toasts (sonner) arriba-derecha
```

**IDs de ancla del nav (en este orden):** `hero, about, experience, projects, skills, ai-lab, contact`.

**Scroll:** `scroll-behavior: smooth` en `html`. El enlace activo se resalta con `IntersectionObserver` (`rootMargin: '-40% 0px -55% 0px'`): activo → color `accent`; resto → color `muted-foreground`.

**Fondos alternos por sección (CRÍTICO):**

| Sección | Fondo |
|---|---|
| Hero | `hero-gradient` (ver §5.5) |
| About | `background` normal |
| **Experience** | **`bg-muted/20`** (muted al 20 % de opacidad) |
| Projects | `background` normal |
| **Skills** | **`bg-muted/20`** |
| **AI Lab** | **`bg-muted/20`** |
| Contact | `background` normal |
| Privacy | `background` normal |
| Footer | `bg-card` + `border-t border-border` |

---

## 2. DISEÑO TOKENS — COLORES (MÁS IMPORTANTE)

Los colores se definen como **tokens con doble variante claro/oscuro**. Crea variables y mapea cada componente a un token (nunca a un gris hardcodeado).

### 2.1 TEMA CLARO (default)

| Token | HSL | HEX | Uso |
|---|---|---|---|
| `background` | `0 0% 100%` | `#FFFFFF` | Fondo de página |
| `foreground` | `0 0% 0%` | `#000000` | Texto principal |
| `card` | `0 0% 100%` | `#FFFFFF` | Fondo de tarjetas |
| `card-foreground` | `0 0% 0%` | `#000000` | Texto en tarjetas |
| `popover` | `0 0% 100%` | `#FFFFFF` | Popovers/toasts |
| `popover-foreground` | `0 0% 0%` | `#000000` | |
| `primary` | `0 0% 0%` | `#000000` | Botón primario (negro) |
| `primary-foreground` | `0 0% 100%` | `#FFFFFF` | |
| `secondary` | `240 5% 96%` | `#F4F4F5` | Botón secundario / badge |
| `secondary-foreground` | `240 6% 10%` | `#18181B` | |
| `muted` | `240 5% 93%` | `#ECECEE` | Fondos sutiles, burbuja bot |
| `muted-foreground` | `240 4% 42%` | `#67676F` | Texto secundario |
| **`accent`** | `210 100% 56%` | **`#1F8FFF`** | **Azul de marca** |
| `accent-foreground` | `0 0% 100%` | `#FFFFFF` | Texto sobre acento |
| `destructive` | `0 72% 45%` | `#C52020` | Errores |
| `destructive-foreground` | `0 0% 100%` | `#FFFFFF` | |
| `border` | `0 0% 90%` | `#E6E6E6` | **Borde por defecto de TODO** |
| `input` | `0 0% 90%` | `#E6E6E6` | Borde de inputs |
| `input-background` | `240 9% 96%` | `#F4F4F6` | Fondo de inputs |
| `ring` | `210 100% 56%` | `#1F8FFF` | Focus ring |
| `switch-background` | `220 9% 81%` | `#CACDD3` | |

### 2.2 TEMA OSCURO (clase `.dark` en el raíz)

| Token | HSL | HEX |
|---|---|---|
| `background` | `0 0% 7%` | `#121212` |
| `foreground` | `0 0% 100%` | `#FFFFFF` |
| `card` | `0 0% 10%` | `#1A1A1A` |
| `card-foreground` | `0 0% 100%` | `#FFFFFF` |
| `popover` | `0 0% 10%` | `#1A1A1A` |
| `popover-foreground` | `0 0% 100%` | `#FFFFFF` |
| `primary` | `0 0% 100%` | `#FFFFFF` |
| `primary-foreground` | `0 0% 0%` | `#000000` |
| `secondary` | `0 0% 17%` | `#2B2B2B` |
| `secondary-foreground` | `0 0% 98%` | `#FAFAFA` |
| `muted` | `0 0% 17%` | `#2B2B2B` |
| `muted-foreground` | `0 0% 65%` | `#A6A6A6` |
| **`accent`** | `210 100% 56%` | **`#1F8FFF`** (idéntico) |
| `accent-foreground` | `0 0% 100%` | `#FFFFFF` |
| `destructive` | `0 72% 55%` | `#DF3A3A` |
| `destructive-foreground` | `0 0% 100%` | `#FFFFFF` |
| `border` | `0 0% 18%` | `#2E2E2E` |
| `input` | `0 0% 18%` | `#2E2E2E` |
| `input-background` | `0 0% 12%` | `#1F1F1F` |
| `ring` | `210 100% 56%` | `#1F8FFF` |
| `switch-background` | `0 0% 30%` | `#4C4C4C` |

> **Regla de oro:** `border` es el color por defecto de TODOS los bordes (`* { border-color: border }`). Grosor por defecto 1 px.

### 2.3 Colores de marca sueltos (Tailwind palette)

| Hex | Nombre | Uso |
|---|---|---|
| `#1E90FF` | Dodger Blue | `theme-color`, stop 1 del `text-gradient` |
| `#DC2626` | red-600 | stop 2 del `text-gradient` |
| `#22C55E` | green-500 | punto "online", dot avatar, skill ≥90, Infra badge |
| `#16A34A` | green-600 | texto "Disponible para proyectos" |
| `#10B981` | emerald-500 | fun fact "Clean code advocate" |
| `#F59E0B` | amber-500 | fun fact café, status degraded |
| `#B45309` | amber-700 | banner chat (claro) |
| `#FBBF24` | amber-400 | banner chat (oscuro) |
| `#A855F7` | purple-500 | fun fact música, badge AI/ML, cat. Tools |
| `#F97316` | orange-500 | fun fact Trophy, cat. Learning, skill 60–69 |
| `#3B82F6` | blue-500 | cat. Frontend, skill 80–89 |
| `#2563EB` | blue-600 | hover LinkedIn |
| `#60A5FA` | blue-400 | hover Twitter |
| `#EAB308` | yellow-500 | skill 70–79 |
| `#EF4444` | red-500 | skill <60, corazón footer |
| `#4B5563` | gray-600 | hover GitHub |
| `#F3F4F6` | gray-100 | fallback de imagen rota |
| `rgba(0,0,0,0.4)` | black/40 | overlay hover en imagen de proyecto |
| `rgba(255,255,255,0.1)` | white/10 | hover botones header del chat |

---

## 3. TIPOGRAFÍA

### 3.1 Familia
```
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
```
Mono (líneas de código del hero):
```
ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace
```
**No hay webfonts.** Inter se declara pero cae al sistema. Letter-spacing: **0 en todo** (no usar `tracking-*`).

### 3.2 ESCALA RAÍZ — CLAVE PARA EL TAMAÑO REAL
```
html { font-size: 14px }   ← TODA la escala rem se multiplica × 0.875
```

**Tabla de conversión (usa EXACTAMENTE estos px):**

| Clase Tailwind | PX reales | Line-height |
|---|---|---|
| `text-xs` | **10.5 px** | 14 px |
| `text-sm` | **12.25 px** | 17.5 px |
| `text-base` | **14 px** | 21 px |
| `text-lg` | **15.75 px** | 24.5 px |
| `text-xl` | **17.5 px** | 24.5 px |
| `text-2xl` | **21 px** | 28 px |
| `text-6xl` | **52.5 px** | 1 (52.5 px) |
| Hero `h1` | `clamp(35px, 8vw, 70px)` | 1.25 (`leading-tight`) |

### 3.3 Pesos
- 400 normal · **500 medium** (el más usado: h2, labels, botones, badges) · **600 semibold** (switch de idioma, título chat) · **700 bold** (span "Rafael" del hero).

### 3.4 Jerarquía real de títulos de sección
Los `<h2>` de cada sección se renderizan a **14 px / peso 500 / line-height 1.5** (mismo tamaño que el párrafo, solo se distingue por el peso). **Replica esto**: los títulos de sección NO son grandes; el elemento protagonista es la **barra azul** debajo. El `<h1>` del hero sí es enorme (clamp 35–70 px).

### 3.5 Line-heights explícitas usadas
- `leading-tight` 1.25 → h1 hero
- `leading-relaxed` 1.625 → resumen About
- `leading-none` 1 → CardTitle
- default 1.5 → todo lo demás

---

## 4. SISTEMA DE ESPACIADO, RADII, SOMBRAS

### 4.1 Radii (px reales — muy importantes)

| Clase | PX | Uso |
|---|---|---|
| `rounded` | **3.5** | botones de acción del bubble |
| `rounded-md` | **5.25** | **TODOS los Button y Badge**, inputs |
| `rounded-lg` | **7** | chips, icon-boxes, tiles sociales, figura hero |
| `rounded-xl` | **10.5** | **Card** (el radio principal) |
| `rounded-2xl` | **14** | burbujas de chat |
| `rounded-full` | círculo/pill | nav, botones circulares, avatares, dots |

### 4.2 Espaciado frecuente (px reales)

| Clase | px | | Clase | px |
|---|---|---|---|---|
| `p-1` | 3.5 | | `px-3` | 10.5 |
| `p-2` | 7 | | `px-4` | 14 |
| `p-3` | 10.5 | | `px-6` | 21 |
| `p-4` | 14 | | `py-2` | 7 |
| `p-6` | 21 | | `py-3` | 10.5 |
| `p-8` | 28 | | `py-4` | 14 |
| `gap-1/2/3/4/6/8/12` | 3.5 / 7 / 10.5 / 14 / 21 / 28 / 42 | | `py-12` (footer) | 84 |
| `mb-4/6/8/12/16` | 14 / 21 / 28 / 84 / **112** | | **`py-20` (secciones)** | **70** |
| `space-y-2/4/6/8/12` | 7 / 14 / 21 / 28 / 42 | | `pl-5` (listas) | 17.5 |
| `space-x-6` (nav) | 21 | | `mt-12` | 84 |

> **`mb-16` = 112 px** es el margen inferior de TODAS las cabeceras de sección. **`py-20 px-6` = 70 px vertical / 21 px horizontal** es el padding de TODAS las secciones.

### 4.3 Contenedores (ancho máximo, todos con `mx-auto`)

| Clase | Ancho real | Secciones |
|---|---|---|
| `max-w-6xl` | **1008 px** | About, Projects, Skills, AI Lab, Contact, Footer |
| `max-w-4xl` | **784 px** | Hero, Experience, Privacy |
| `max-w-2xl` | **588 px** | párrafos subtítulo |
| `max-w-md` | **392 px** | texto descarga CV |

### 4.4 Tamaños fijos notables (px reales)

| Elemento | Clase | px |
|---|---|---|
| Input/botón default | `h-9` | 31.5 |
| Botón sm | `h-8` | 28 |
| Botón lg | `h-10` | 35 |
| Icon button | `size-9` | 31.5 |
| Touch target chat | `h-11 w-11` → `sm:h-7` | 38.5 → 24.5 |
| Avatar About | `w-40 h-40` | 140 |
| Imagen proyecto | `h-48` | 168 |
| Launcher chat | `h-14 w-14` | 49 |
| Barra azul de sección | `w-20 h-1` | **70 × 3.5** |
| Botones hero (min-width) | `min-w-[200px]` | 200 |
| Dot status | `w-2.5 h-2.5` | 8.75 |
| Bullet timeline/lista | `w-1.5 h-1.5` | 1.75 |
| Línea timeline | `w-0.5` | 1.75 |
| Progress bar | `h-2` | 7 |
| Textarea chat | `min-h-10 max-h-32` | 35 → 112 |
| Panel chat (desktop) | `sm:w-[400px] sm:h-[600px]` | 400 × 600 |
| Panel chat bottom | `sm:bottom-24` | 84 desde abajo |

### 4.5 Breakpoints (Tailwind v3 defaults, sin personalizar)
`sm 640` · `md 768` · `lg 1024` · `xl 1280` · `2xl 1536`

### 4.6 Bordes
- Grosor **1 px** en el 99 % de los casos.
- `border-2` → figura geométrica del hero y scroll indicator.
- `border-4` → avatar, dot verde grande, timeline dot.
- Variantes con alfa: `border-border/50` (nav, controles), `border-accent/20` (avatar), `border-accent/50` (tiles sociales hover), `border-green-500/20` (pill experiencia), `border-muted-foreground/50` (scroll indicator), `border-green-500/20` (card disponibilidad).

### 4.7 Sombras

| Nombre | Valor |
|---|---|
| `shadow-lg` | `0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1)` |
| `shadow-xl` | `0 20px 25px -5px rgba(0,0,0,.1), 0 8px 10px -6px rgba(0,0,0,.1)` |
| `.glow-pulse` (animado) | `0 0 20px accent@40%` ↔ `0 0 40px accent@80%` |
| `.chat-window` | `0 10px 30px accent@25%` |
| `.message-user` | `0 2px 10px accent@40%` |
| `.message-bot` | `0 2px 10px foreground@5%` |
| Focus (inputs/badges) | `ring 3px accent@50%` + borde `ring` |
| Focus global (`a,button,input,textarea:focus-visible`) | `outline: 2px solid accent; outline-offset: 2px` |

### 4.8 Transiciones
- Base: `cubic-bezier(.4,0,.2,1)` **150 ms**.
- `duration-200` → nav links, inputs.
- `duration-300` → cards, launcher, hover de imagen.
- Hover de tarjeta: `transition-all duration-300` + `shadow-lg`/`shadow-xl`.

---

## 5. COMPONENTES BASE (estilo shadcn/ui)

### 5.1 Button
**Base:** `inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all`, iconos 16 × 16 px (`size-4`) a la izquierda con 8 px de separación. Disabled: `opacity 0.5`, sin puntero. Focus-visible: `border-color: ring` + `ring 3px ring@50%`.

**Variantes:**

| Variante | Estilo |
|---|---|
| `default` | fondo `primary`, texto `primary-foreground`, hover `primary@90%` → **negro/blanco en oscuro** |
| `outline` | `border 1px`, fondo `background`, texto `foreground`, **hover: fondo `accent`, texto `accent-foreground`**; en oscuro: `bg input@30%, border input, hover bg input@50%` |
| `secondary` | fondo `secondary`, texto `secondary-foreground`, hover `secondary@80%` |
| `ghost` | transparente, hover `bg accent`, `text accent-foreground` |
| `destructive` | fondo `destructive`, texto blanco, hover `destructive@90%` |
| `link` | texto `primary`, subrayado en hover, `underline-offset 4` |

**Tamaños:**

| size | Altura | Padding X | Radio |
|---|---|---|---|
| `default` | 31.5 px | 14 px (10.5 con icono) | 5.25 |
| `sm` | 28 px | 10.5 px (8.75 con icono) | 5.25 |
| `lg` | 35 px | 21 px (14 con icono) | 5.25 |
| `icon` | 31.5 × 31.5 px | — | 5.25 |

### 5.2 Card
- **Card:** fondo `card`, texto `card-foreground`, **`border-radius: 10.5 px`**, `border 1px border`, **gap interno 21 px**, flex-column.
- **CardHeader:** padding `21 px` laterales + `21 px` superior, gap 5.25 px.
- **CardTitle:** `<h4>` con `line-height: 1`, peso 500.
- **CardDescription:** color `muted-foreground`.
- **CardContent:** padding lateral 21 px; `padding-bottom: 21 px` si es el último hijo.
- **CardFooter:** `padding: 0 21px 21px`.
- Hover frecuente: `shadow-lg` o `shadow-xl` + `transition-all 300ms`.

### 5.3 Badge
`inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium whitespace-nowrap`.
→ **radio 5.25 px, alto ≈21 px, padding 7 × 1.75 px, texto 10.5 px / peso 500.**

| Variante | Estilo |
|---|---|
| `default` | borde transparente, fondo `primary`, texto `primary-foreground` (negro en claro) |
| `secondary` | borde transparente, fondo `secondary`, texto `secondary-foreground` |
| `outline` | borde `border`, texto `foreground`, hover `bg accent` + `text accent-foreground` |

### 5.4 Input / Textarea / Label
- **Input:** alto **31.5 px**, radio **5.25 px**, padding X 10.5 px, fondo `input-background`, borde 1 px `input`, texto 14 px (12.25 px en ≥768 px), placeholder `muted-foreground`. Focus: borde `ring` + `ring 3px ring@50%`.
- **Textarea:** min-height **56 px**, radio 5.25 px, mismo estilo, `resize: none`.
- **Label:** flex, `gap 8 px`, **12.25 px / peso 500 / line-height 1**, `select-none`.

### 5.5 Gradientes y glassmorphism
| Clase | Definición |
|---|---|
| `hero-gradient` (claro) | `linear-gradient(135deg, #FFFFFF 0%, rgba(31,143,255,0.05) 100%)` |
| `hero-gradient` (oscuro) | `linear-gradient(135deg, #121212 0%, rgba(31,143,255,0.10) 100%)` |
| `text-gradient` | `linear-gradient(135deg, #1E90FF, #DC2626)` + `background-clip:text; text-fill-color:transparent` |

**Glassmorphism (3 elementos idénticos):** `background: card@80%` + `border 1px border@50%` + `backdrop-filter: blur(4px)` + `border-radius: 9999px`.
1. Nav pill · 2. Switch de idioma · 3. Botón de tema.

### 5.6 Progress (barras de skills)
- Track: `background: primary@20%`, alto **7 px**, `border-radius: 9999px`, `overflow: hidden`.
- Indicador: capa superpuesta con ancho animado al `%` del skill, color según nivel (§10.3).

### 5.7 Avatar
Root: `position relative, overflow hidden, border-radius: 9999px`. En About: **140 × 140 px** con `border: 4px solid accent@20%`. Fallback: círculo `accent` con texto **"RA"** a 21 px, color `accent-foreground`.

### 5.8 Iconos — **Lucide** (stroke 2 px, round caps/joins)
`Activity, AlertTriangle, ArrowUp, BookOpen, Bot, Brain, Building2, Calendar, Check, Code, Code2, Coffee, Copy, Download, ExternalLink, Eye, Gamepad2, Github, Globe, Heart, Layout, Linkedin, Mail, MapPin, MessageCircle, MessageSquare, Moon, Music, Network, RotateCcw, Send, Server, Settings, ShieldCheck, Sparkles, Square, Sun, ThumbsDown, ThumbsUp, Trophy, Users, WifiOff, X`
Tamaños: 16 px (inline en botones), 20 px (títulos de card), 24 px (launcher chat).

### 5.9 Toasts (sonner)
Arriba-derecha. Fondo `popover`, texto `popover-foreground`, borde 1 px `border`. Éxito/error del formulario.

---

## 6. SECCIÓN A SECCIÓN (contenido textual LITERAL)

### 6.0 CABECERA DE SECCIÓN (patrón repetido 8 veces)
```
<div style="text-align:center; margin-bottom:112px">
  <h2 style="margin-bottom:14px; font-size:14px; font-weight:500">TÍTULO</h2>
  <div style="width:70px; height:3.5px; background:accent; margin:0 auto; border-radius:9999px"/>
  [<p style="color:muted-foreground; margin-top:14px; max-width:588px; margin-left:auto; margin-right:auto">SUBTÍTULO</p>]
</div>
```

---

### 6.1 CONTROLES FIJOS (esquina superior derecha, `top:24px; right:24px; z:50`)
Flex con `gap: 7 px`:

**a) Switch de idioma** — píldora glass: `bg card@80%`, `border 1px border@50%`, `radius 9999px`, `padding 3.5 px`, `backdrop-blur 4 px`.
- Dos botones `ES` / `EN`: `font-size 10.5 px`, `font-weight 600`, `padding 7 px 7 px`, `radius 9999px`.
- Activo: `bg accent`, `color accent-foreground`. Inactivo: `color muted-foreground`, hover `color accent`.

**b) Botón de tema** — círculo glass: `size 31.5 × 31.5 px`, `radius 9999px`, `bg card@80%`, `border 1px border@50%`, `backdrop-blur 4 px`.
- Icono `Moon` en tema claro / `Sun` en tema oscuro. `aria-label` = "Activar tema oscuro" / "Activar tema claro".
- Hover: `bg accent`, `color accent-foreground`.

---

### 6.2 NAV — píldora fija centrada
- `position: fixed; top: 24px; left: 50%; transform: translateX(-50%); z-index: 40`.
- Estilo: `bg card@80%` · `backdrop-blur 4 px` · `border 1px border@50%` · `radius 9999px` · `padding 7 px 21 px`.
- Interior: flex, `gap: 21 px` entre 7 enlaces.
- Enlace: `font-size 12.25 px`, `font-weight 500`, `color muted-foreground`, `transition color 200 ms`. Hover → `color accent`. Activo → `color accent`.

**Labels ES:** `Inicio · Sobre mí · Experiencia · Proyectos · Habilidades · AI Lab · Contacto`
**Labels EN:** `Home · About · Experience · Projects · Skills · AI Lab · Contact`

---

### 6.3 HERO (#hero)
`position: relative; min-height: 100vh; display:flex; align-items:center; justify-content:center; overflow:hidden; background: hero-gradient`.

**Contenido central** (`max-width 784 px; margin auto; padding 0 21 px; text-align:center`):

1. **`h1`** — `margin-bottom:21px; line-height:1.25; font-size: clamp(35px, 8vw, 70px)`:
   ```
   Hi, I am [Rafael]        ← "Rafael" con text-gradient + font-weight 700
   (salto de línea)
   Full Stack Developer passionate about [technology] and [AI]
                            ← "technology" y "AI" en color accent; bloque con margin-top 8px
   ```
2. **`p` subtítulo** — `font-size 17.5 px`, `color muted-foreground`, `margin-bottom:84px`, `max-width 588 px`, centrado:
   > *"Building innovative web solutions with modern technologies and a passion for clean, efficient code."*
3. **Fila de 3 botones** — flex, `gap:14px`, centrados; apilan en columna bajo 640 px. Todos con `min-width: 200 px`:
   1. **`View Projects`** — icono `Eye`, tamaño `lg`, **fondo `accent`, texto `accent-foreground`, animación glow-pulse** → ancla `#projects`
   2. **`Download CV`** — icono `Download`, variante `outline` con `border-color: accent; color: accent`; hover → fondo accent. Descarga `Rafael_CV.pdf`
   3. **`Contact`** — icono `MessageSquare`, variante `outline` → ancla `#contact`

**Capas decorativas de fondo:**
- **20 partículas:** círculos `4 × 4 px` (`w-1 h-1`), fondo `accent`, `border-radius 50%`, `opacity 0.6`, posiciones aleatorias en % (left/top). Animación: `translateY 0 → -30px → 0` + `opacity 0.6 → 1 → 0.6`, duración `3–5 s`, delay aleatorio `0–2 s`, infinito, ease-in-out.
- **4 líneas de código flotantes** — `font-size 10.5 px`, `color muted-foreground@40%`, fuente mono, posicionadas `left: 10% + i*20%`, `top: 20% + i*15%`. Animación: `opacity 0 → 0.6 → 0` y `translateX 0 → 100px → 200px`, duración 8 s, delay `i*1.5 s`, lineal, infinito. Texto literal:
  1. `const developer = new FullStack("Rafael");`
  2. `developer.setPassions(["Technology", "AI", "Football"]);`
  3. `developer.build(awesome_projects);`
  4. `if (developer.isReady()) { developer.launch(); }`
- **Cuadrado:** `top:80px; right:80px; width:80px; height:80px; border:2px solid accent; radius 7px; opacity 0.2` — rota `0→360°` en 20 s lineal infinito.
- **Círculo:** `bottom:128px; left:80px; width:48px; height:48px; background:accent; border-radius:50%; opacity 0.2` — escala `1 → 1.2 → 1` en 4 s ease-in-out infinito.
- **Scroll indicator:** centrado, `bottom:32px`. Contenedor `24 × 40 px`, `border 2px solid muted-foreground@50%`, `radius 9999px`, centrado horizontalmente; dentro un punto `4 × 12 px` fondo `accent`, `radius 9999px`, `margin-top 8px`. Ambos hacen `translateY 0 → 10 → 0` en 1.5 s infinito. Aparece con fade-in a los 1.5 s.

**Entradas (Framer Motion):** bloque principal `opacity 0→1, y 30→0`, 0.8 s ease-out; subtítulo con delay 0.3 s; botones `y 20→0` con delay 0.6 s.

---

### 6.4 SOBRE MÍ (#about)
Sección `padding: 70 px 21 px`, contenedor `max-width 1008 px`.

**Cabecera:** `Sobre mí` / `About me` + barra azul.

**Grid:** `2 columnas en ≥1024 px, gap 42 px, items centrados`. Columna izquierda centrada en móvil, alineada a la izquierda en desktop (`text-align`).

**Columna izquierda:**
- Avatar **140 × 140 px**, `border: 4px solid accent@20%`, imagen `/RAFAEL.png` (247×276), alt "Rafael". Fallback: círculo accent con **"RA"** 21 px.
  - Dot verde superpuesto: `bottom:-8px; right:-8px; width:32px; height:32px; background:green-500; border:4px solid background; border-radius:50%`.
  - Hover: escala 1.05 (spring stiffness 300, damping 20).
- `h3` a **21 px**: **`Rafael`**
- `p` color `accent`: **`Full Stack Developer • Sevilla, España`**
- `p` color `muted-foreground`, `line-height 1.625`:
  > *"Desarrollador Full Stack de Sevilla (España), titulado en Desarrollo de Aplicaciones Multiplataforma (DAM). Trabaja en AePTIC desarrollando aplicaciones web y móviles, y mantiene un laboratorio doméstico con modelos de IA locales."*

**Columna derecha:**
- **Card** (`padding 21 px`) con `h4` centrado `margin-bottom:21px`: **`Fun Facts About Me`** (igual en ES y EN).
- Grid **2 columnas, gap 14 px**. Cada fila: flex, `gap 10.5 px`, `padding 10.5 px`, `radius 7 px`, hover `bg accent@10%`. Icono en círculo `padding 7 px`, `border-radius 9999px`, texto blanco; etiqueta `12.25 px / peso 500`:

  | Icono | Color del círculo | Texto |
  |---|---|---|
  | `Gamepad2` | `#22C55E` | **Loves football** |
  | `Brain` | `accent` | **Always learning AI** |
  | `Coffee` | `#F59E0B` | **Coffee enthusiast** |
  | `Music` | `#A855F7` | **Coding with music** |
  | `Code2` | `#10B981` | **Clean code advocate** |
  | `Trophy` | `#F97316` | **Problem solver** |

- **3 stat-cards** (grid 3 columnas, gap 14 px, `margin-top 14 px`): Card con `padding 14 px`, centrado, hover `shadow-lg`:
  `2+` **Years Learning** · `10+` **Projects Built** · `5+` **Technologies**

**Animación:** columna izquierda entra desde `x:-50`, columna derecha desde `x:50` (delay 0.3), fun facts `y:10` escalonados `i*0.1`, stats delay 0.5.

---

### 6.5 EXPERIENCIA (#experience)
Sección con **fondo `bg-muted/20`**, `padding: 70 px 21 px`, contenedor `max-width 784 px`.

**Cabecera:** `Experiencia` / `Experience` + barra azul.

**Timeline (solo ≥768 px):**
- Línea vertical: `left:32px; top:0; bottom:0; width:1.75px; background:accent@30%`.
- Punto: `left:24px; width:16px; height:16px; background:accent; border-radius:50%; border:4px solid background; z-index:10`.
- Contenido desplazado `margin-left:112 px`.
- En móvil: sin línea ni punto, contenido a sangre.

**Tarjetas** (`space-y 42 px`), cada una en Card:

**Tarjeta 1**
- Icono `Building2` (20 px) en caja `padding 7 px; radius 7 px; background accent@10%; color accent`; al hover de la card → fondo `accent`, texto `accent-foreground`.
- Título: **`Full Stack Developer`** + Badge `default` → **`Full-time`** (negro con texto blanco en claro).
- Empresa `color accent, peso 500`: **`AePTIC`**
- Meta (`12.25 px`, `muted-foreground`, `margin-top 7 px`, iconos 12 px, gap 14 px): `Calendar` → **`junio 2025 - actualidad`** · `MapPin` → **`Sevilla, España`**
- Descripción (`muted-foreground`, `margin-bottom:21 px`):
  > *"Desarrollo de aplicaciones web, Android e iOS con tecnologías modernas, APIs RESTful y colaboración en equipos ágiles."*
- Subtítulo **`Responsabilidades`** (`peso 500, margin-bottom 10.5 px`, icono `Users`), lista `space-y 7 px`, cada item flex `gap 7 px`, `12.25 px muted-foreground`, con bullet `7 × 7 px background accent, radio 9999px, margin-top 7 px`:
  1. *Desarrollo backend/frontend con Django y FastAPI*
  2. *Implementación de APIs RESTful*
  3. *Networking y configuración de servidores*
  4. *Mantenimiento y optimización de aplicaciones*
- Subtítulo **`Tecnologías utilizadas`** (icono `Network`), chips flex-wrap `gap 7 px` con Badge `outline` (hover → fondo accent, texto accent-foreground):
  `Python · Django · FastAPI · Kotlin · Dart · Flutter · MySQL · PostgreSQL · Git · Docker`

**Tarjeta 2**
- Icono `Code` (20 px). Título: **`Mobile App Developer`** + Badge `secondary` → **`Prácticas`**.
- **`AePTIC`** · `marzo 2025 - junio 2025` · `Sevilla, España`
- Descripción: *"Prácticas del CFGS DAM: desarrollo de una aplicación Android y su backend, pruebas, depuración y documentación técnica."*
- Responsabilidades: *Desarrollo de una aplicación Android funcional y optimizada* · *Backend con Node.js y Express* · *Pruebas, depuración y documentación técnica*
- Tecnologías: `Kotlin · Android Studio · Node.js · Express · MySQL · Git`

**Pill de estado final** (`margin-top 84 px`, centrado): `padding 14 px 21 px`, fondo `green-500@10%`, texto `green-600`, `border-radius 9999px`, `border 1px green-500@20%`, con dot `8 × 8 px green-500` pulsante + texto **`Currently employed and loving it!`** (igual ES/EN).

**Animación:** tarjetas `y:50 → 0`, delay `i*0.2`; bullets `x:-10` delay `i*0.05`; chips `scale 0.8 → 1` delay `i*0.05`.

---

### 6.6 PROYECTOS (#projects)
Sección fondo normal, `padding 70/21`, contenedor `1008 px`.

**Cabecera:** `Proyectos` / `Projects` + barra + subtítulo (`max-width 588 px`):
> ES: *"Una selección de proyectos en los que he trabajado, demostrando mis habilidades en desarrollo full stack, inteligencia artificial y tecnologías modernas."*
> EN: *"A selection of projects I have worked on, showcasing my skills in full stack development, artificial intelligence and modern technologies."*

**Grid: 2 columnas desde 768 px, gap 28 px.** Cada proyecto: Card con `overflow:hidden`, `transition-all 300 ms`, hover `shadow-xl`.

**Media de cada card:**
- Imagen `width 100%`, `height 168 px`, `object-fit cover`; hover → `scale 1.05` (300 ms). `loading: lazy`, 600×300.
  - Rafita → `https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=600&h=300&fit=crop`
  - CV Web → `https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=600&h=300&fit=crop`
  - Infraestructura IA híbrida → `https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=300&fit=crop`
  - Fallback imagen rota: SVG data-URI 88×88 con icono de imagen rota, stroke `#000`, stroke-width 3.7, opacity 0.3, fondo `#F3F4F6`.
- **Overlay hover:** `inset 0`, `background rgba(0,0,0,0.4)`, opacidad 0 → 1 en hover (300 ms), centrando un botón `Github` (`secondary`, `sm`, icono `Code`) — y un botón `Demo` (`ExternalLink`) que NO aparece (sin URL live).
- **Badge** arriba-izquierda (`top:14px; left:14px`) según tipo:
  - `Full Stack` → fondo `accent`, texto `accent-foreground`
  - `AI/ML` → fondo `#A855F7`, texto blanco
  - `Infra` → fondo `#22C55E`, texto blanco

**Proyecto 1 — `Rafita`** (icono `Brain`, badge `AI/ML`)
- Desc: *"Asistente personal con RAG sobre el Segundo Cerebro (Obsidian): recuperación semántica con bge-m3 y Chroma y generación con LLM local."*
- **`Stack Tecnológico`:** `Python · RAG · Chroma · Ollama · bge-m3` (Badge `outline`, 10.5 px)
- Botón **`View on GitHub`** (`outline`, `sm`, ancho flexible, icono `Github`) → `https://github.com/rufae`

**Proyecto 2 — `CV Web`** (icono `Globe`, badge `Full Stack`)
- Desc: *"Este portfolio: SPA en React con chatbot IA y formulario de contacto sobre una API FastAPI, con despliegue self-hosted."*
- Stack: `React · TypeScript · FastAPI · Python · Tailwind CSS`
- Botón → `https://github.com/rufae/CV-Web`

**Proyecto 3 — `Infraestructura IA híbrida`** (icono `Server`, badge `Infra`)
- Desc: *"Laboratorio doméstico: nodo HP para aplicaciones, torre GPU y nodo Dell con Ollama para inferencia, unidos por Tailscale."*
- Stack: `Linux · Ollama · Docker · Tailscale · Networking`
- Botón → `https://github.com/rufae`

**Cierre** (`text-align center; margin-top 84 px`): botón `outline` `lg` con icono `Github` → **`Ver más proyectos en GitHub`** → `https://github.com/rufae`. Delay de animación 0.5 s.

**Animación:** cards `y:50 → 0` delay `i*0.1`; chips stack `scale 0.8 → 1` delay `i*0.05`.

---

### 6.7 HABILIDADES (#skills)
Sección **fondo `bg-muted/20`**, `padding 70/21`, contenedor `1008 px`.

**Cabecera:** `Habilidades` / `Skills` + barra + subtítulo:
> *"Mis competencias técnicas organizadas por categoría, desde desarrollo frontend y backend hasta tecnologías emergentes y herramientas especializadas."*

**Grid 2 columnas desde 768 px, gap 28 px.** 4 Cards (`height 100%`, hover `shadow-lg`, `transition-all 300 ms`).

**Título de card:** flex `gap 10.5 px`, con caja de icono `padding 7 px; radius 7 px; background accent@10%`:

| # | Título | Icono | Color icono |
|---|---|---|---|
| 1 | **Frontend Development** | `Layout` | `#3B82F6` (blue-500) |
| 2 | **Backend Development** | `Server` | `#22C55E` (green-500) |
| 3 | **Tools & Technologies** | `Settings` | `#A855F7` (purple-500) |
| 4 | **Learning & Emerging** | `Brain` | `#F97316` (orange-500) |

**Skills por card** (cada fila: `space-y 7 px` dentro de `space-y 21 px`):

| Categoría | Skills (emoji · nombre · nivel) |
|---|---|
| **Frontend** | ⚛️ React 90 · 🅰️ Angular 85 · 🌐 HTML/CSS 95 · 🟨 JavaScript 90 · 🔷 TypeScript 85 · 💨 Tailwind CSS 90 |
| **Backend** | ☕ Java 90 · 🍃 Spring Boot 85 · 🟢 Node.js 80 · 🐍 Python 75 · 🔗 REST APIs 90 · 🗄️ MySQL 80 |
| **Tools** | 📝 Git 90 · 🐳 Docker 70 · 🌐 Networking 75 · 🐧 Linux 70 · ☁️ AWS 60 · 🎨 Figma 75 |
| **Learning** | 🤖 Artificial Intelligence 60 · 📊 Machine Learning 55 · 📱 React Native 70 · 📈 GraphQL 50 · ⚙️ Kubernetes 40 · 🧠 TensorFlow 45 |

**Fila de skill:**
- Izquierda: emoji a **15.75 px** + nombre con `font-weight 500`.
- Derecha: Badge `outline` (10.5 px) con el nivel + `%` a `12.25 px muted-foreground`.
- **Barra:** track `primary@20%`, alto 7 px, radio 9999px; indicador superpuesto con ancho = nivel %, animado de 0 al valor en 1 s ease-out con delay `i*0.1`.
- **Color de barra por nivel:** `≥90 → #22C55E` · `≥80 → #3B82F6` · `≥70 → #EAB308` · `≥60 → #F97316` · `<60 → #EF4444`
- **Etiqueta de nivel:** `Expert / Advanced / Intermediate / Learning / Beginner` (mismos umbrales).

**Skills Overview** (`margin-top 84 px`): Card con `CardTitle` centrado **`Skills Overview`**, grid **4 columnas desde 768 px (2 en móvil), gap 21 px, text-align center**:
`15+` **Technologies** · `8+` **Expert Level** · `3+` **Learning AI/ML** · `24/7` **Always Learning**
(cifras a **21 px**, labels a `12.25 px muted-foreground`).

**Descarga de CV** (`margin-top 84 px`, centrado): Card `display:inline-block; padding 28 px`, `space-y 14 px`:
- `📄` a **52.5 px**
- `h3` → **`Download My CV`**
- `p muted-foreground max-width 392 px` → *"Get a detailed overview of my experience, education, and technical skills in PDF format."*
- Botón `lg` `outline` con `border-color accent; color accent` (hover: fondo accent) + icono `Download` → **`Download CV`**, `min-width 200 px` → `/curriculum-vitae.pdf` (descarga como `Rafael_CV.pdf`).

**Animación:** cards `y:50 → 0` delay `i*0.1`; skills `x:-20` delay `i*0.05`; resumen delay 0.5; card CV delay 0.6.

---

### 6.8 AI LAB (#ai-lab)
Sección **fondo `bg-muted/20`**, `padding 70/21`, contenedor `1008 px`.

**Cabecera:** `AI Lab` + barra + subtítulo:
> ES: *"La ingeniería del asistente, a la vista: arquitectura híbrida, estado en vivo y resultados de evaluación."*
> EN: *"The assistant engineering on display: hybrid architecture, live status and evaluation results."*

**Grid `gap 28 px`, 2 columnas desde 1024 px:**

**Columna izquierda — Card `Estado del asistente`:**
- Título con icono `Activity` (20 px, color `accent`).
- Fila de estado: dot `10 × 10 px` radio completo — `online → #22C55E` · `degraded → #F59E0B` · `offline → #EF4444`; label **`En línea` / `Degradado` / `Sin conexión`** (EN: Online/Degraded/Offline) + sufijo `muted-foreground` `· tier gpu` (o `cpu`).
- Imagen `/architecture.svg` → `width 100%`, `radius 7 px`, `border 1px border`, fondo `card`. Alt: *"Diagrama de arquitectura: Caddy, FastAPI, Chroma en el nodo HP y Ollama en la torre GPU y el nodo Dell por Tailscale"*.
  - **Paleta del SVG (960 × 380):** fondo `#0b1220`; cajas `fill #0f172a, stroke #1e90ff, stroke-width 2, rx 10`; cajas alternas `fill #101f38, stroke #38bdf8`; texto `#e2e8f0` 16 px Segoe UI; texto pequeño `#93a4bd` 12 px; flechas `#64748b` sw 2; líneas discontinuas `#475569` dash `6 5`.

**Columna derecha (`space-y 21 px`):**
1. Card **`Última evaluación (recuperación y rechazo)`** → grid **3 columnas, gap 14 px, text-align center**:
   - `0.983` → `recall@5`
   - `1.000` → `rechazo fuera de dominio`
   - `0` → `fugas`
   - pie: `modelo de embeddings:` **`bge-m3:latest`**
2. Card **`Qué puede ver el asistente`** (icono `ShieldCheck` 20 px, `accent`), texto `12.25 px muted-foreground`:
   > *"Solo indexa notas de la carpeta Public con cv_public: true, con redacción de datos sensibles. El vault privado nunca se expone."*
3. Card **`Enlaces`**, lista vertical `gap 7 px`, `12.25 px`; enlaces flex `gap 7 px`, color `accent`, hover subrayado:
   - `Github` → **`Repositorio en GitHub`** → `https://github.com/rufae/CV-Web`
   - `BookOpen` → **`Metodología y dataset`** → `https://github.com/rufae/CV-Web/blob/main/docs/evaluation.md`

---

### 6.9 CONTACTO (#contact)
Sección fondo normal, `padding 70/21`, contenedor `1008 px`.

**Cabecera:** `Contacto` / `Contact` + barra + subtítulo (`max-width 588 px`):
> ES: *"¿Tienes un proyecto en mente o quieres colaborar? Me encantaría escuchar sobre tu idea y explorar cómo podemos trabajar juntos."*
> EN: *"Do you have a project in mind or want to collaborate? I would love to hear about your idea and explore how we can work together."*

**Grid 2 columnas desde 1024 px, gap 42 px:**

**Columna izquierda — Card del formulario:**
- Título: icono `MessageSquare` (20 px, `accent`) + **`Envíame un mensaje`**
- Formulario `space-y 21 px`; cada campo `space-y 7 px`:
  | Label (icono 16 px, gap 8 px) | Control | Placeholder |
  |---|---|---|
  | `User` → **`Nombre completo`** (required) | Input | `Tu nombre` |
  | `Mail` → **`Email`** (type email) | Input | `tu@email.com` |
  | `FileText` → **`Mensaje`** | Textarea 6 filas | `Cuéntame sobre tu proyecto o idea...` |
  - Inputs: `transition-all 200 ms`, focus `ring 2 px accent`.
- Botón submit `lg` ancho completo, **fondo `accent`, texto `accent-foreground`, hover `accent@90%`**:
  - idle: icono `Send` + **`Enviar mensaje`**
  - enviando: spinner (16 px, `border 2px current, borde superior transparente, radio completo`, gira 1 s lineal infinito) + **`Enviando...`**, deshabilitado.
- Mensajes de validación (toast): **`Indica tu nombre (máximo 100 caracteres).`** / **`El email no parece válido.`** / **`Escribe un mensaje (máximo 2000 caracteres).`**
- Éxito (toast): **`¡Mensaje enviado correctamente! Te responderé pronto.`**
- Rate-limit: **`Demasiados mensajes; prueba en {n} s.`** · Budget: **`Se alcanzó el límite diario de mensajes. Inténtalo mañana.`** · Error: **`Error al enviar el mensaje. Por favor, intenta de nuevo.`**

**Columna derecha (`space-y 28 px`):**

1. **Card `Información de contacto`** — filas flex `gap 10.5 px`, `padding 10.5 px`, `radius 7 px`, hover `bg accent@10%`, desplazamiento `x: 0 → 5 px` al hover. Icono en caja `padding 7 px; radius 7 px; background accent@20%; color accent` → hover caja `accent` + texto `accent-foreground`:
   - `Mail` (20 px) · label **`Email`** · valor `rafaelcastanoblanca1805@gmail.com` · `mailto:`
   - `MapPin` (20 px) · **`Ubicación`** · **`Sevilla, España`** · `https://maps.google.com/?q=Seville,Spain`

2. **Card `Redes sociales`** — grid **2 columnas, gap 14 px**. Tile: flex `gap 10.5 px`, `padding 14 px`, `radius 7 px`, `border 1px border`; hover → `border-color accent@50%`; icono `scale 1.1` en hover; tile `scale 1.02` al hover / `0.98` al pulsar:

   | Nombre | Icono | URL | Color en hover |
   |---|---|---|---|
   | `GitHub` | `Github` (20 px) | `https://github.com/rufae` | `#4B5563` |
   | `LinkedIn` | `Linkedin` | `https://www.linkedin.com/in/rafael-castaño-blanca/` | `#2563EB` |
   | `Twitter` | `Twitter` | `https://twitter.com/rafael_dev` | `#60A5FA` |
   | `Email` | `Mail` | `mailto:rafaelcastanoblanca1805@gmail.com` | `#EF4444` |

3. **Card de disponibilidad:** `border 1px green-500@20%`, `background green-500@5%`, `padding 21 px`. Fila: dot `12 × 12 px green-500` pulsante + **`Disponible para proyectos`** (`font-weight 500`, color `#16A34A`) + debajo **`Actualmente abierto a nuevas oportunidades y colaboraciones`** (`12.25 px muted-foreground`).

**Animación:** izquierda `x:-50`, derecha `x:50` (delay 0.2); filas `y:10` delay `i*0.1` con hover `x:5`; social `scale 0.9 → 1` delay `i*0.1`; disponibilidad delay 0.4.

---

### 6.10 PRIVACIDAD (#privacy)
Sección fondo normal, `padding 70/21`, contenedor `784 px`.

**Cabecera:** `Privacidad` / `Privacy` + barra + intro (`max-width 588 px`):
> ES: *"Esta web es un portfolio personal. No hay cookies de seguimiento ni publicidad, por eso no verás banners de consentimiento."*

**Grid `gap 21 px`, 2 columnas desde 768 px.** 4 Cards con título `font-size 14 px` + icono `ShieldCheck` (16 px, `accent`):

1. **`Asistente de IA`** → *"El asistente solo responde con información pública del portfolio (notas de la carpeta Public con cv_public). No se almacenan tus conversaciones en el servidor. El feedback es anónimo: guarda únicamente la valoración (👍/👎) y metadatos técnicos, nunca la pregunta ni tu IP."*
2. **`Formulario de contacto`** → *"Si me escribes, trato tu nombre, email y mensaje con la única finalidad de responder a tu consulta. No se usan para marketing ni se ceden a terceros."*
3. **`Conservación`** → *"Los mensajes de contacto se conservan un máximo de 12 meses. El feedback anónimo se conserva para mejorar el asistente. Puedes pedir su supresión escribiendo al email de contacto."*
4. **`Cookies y analítica`** → *"No se usan cookies de terceros ni analítica con seguimiento. El tema (claro/oscuro) y tus preferencias se guardan solo en tu navegador."*

**Cierre** (`margin-top 28 px`, centrado, `12.25 px muted-foreground`): **`Tus derechos (RGPD)`** (`font-weight 500`, color `foreground`) + `: ` + *"Puedes ejercer tus derechos de acceso, rectificación, supresión y oposición escribiendo a"* + enlace `color accent` + subrayado → `rafaelcastanoblanca1805@gmail.com`.

*(EN: Privacy / AI assistant / Contact form / Retention / Cookies and analytics / Your rights (GDPR))*

---

### 6.11 FOOTER
`background: card`, `border-top 1px border`. Contenedor `1008 px`, `padding: 84 px 21 px`.

1. **Volver arriba** (`text-align center; margin-bottom 28 px`): botón `outline` `sm` **`border-radius 9999px`**, hover fondo `accent` + texto `accent-foreground`, icono `ArrowUp` (16 px, margen derecho 4 px) + **`Volver arriba`** → scroll suave al top.
2. **Grid 3 columnas desde 768 px, gap 28 px, `margin-bottom 28 px`:**
   - **Col 1** (centrada en móvil, izquierda en desktop): `h3` con **`text-gradient`** (azul→rojo) → **`Rafael`**; `p muted-foreground` → *"Full Stack Developer apasionado por crear soluciones innovadoras con tecnologías modernas."*
   - **Col 2** (centrada): `h4 margin-bottom 14 px` → **`Enlaces rápidos`**; lista `space-y 7 px` de enlaces `block 12.25 px muted-foreground`, hover `accent`, con desplazamiento `x: 0 → 2 px` (spring 400/10):
     `Sobre mí → #about` · `Experiencia → #experience` · `Proyectos → #projects` · `Habilidades → #skills` · `Contacto → #contact` · `Privacidad → #privacy`
   - **Col 3** (centrada en móvil, derecha en desktop): `h4 margin-bottom 14 px` → **`Sígueme`**; flex `justify-end` `gap 10.5 px`, botones `padding 7 px; background accent@10%; color muted-foreground; radius 7 px`; hover → fondo `accent`, texto `accent-foreground`, `scale 1.1, rotate 5°`; tap `scale 0.95`. Iconos 16 px: **GitHub** (`https://github.com/rufae`), **LinkedIn** (`https://www.linkedin.com/in/rafael-castaño-blanca/`), **Email** (`mailto:rafaelcastanoblanca1805@gmail.com`).
3. **Divisor:** `border-top 1px border`, `margin-bottom 21 px`.
4. **Copyright** (flex columna en móvil / fila en desktop, `justify-between`, `gap 14 px`, `12.25 px muted-foreground`):
   - `© {año actual} Rafael. Todos los derechos reservados.`
   - `Hecho con` + `Heart` (16 px, `#EF4444`, relleno completo, latiendo `scale 1 → 1.2 → 1` en 1 s) + ` y mucho ☕ en Sevilla, España`
5. **Info técnica** (`margin-top 21 px; padding-top 21 px; border-top 1px border; text-align center`): `10.5 px muted-foreground` → **`Construido con React, TypeScript, Tailwind CSS y Motion`** + ` • ` + span `color accent` = **`Siempre en evolución`**.

---

## 7. WIDGET DE CHAT FLOTANTE

### 7.1 Launcher — `fixed bottom:24px; right:24px; z-index:50`
Botón circular **49 × 49 px**, `radius 9999px`, **fondo `accent`, texto `accent-foreground`, `shadow-lg`**, `transition-all 300 ms`, con **animación `glow-pulse`** (halo azul pulsante), hover → `accent@90%` + `shadow-xl`.
- Icono `MessageCircle` (24 px) cerrado / `X` (24 px) abierto.
- `aria-label`: **`Abrir el asistente`** / **`Cerrar el asistente`**.

### 7.2 Panel
- **Móvil (<640 px):** `inset 0` (pantalla completa), z-50.
- **Desktop (≥640 px):** `bottom:84px; right:24px; width:400px; height:600px`.
- Estilo: `border-radius 14 px`, `box-shadow 0 10px 30px accent@25%`, `background card`, `border 1px border`, `overflow hidden`, flex-column.

**Header** (`flex, justify-between, padding 14 px, fondo accent, texto accent-foreground, border-bottom 1px border`):
- Avatar `31.5 × 31.5 px`, `radius 9999px`, fondo `accent-foreground`, icono `Bot` (20 px, color `accent`).
- `h3` `font-weight 600` → **`Asistente de Rafael`** / EN `Rafael assistant`
- `p` `10.5 px, opacity 0.9` → **`Asistente de IA; solo responde con información pública del portfolio`** / EN `AI assistant; it only answers with public portfolio information`
- Dos botones ghost-icon (`RotateCcw` = **`Nueva conversación`**, `X` = **`Cerrar el asistente`**), color `accent-foreground`, hover `rgba(255,255,255,0.1)`.

**Banners de estado** (`padding 7 px 14 px`, `12.25 px`):
- offline / degraded: `background amber-500@10%`, texto `#B45309` (claro) / `#FBBF24` (oscuro).
  - offline: icono `WifiOff` + **`El asistente está en mantenimiento.`** + enlace **`Usa el formulario de contacto`** (`#contact`)
  - degraded: **`Respuestas algo más lentas de lo normal.`**
- rate-limit: mismo estilo ámbar → **`Has alcanzado el límite de mensajes.`** + **`Reintenta en {n} s`**
- error: `background red-500@10%`, texto `#DC2626`, icono `AlertTriangle` + **`El asistente está en mantenimiento.`**
- refused: `background muted`, `muted-foreground` → **`¿Prefieres hablar con Rafael?`** + **`Usa el formulario de contacto`** (`accent`, subrayado)
- Botón **`Reintentar`** (`outline`, `sm`) en `error`/`rate_limited`.

**Área de mensajes** (`flex:1, overflow-y auto, padding 14 px, space-y 14 px`, `role=group aria-label="Conversación"`):
- Scrollbar custom: ancho **6 px**, track transparente, thumb `accent`, `border-radius 3 px`.
- **Estado vacío:**
  - `p` centrado `12.25 px muted-foreground`, `margin-bottom 10.5 px`: **`Pregúntame por su experiencia, proyectos o stack técnico.`**
  - Rótulo flex `gap 5.25 px`, `10.5 px peso 500 muted-foreground`, icono `Sparkles` (14 px) + **`Prueba con…`**
  - **4 botones starter**: `min-height 38.5 px`, `radius 7 px`, `border 1px border`, `padding 10.5 px`, `text-align left`, `12.25 px`, hover → `border accent@50%` + `bg accent@10%`, focus `ring 2 px accent`:
    1. `¿Qué proyectos de IA ha desarrollado Rafael?`
    2. `¿Cuál es su stack de backend?`
    3. `¿Qué experiencia tiene con Docker y Linux?`
    4. `¿Qué está haciendo ahora mismo?`
    (EN: *"Which AI projects has Rafael built?" · "What is his backend stack?" · "What experience does he have with Docker and Linux?" · "What is he working on right now?"*)
- **Burbujas** (`max-width 85%`, `padding 12.25 px`, `word-break: break-word`):
  - **Usuario** — alineada derecha, fondo `accent`, texto `accent-foreground`, **`border-radius: 14px 14px 3.5px 14px`**, `box-shadow 0 2px 10px accent@40%`, `white-space: pre-wrap`.
  - **Bot** — alineada izquierda, fondo `muted`, texto `card-foreground`, **`border-radius: 14px 14px 14px 3.5px`**, `box-shadow 0 2px 10px foreground@5%`. Markdown: párrafos, `ul` con `list-disc padding-left 17.5 px`, **negrita**, enlaces `accent` subrayados, citas `[n]` en `<sup color accent>`.
  - **Source chips** (`margin-top 7 px`, flex-wrap `gap 5.25 px`, `aria-label="Fuentes consultadas"`): `radius 9999px`, `background accent@15%`, `padding 1.75 px 7 px`, `10.5 px`, `color accent` → texto `[1] Título › Sección`.
  - **Acciones del bot** (`margin-top 7 px`, flex `gap 3.5 px`, `muted-foreground`): Copiar (`Copy`→`Check`, **`Copiar respuesta`**), `ThumbsUp` (**`Respuesta útil`**), `ThumbsDown` (**`Respuesta no útil`**); botones `padding 7 px`, `radius 3.5 px`, hover `accent`, focus `ring 2 px accent`; en ≥640 px reducidos a `28 × 28 px` (en móvil `44 × 44 px` táctil).
- **Typing indicator:** fondo `muted`, texto `muted-foreground`, `padding 7px 14px`, `radius 14 px`, `gap 4 px`, `width 56 px`; 3 puntos de **8 px** con keyframe `scale 0→1→0` (1.2 s infinito, delays 0.2/0.4 s). `aria-label="Buscando información"`.

**Composer** (`border-top 1px border`, `padding 10.5 px`):
- Textarea `flex:1`, `background input-background`, `min-height 35 px`, `max-height 112 px`, `radius 5.25 px`, `resize none`, 1 fila, `maxLength 500`, placeholder **`Escribe tu pregunta…`** / `Type your question…`. Enter envía, Shift+Enter salto de línea.
- Contador `10.5 px muted-foreground`, alineado a la derecha, visible cuando `length > 350` → `n/500`.
- Botón: si streaming → `outline icon` con `Square` (**`Detener la respuesta`**); si no → **fondo `accent`, texto `accent-foreground`, hover `accent@90%`** con `Send` (**`Enviar mensaje`**), deshabilitado si vacío.
- Franja `aria-live="polite"` solo para lectores de pantalla.
- Focus trap dentro del panel; `Escape` cierra y devuelve el foco al launcher.

---

## 8. ANIMACIONES Y MOTION (Framer Motion)

### 8.1 Patrón de entrada en scroll (repetido en casi todo)
```
initial     { opacity: 0, y: 20 }     (o x: -50 / x: 50 / y: 50 / scale: 0.9)
whileInView { opacity: 1, y: 0 }
viewport    { once: true }            ← solo una vez
transition  { duration: 0.6 }         (+ delay index * 0.1 | 0.2)
```

| Dónde | Variante |
|---|---|
| Cabeceras de sección | `y:20 → 0`, 0.6 s |
| About col. izq. | `x:-50 → 0`, 0.6 s; texto con delay 0.2 |
| About col. der. | `x:50 → 0`, delay 0.3; fun facts `y:10` delay `i*0.1`, hover `scale 1.02`; stats delay 0.5 |
| Experience items | `y:50 → 0`, delay `i*0.2`; bullets `x:-10` delay `i*0.05`; chips `scale 0.8 → 1` delay `i*0.05` |
| Projects cards | `y:50 → 0`, delay `i*0.1`; chips `scale 0.8→1` delay `i*0.05`; cierre delay 0.5 |
| Skills cards | `y:50 → 0`, delay `i*0.1`; skills `x:-20` delay `i*0.05`; **barra `width 0 → n%` 1 s easeOut delay `i*0.1`**; resumen delay 0.5; CV delay 0.6 |
| Contact | izq `x:-50`, der `x:50` delay 0.2; filas `y:10` delay `i*0.1` + hover `x:5`; social `scale 0.9→1` delay `i*0.1`, hover `1.02`, tap `0.98`; disponibilidad delay 0.4 |
| Footer | bloques `y:20` delays 0.1/0.2/0.3; enlaces hover `x:2` (spring 400/10); iconos hover `{scale:1.1, rotate:5°}`, tap `0.95`; corazón `scale [1,1.2,1]` 1 s |
| Hero | bloque `y:30 → 0` 0.8 s easeOut; subtítulo delay 0.3; botones `y:20` delay 0.6 |

### 8.2 Keyframes CSS
| Nombre | Definición | Dónde |
|---|---|---|
| `pulse-glow` | `0%,100% {box-shadow: 0 0 20px accent@40%} 50% {box-shadow: 0 0 40px accent@80%}` — 2 s ease-in-out infinito | clase `.glow-pulse`: botón "View Projects" y launcher del chat |
| `pulse` | `50% {opacity:.5}` — 2 s infinito | `.animate-pulse`: puntos verdes |
| `typing-bounce` | `0%,80%,100% {scale(0), opacity .3} 40% {scale(1), opacity 1}` — 1.2 s infinito | typing indicator |
| `float` | `0%,100% {translateY(0)} 50% {translateY(-20px)}` — 6 s | definida pero sin usar |

### 8.3 Hover de tarjetas
`group` → `hover:shadow-lg` o `hover:shadow-xl` + `transition-all 300 ms` + en la imagen `group-hover:scale-105` + overlay `group-hover:opacity-100`.

### 8.4 Spinner de envío
16 px, `border 2px solid current`, borde superior transparente, `border-radius 50%`, rotación 360° en 1 s lineal infinito.

---

## 9. MODO OSCURO

- **Mecanismo:** clase `.dark` en `<html>`; doble set de tokens §2.1/§2.2.
- **Anti-flash pre-layout:** script inline antes del bundle:
  ```js
  var saved = localStorage.getItem('theme');
  var dark = saved ? saved === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  if (dark) document.documentElement.classList.add('dark');
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
  ```
- **Toggle:** cambia la clase, persiste en `localStorage['theme']`, y actualiza `documentElement.style.colorScheme`.
- **Variantes `dark:*` puntuales:** `dark:bg-input/30`, `dark:border-input`, `dark:hover:bg-input/50` (inputs y outline), `dark:hover:bg-accent/50` (ghost), `dark:bg-destructive/60`, `dark:text-amber-400` (banners chat), `dark:focus-visible:ring-destructive/40`, `.dark .hero-gradient` (más azul).
- `accent` es **idéntico en ambos temas**; solo cambian fondos, bordes y textos secundarios.

---

## 10. CONTENIDO I18N (ES / EN)

**Idioma por defecto:** ES (se lee `localStorage['cvweb.lang']` o `navigator.language`; `es` salvo que empiece por "en").

### 10.1 Textos traducidos clave

| Clave | ES | EN |
|---|---|---|
| Nav | Inicio / Sobre mí / Experiencia / Proyectos / Habilidades / AI Lab / Contacto | Home / About / Experience / Projects / Skills / AI Lab / Contact |
| Secciones | Sobre mí / Experiencia / Proyectos / Habilidades / Contacto / Privacidad | About me / Experience / Projects / Skills / Contact / Privacy |
| Hero sub | *(igual)* | *(igual)* |
| Botones hero | Ver proyectos / Descargar CV / Contacto | View Projects / Download CV / Contact |
| About desc | *"Desarrollador Full Stack de Sevilla (España), titulado en Desarrollo de Aplicaciones Multiplataforma (DAM). Trabaja en AePTIC desarrollando aplicaciones web y móviles, y mantiene un laboratorio doméstico con modelos de IA locales."* | *"Full Stack developer from Seville (Spain), graduated in Multiplatform Application Development (DAM). Works at AePTIC building web and mobile apps, and keeps a home lab with local AI models."* |
| Projects subt | *"Una selección de proyectos en los que he trabajado, demostrando mis habilidades en desarrollo full stack, inteligencia artificial y tecnologías modernas."* | *"A selection of projects I have worked on, showcasing my skills in full stack development, artificial intelligence and modern technologies."* |
| Skills subt | *"Mis competencias técnicas organizadas por categoría, desde desarrollo frontend y backend hasta tecnologías emergentes y herramientas especializadas."* | *"My technical skills organized by category, from frontend and backend development to emerging technologies and specialized tools."* |
| AI Lab subt | *"La ingeniería del asistente, a la vista: arquitectura híbrida, estado en vivo y resultados de evaluación."* | *"The assistant engineering on display: hybrid architecture, live status and evaluation results."* |
| Contact subt | *"¿Tienes un proyecto en mente o quieres colaborar? Me encantaría escuchar sobre tu idea y explorar cómo podemos trabajar juntos."* | *"Do you have a project in mind or want to collaborate? I would love to hear about your idea and explore how we can work together."* |
| Form labels | Nombre completo / Email / Mensaje | Full name / Email / Message |
| Form placeholders | `Tu nombre` / `tu@email.com` / `Cuéntame sobre tu proyecto o idea...` | `Your name` / `you@email.com` / `Tell me about your project or idea...` |
| Submit | Enviar mensaje / Enviando... | Send message / Sending... |
| Title | `Rafael Castaño — Full Stack Developer` | `Rafael Castaño — Full Stack Developer (English)` |
| Meta desc | *"Portfolio de Rafael Castaño, desarrollador Full Stack en Sevilla: experiencia, proyectos con IA, habilidades y asistente virtual con RAG."* | *"Portfolio of Rafael Castaño, Full Stack developer in Seville: experience, AI projects, skills and a RAG-powered virtual assistant."* |

### 10.2 Textos SIEMPRE en inglés (no se traducen)
- `Fun Facts About Me` y sus 6 items.
- Stats About: `Years Learning`, `Projects Built`, `Technologies`.
- `Skills Overview` y sus 4 labels: `Technologies`, `Expert Level`, `Learning AI/ML`, `Always Learning`.
- `Download My CV` + *"Get a detailed overview of my experience, education, and technical skills in PDF format."* + botón `Download CV`.
- Nombres de categorías de skills: `Frontend Development`, `Backend Development`, `Tools & Technologies`, `Learning & Emerging`.
- Niveles de skill: `Expert / Advanced / Intermediate / Learning / Beginner`.
- Pill: `Currently employed and loving it!`
- Títulos de experiencia: `Full Stack Developer`, `Mobile App Developer`, badges `Full-time`.
- `Volver arriba`, `Construido con React, TypeScript, Tailwind CSS y Motion`, `Siempre en evolución`.
- `AI Lab`, `Skills Overview`.
- Botones de proyectos: `View on GitHub`, `Ver más proyectos en GitHub`.
- Chat: `Asistente de Rafael`, starters, banners.

### 10.3 Niveles de skill (badge + etiqueta)
| Rango | Badge | Etiqueta | Color barra |
|---|---|---|---|
| ≥90 | `90` | Expert | `#22C55E` |
| 80–89 | `85` | Advanced | `#3B82F6` |
| 70–79 | `75` | Intermediate | `#EAB308` |
| 60–69 | `60` | Learning | `#F97316` |
| <60 | `55` | Beginner | `#EF4444` |

---

## 11. DATOS DUROS DEL CV

### 11.1 Datos personales
| Campo | Valor |
|---|---|
| Nombre | **Rafael Castaño** (corto: **Rafael**) |
| Avatar fallback | **RA** |
| Rol | **Full Stack Developer** |
| Ubicación | **Sevilla, España** / EN **Seville, Spain** |
| Email | `rafaelcastanoblanca1805@gmail.com` |
| GitHub | `https://github.com/rufae` |
| LinkedIn | `https://www.linkedin.com/in/rafael-castaño-blanca/` |
| Twitter | `https://twitter.com/rafael_dev` |
| Google Maps | `https://maps.google.com/?q=Seville,Spain` |
| JSON-LD Person | jobTitle "Full Stack Developer"; knowsAbout: React, TypeScript, FastAPI, Python, RAG, Inteligencia artificial |
| theme-color | `#1E90FF` |

### 11.2 Experiencia
| Empresa | Rol | Periodo | Ubicación | Tipo |
|---|---|---|---|---|
| **AePTIC** | **Full Stack Developer** | **junio 2025 - actualidad** | Sevilla, España | **Full-time** |
| **AePTIC** | **Mobile App Developer** | **marzo 2025 - junio 2025** | Sevilla, España | **Prácticas** |

### 11.3 Educación y certificaciones
- **CFGS DAM:** *"Técnico Superior en Desarrollo de Aplicaciones Multiplataforma (CFGS DAM), obtenido con excelentes calificaciones."*
- **Certificaciones:** *"Cursos y certificaciones en OpenWebinars y Nuclio Digital School sobre inteligencia artificial, machine learning, React avanzado, Spring Boot, Flutter y Docker. Formación complementaria en inglés técnico."*
  1. `Cursos de IA y machine learning (OpenWebinars, Nuclio Digital School)`
  2. `React avanzado y Spring Boot (OpenWebinars)`
  3. `Flutter y Docker (OpenWebinars)`
- **Idiomas:** `Español nativo` · `Inglés técnico`

### 11.4 Estadísticas
- About: `2+` Years Learning · `10+` Projects Built · `5+` Technologies
- Skills Overview: `15+` Technologies · `8+` Expert Level · `3+` Learning AI/ML · `24/7` Always Learning
- AI Lab: `0.983` recall@5 · `1.000` rechazo fuera de dominio · `0` fugas · modelo `bge-m3:latest`

### 11.5 Bio larga (vault)
> *"Rafael Castaño es un desarrollador Full Stack de Sevilla (España). Le apasionan la programación, la inteligencia artificial y el fútbol. Mantiene un laboratorio doméstico con modelos de IA locales y disfruta construyendo proyectos propios de principio a fin."*

---

## 12. ACCESIBILIDAD

- **Focus visible global:** `outline: 2px solid accent; outline-offset: 2px` en `a, button, input, textarea`. Inputs/badges además `ring 3px accent@50%`.
- **Contraste:** texto principal 21:1; `muted-foreground` sobre blanco ≈ 5.6:1 (AA).
- **Targets táctiles:** ≥44 px en botones del chat en móvil (`h-11 w-11`), reducidos a 28 px en ≥640 px.
- **`prefers-reduced-motion`:**
  ```css
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
  ```
  + `.motion-reduce:animate-none` en el launcher; typing indicator sin animación.
- Labels asociados a inputs; `aria-label` en iconos botones; `aria-live="polite"` en el chat; focus trap + `Escape` en el panel; `role="group"` en el área de mensajes.
- Honeypot oculto en el formulario (`position absolute; left -9999px; height 0; width 0; overflow hidden`) con label *"No rellenar este campo"*.

---

## 13. COMPORTAMIENTOS Y ESTADOS

- **Nav activo** por IntersectionObserver (`rootMargin -40% 0px -55% 0px`).
- **Scroll suave** a anclas; "Volver arriba" con `scrollTo({top:0, behavior:'smooth'})`.
- **Formulario:** validación client-side (nombre 1–100 chars, email válido, mensaje 1–2000 chars) → toasts sonner; estado `Enviando...` con spinner; honeypot.
- **Chat:** estado vacío con starters → streaming con typing indicator → burbuja con markdown + chips de fuente + acciones (copiar 👍 👍👎) → banners de estado (offline/degraded/rate-limit/error/refused) → botón "Nueva conversación" → contador 500 caracteres → botón detener durante streaming.
- **Estado del AI Lab:** consulta `/api/status` cada 30 s → dot + label + tier.
- **Print:** `nav, footer, .fixed { display:none }`, `body{background:#fff;color:#000}`, `section{break-inside:avoid; padding:1rem 0}`.

---

## 14. PANTALLAS QUE DEBES ENTREGAR EN FIGMA MAKE

1. **Desktop 1440 px — Tema CLARO**, página completa scrolleable (todas las secciones §6.1–6.11).
2. **Desktop 1440 px — Tema OSCURO**, idéntico.
3. **Tablet 768 px** (grid colapsando: 2→1 columnas, nav y footer adaptados).
4. **Móvil 390 px** (nav en píldora compacta, hero apilado, grids de 1 columna, chat a pantalla completa).
5. **Componentes sueltos (design sheet):** Button (6 variantes × 4 tamaños × estados default/hover/focus/disabled), Badge (4 variantes), Card, Input/Textarea/Label en sus estados, Progress con los 5 colores, Avatar, chips, tiles sociales, partículas/gradientes.
6. **Widget de chat:** launcher, panel abierto con estado vacío + starters, panel con conversación de ejemplo (burbuja usuario, burbuja bot con markdown y source chips, typing indicator), banners de estado, composer con contador.
7. **Formulario de contacto:** estado vacío, focus, error de validación, estado "Enviando...", toast de éxito.
8. **Hero decorado:** partículas, 4 líneas de código, cuadrado/círculo, scroll indicator.
9. **Dark mode sheet de tokens** (muestra los 19 tokens claros y 19 oscuros).

---

## 15. CHECKLIST DE RECONSTRUCCIÓN

1. ✅ Root font-size **14 px** → toda escala rem × 0.875 (ver §3.2).
2. ✅ Tokens HSL claros/oscuros §2 con `accent = #1F8FFF` (`#1E90FF` de marca).
3. ✅ Tipografía Inter/system, base 14 px, lh 1.5, pesos 400/500/600/700, **sin letter-spacing**.
4. ✅ Títulos de sección a **14 px / peso 500** (no grandes); el protagonista es la barra azul 70 × 3.5 px.
5. ✅ Radii: **3.5 / 5.25 / 7 / 10.5 (Card) / 14 / full**.
6. ✅ Sombras `shadow-lg`, `shadow-xl`, `glow-pulse`, halo del chat.
7. ✅ Glass en 3 elementos: `card@80% + border@50% + blur(4px) + radius full`.
8. ✅ Secciones `padding 70 px 21 px`; contenedores 1008 px / 784 px / 588 px / 392 px; cabecera con `margin-bottom 112 px`.
9. ✅ Alternancia de fondo: normal → **muted/20** (Experience, Skills, AI Lab) → normal.
10. ✅ Iconos **Lucide** (lista §5.8) + emojis en skills.
11. ✅ Imágenes: `/RAFAEL.png`, `/architecture.svg`, 3 de Unsplash con parámetros exactos.
12. ✅ Dark mode completo + persistencia `localStorage['theme']` + script anti-flash.
13. ✅ i18n ES/EN con `localStorage['cvweb.lang']`.
14. ✅ Accesibilidad: reduced-motion, targets 44 px, focus-visible, contraste AA.
15. ✅ Animaciones: entrada `whileInView once` 0.6 s, delays escalonados, barras de skills animadas, partículas, glow, latido del corazón.
