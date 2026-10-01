interface DiagramProps {
  variant: 'rag' | 'twin' | 'pyme' | 'agents';
  label: string;
}

const BOX = 'fill-[#0f172a] stroke-[#1e90ff]';
const BOX_ALT = 'fill-[#101f38] stroke-[#38bdf8]';

function Node({
  x,
  y,
  w = 120,
  h = 40,
  title,
  alt = false,
}: {
  x: number;
  y: number;
  w?: number;
  h?: number;
  title: string;
  alt?: boolean;
}) {
  return (
    <g tabIndex={0} role="img" aria-label={title}>
      <rect
        x={x}
        y={y}
        width={w}
        height={h}
        rx={8}
        strokeWidth={2}
        className={alt ? BOX_ALT : BOX}
      />
      <text
        x={x + w / 2}
        y={y + h / 2 + 4}
        textAnchor="middle"
        fontSize="11"
        fill="#e2e8f0"
        fontFamily="Inter Variable, sans-serif"
      >
        {title}
      </text>
    </g>
  );
}

function Arrow({ x1, y1, x2, y2 }: { x1: number; y1: number; x2: number; y2: number }) {
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke="#64748b"
      strokeWidth={2}
      markerEnd="url(#arrow)"
    />
  );
}

export function Diagram({ variant, label }: DiagramProps) {
  return (
    <figure className="overflow-hidden rounded-lg border border-border bg-[#0b1220]">
      <svg
        viewBox="0 0 480 240"
        role="img"
        aria-label={label}
        className="h-auto w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 z" fill="#64748b" />
          </marker>
        </defs>

        {variant === 'rag' && (
          <g>
            <Node x={20} y={100} title="Telegram" alt />
            <Arrow x1={140} y1={120} x2={170} y2={120} />
            <Node x={170} y={100} title="Núcleo" />
            <Arrow x1={290} y1={120} x2={320} y2={70} />
            <Node x={320} y={40} w={140} title="bge-m3 + Chroma" alt />
            <Arrow x1={320} y1={70} x2={290} y2={120} />
            <Arrow x1={290} y1={120} x2={320} y2={170} />
            <Node x={320} y={160} w={140} title="Ollama (local)" />
            <text
              x={20}
              y={220}
              fontSize="10"
              fill="#93a4bd"
              fontFamily="JetBrains Mono, monospace"
            >
              consulta → recuperación → generación
            </text>
          </g>
        )}

        {variant === 'twin' && (
          <g>
            <Node x={20} y={100} title="Visitante" alt />
            <Arrow x1={140} y1={120} x2={170} y2={120} />
            <Node x={170} y={100} title="FastAPI" />
            <Arrow x1={290} y1={120} x2={320} y2={70} />
            <Node x={320} y={40} w={140} title="Guardarraíles" alt />
            <Arrow x1={320} y1={90} x2={320} y2={140} />
            <Node x={310} y={150} w={160} title="Router GPU → Dell" />
            <text
              x={20}
              y={220}
              fontSize="10"
              fill="#93a4bd"
              fontFamily="JetBrains Mono, monospace"
            >
              allow-list · CV público · sin fugas
            </text>
          </g>
        )}

        {variant === 'pyme' && (
          <g>
            <Node x={20} y={40} w={140} title="Documentación" alt />
            <Arrow x1={160} y1={60} x2={200} y2={100} />
            <Node x={160} y={100} w={140} title="Ingesta + Chroma" />
            <Arrow x1={300} y1={120} x2={330} y2={120} />
            <Node x={330} y={100} w={130} title="Asistente" alt />
            <Node x={20} y={160} w={140} title="Proxmox" />
            <Arrow x1={160} y1={180} x2={330} y2={140} />
            <text
              x={20}
              y={220}
              fontSize="10"
              fill="#93a4bd"
              fontFamily="JetBrains Mono, monospace"
            >
              on-premise · datos del cliente
            </text>
          </g>
        )}

        {variant === 'agents' && (
          <g>
            <Node x={20} y={100} title="Telegram" alt />
            <Arrow x1={140} y1={120} x2={170} y2={120} />
            <Node x={170} y={100} title="Orquestador" />
            <Arrow x1={290} y1={110} x2={330} y2={60} />
            <Node x={330} y={30} w={130} title="Herramientas" alt />
            <Arrow x1={290} y1={130} x2={330} y2={180} />
            <Node x={330} y={170} w={130} title="Entrega" />
            <text
              x={20}
              y={220}
              fontSize="10"
              fill="#93a4bd"
              fontFamily="JetBrains Mono, monospace"
            >
              planificar → ejecutar → entregar
            </text>
          </g>
        )}
      </svg>
    </figure>
  );
}
