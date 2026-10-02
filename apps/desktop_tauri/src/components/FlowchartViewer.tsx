import React, { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";
import { GitBranch, ZoomIn, ZoomOut, RotateCcw, Copy, Check, Download, Layers } from "lucide-react";

interface FlowchartViewerProps {
  chartDefinition?: string;
  title?: string;
}

const DEFAULT_CIVIC_CHART = `graph TD
    classDef default fill:#1e293b,stroke:#475569,stroke-width:1px,color:#f8fafc;
    classDef carried fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ecfdf5;
    classDef defeated fill:#7f1d1d,stroke:#ef4444,stroke-width:2px,color:#fef2f2;
    classDef pending fill:#78350f,stroke:#f59e0b,stroke-width:2px,color:#fffbeb;
    classDef root fill:#312e81,stroke:#6366f1,stroke-width:2px,color:#e0e7ff;

    Start(["Meeting Called to Order"]):::root
    Agenda["Adoption of Regular Agenda"]:::carried
    Start --> Agenda

    Mot104["Motion MOT-2026-104<br/>2027 Capital Infrastructure Budget"]:::carried
    Agenda --> Mot104

    Amend105["Amendment MOT-2026-105<br/>Defer Stormwater Upgrades"]:::defeated
    Mot104 -.->|Proposed Amend| Amend105
    Amend105 -.->|Defeated 2-5| Mot104

    Mot106["Motion MOT-2026-106<br/>Public Hearing Notice (Bylaw 24-09)"]:::carried
    Mot104 --> Mot106

    Mot107["Motion MOT-2026-107<br/>First Reading: Land Use Rezoning"]:::pending
    Mot106 --> Mot107
`;

export const FlowchartViewer: React.FC<FlowchartViewerProps> = ({
  chartDefinition = DEFAULT_CIVIC_CHART,
  title = "Council Decision & Parliamentary Flow",
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>("");
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [isCopied, setIsCopied] = useState<boolean>(false);
  const [renderError, setRenderError] = useState<string | null>(null);

  // Initialize mermaid configuration for dark civic theme
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      securityLevel: "loose",
      themeVariables: {
        darkMode: true,
        background: "#090d16",
        primaryColor: "#312e81",
        primaryTextColor: "#f8fafc",
        primaryBorderColor: "#6366f1",
        lineColor: "#94a3b8",
        secondaryColor: "#1e293b",
        tertiaryColor: "#0f172a",
        fontSize: "13px",
      },
    });
  }, []);

  // Re-render chart on code change
  useEffect(() => {
    let isMounted = true;
    const renderChart = async () => {
      try {
        setRenderError(null);
        const uniqueId = `mermaid-svg-${Date.now()}`;
        const { svg } = await mermaid.render(uniqueId, chartDefinition);
        if (isMounted) {
          setSvgContent(svg);
        }
      } catch (err: unknown) {
        console.error("Mermaid render error:", err);
        if (isMounted) {
          setRenderError(String(err));
        }
      }
    };

    renderChart();
    return () => {
      isMounted = false;
    };
  }, [chartDefinition]);

  const handleZoomIn = () => setZoomLevel((z) => Math.min(2.5, z + 0.15));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(0.4, z - 0.15));
  const handleResetZoom = () => setZoomLevel(1);

  const handleCopyCode = async () => {
    await navigator.clipboard.writeText(chartDefinition);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownloadSvg = () => {
    if (!svgContent) return;
    const blob = new Blob([svgContent], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `civic-decision-tree-${Date.now()}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md flex flex-col h-full">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-indigo-400" />
            {title}
          </h2>
          <p className="text-xs text-slate-400">
            Real-time visual parliamentary graph of motions, amendments, and voting branches
          </p>
        </div>

        {/* Toolbar */}
        <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 p-1 rounded-lg">
          <button
            onClick={handleZoomIn}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleResetZoom}
            className="px-2 py-1 text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded font-mono transition"
            title="Reset Zoom"
          >
            {Math.round(zoomLevel * 100)}%
          </button>
          <div className="w-[1px] h-4 bg-slate-800 mx-1" />
          <button
            onClick={handleCopyCode}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition"
            title="Copy Mermaid Code"
          >
            {isCopied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
          <button
            onClick={handleDownloadSvg}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition"
            title="Export SVG"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div
        ref={containerRef}
        className="relative flex-1 mt-4 overflow-auto min-h-[360px] bg-slate-950/80 border border-slate-800/80 rounded-xl p-6 flex items-center justify-center select-none"
      >
        {renderError ? (
          <div className="text-center p-6 text-rose-400 text-xs font-mono max-w-lg bg-rose-950/20 border border-rose-800/40 rounded-lg">
            <p className="font-semibold mb-2">Mermaid Syntax Error</p>
            <p>{renderError}</p>
          </div>
        ) : (
          <div
            style={{
              transform: `scale(${zoomLevel})`,
              transformOrigin: "center center",
              transition: "transform 0.15s ease-out",
            }}
            className="w-full flex justify-center items-center"
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        )}

        {/* Legend */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg flex items-center gap-3 text-[11px] backdrop-blur-sm">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500" /> Carried
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2 h-2 rounded-full bg-rose-500" /> Defeated
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2 h-2 rounded-full bg-amber-500" /> Pending
          </span>
        </div>
      </div>
    </div>
  );
};
