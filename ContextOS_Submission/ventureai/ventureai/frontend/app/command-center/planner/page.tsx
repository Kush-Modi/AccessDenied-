"use client";

import { useState, useCallback, useEffect } from "react";
import ReactFlow, {
  Node, Edge, Background, Controls, MiniMap,
  BackgroundVariant, Handle, Position, NodeProps,
} from "reactflow";
import "reactflow/dist/style.css";
import { motion, AnimatePresence } from "framer-motion";
import { Play, ShieldAlert, Cpu, Terminal, ArrowRight, Settings2, Info, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/utils";

const nodeTypes = { contextNode: ContextNode };

interface ContextNodeData {
  label: string;
  sub: string;
  icon: string;
  color: string;
  border: string;
  active?: boolean;
  status?: "idle" | "running" | "completed";
}

function ContextNode({ data }: NodeProps<ContextNodeData>) {
  const isCompleted = data.status === "completed";
  const isRunning = data.status === "running";
  const isIdle = !isCompleted && !isRunning;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.85 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "bg-[#F4F1EA] border px-4 py-3 w-52 transition-all duration-300 relative rounded-xl",
        isCompleted && "bg-[#1D8F88]/10 border-[#1D8F88]/40 shadow-sm",
        isRunning && "bg-[#F9A66C]/10 border-[#F9A66C]/60",
        isIdle && "border-[#4E5D5A]/15 opacity-60 hover:opacity-100"
      )}
    >
      <Handle type="target" position={Position.Top} className="!bg-[#4E5D5A]/30 !border-transparent !w-1.5 !h-1.5" />
      <div className="flex items-center gap-3">
        <div>
          <p className={cn(
            "text-sm font-semibold transition-colors",
            isCompleted && "text-[#1D8F88]",
            isRunning && "text-[#F9A66C]",
            isIdle && data.color
          )}>{data.label}</p>
          <p className="text-[#6A756F] text-[10px] mt-0.5 leading-tight">{data.sub}</p>
        </div>
      </div>

      {isRunning && (
        <span className="absolute -top-1.5 -right-1.5 flex h-3.5 w-3.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#F9A66C] opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-[#F9A66C] flex items-center justify-center">
            <Loader2 className="w-2.5 h-2.5 text-[#F7F5EF] animate-spin" />
          </span>
        </span>
      )}
      {isCompleted && (
        <span className="absolute -top-1.5 -right-1.5 flex h-3.5 w-3.5 rounded-full bg-[#1D8F88] flex items-center justify-center text-[9px] text-[#F7F5EF] font-bold shadow-sm">
          ✓
        </span>
      )}

      <Handle type="source" position={Position.Bottom} className="!bg-[#4E5D5A]/30 !border-transparent !w-1.5 !h-1.5" />
    </motion.div>
  );
}

const NODES: Node[] = [
  { id: "1", type: "contextNode", position: { x: 100, y: 0 }, data: { label: "Planner Agent", sub: "Plan Traversal · Tasks", icon: "", color: "text-blue-600", border: "border-blue-500/30" } },
  { id: "2", type: "contextNode", position: { x: 100, y: 120 }, data: { label: "Candidate Agent", sub: "Skills · Timeline", icon: "", color: "text-indigo-600", border: "border-indigo-500/30" } },
  { id: "3", type: "contextNode", position: { x: 100, y: 240 }, data: { label: "Client Agent", sub: "Target JDs · Priority", icon: "", color: "text-cyan-600", border: "border-cyan-500/30" } },
  { id: "4", type: "contextNode", position: { x: 100, y: 360 }, data: { label: "Knowledge Agent", sub: "Universal Knowledge layer", icon: "", color: "text-violet-600", border: "border-violet-500/30" } },
  { id: "5", type: "contextNode", position: { x: 100, y: 480 }, data: { label: "Hybrid RAG Engine", sub: "Filter → Rerank context", icon: "", color: "text-sky-600", border: "border-sky-500/30" } },
  { id: "6", type: "contextNode", position: { x: 100, y: 600 }, data: { label: "Planner Memory Loop", sub: "Feedback · Placements", icon: "", color: "text-amber-600", border: "border-amber-500/30" } },
  { id: "7", type: "contextNode", position: { x: 100, y: 720 }, data: { label: "Business Rules Engine", sub: "Policy · Override · Boosts", icon: "", color: "text-orange-600", border: "border-orange-500/30" } },
  { id: "8", type: "contextNode", position: { x: 100, y: 840 }, data: { label: "Action Planner Agent", sub: "Confidence Scorer Node", icon: "", color: "text-rose-600", border: "border-rose-500/30", active: true } },
  { id: "9", type: "contextNode", position: { x: 100, y: 960 }, data: { label: "HITL Gate Node", sub: "Interrupt · Human Consent", icon: "", color: "text-yellow-600", border: "border-yellow-500/30" } },
];

const EDGES: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true, style: { stroke: "#6366f1", strokeWidth: 2 } },
  { id: "e2-3", source: "2", target: "3", animated: true, style: { stroke: "#8b5cf6", strokeWidth: 2 } },
  { id: "e3-4", source: "3", target: "4", animated: true, style: { stroke: "#06b6d4", strokeWidth: 2 } },
  { id: "e4-5", source: "4", target: "5", animated: true, style: { stroke: "#0ea5e9", strokeWidth: 2 } },
  { id: "e5-6", source: "5", target: "6", animated: true, style: { stroke: "#f59e0b", strokeWidth: 2 } },
  { id: "e6-7", source: "6", target: "7", animated: true, style: { stroke: "#f97316", strokeWidth: 2 } },
  { id: "e7-8", source: "7", target: "8", animated: true, style: { stroke: "#ec4899", strokeWidth: 2 } },
  { id: "e8-9", source: "8", target: "9", animated: true, style: { stroke: "#eab308", strokeWidth: 2 } },
];

interface NodeDetails {
  title: string;
  description: string;
  role: string;
  inputs: string[];
  outputs: string[];
  telemetry: string;
  terminalLogs: string[];
}

const AGENT_DETAILS: Record<string, NodeDetails> = {
  "1": {
    title: "Planner Agent",
    role: "Orchestration & Workflow Planner",
    description: "Determines execution paths and generates sub-tasks dynamically using candidate and match profiles.",
    inputs: ["candidate_id", "execution_context"],
    outputs: ["planner_tasks", "planner_reasoning"],
    telemetry: "Operational · Average Latency: 420ms",
    terminalLogs: [
      "INFO: Orchestrator planner thread started.",
      "DEBUG: Checking supabase schema relationships...",
      "INFO: Formulating LangGraph task execution plan.",
      "SUCCESS: 4 execution steps generated and cached."
    ]
  },
  "2": {
    title: "Candidate Agent",
    role: "Candidate Classifier & Profiler",
    description: "Profiles candidates, retrieves CV structures, parses capabilities, and checks availability timeline.",
    inputs: ["candidate_id"],
    outputs: ["candidate_data", "candidate_skills", "candidate_location"],
    telemetry: "Operational · Average Latency: 650ms",
    terminalLogs: [
      "INFO: CandidateAgent parsing profile data...",
      "DEBUG: Querying supabase 'candidates' table for record.",
      "INFO: Found candidate. Skills parsed: Python, AWS, Docker.",
      "SUCCESS: Context constructed successfully."
    ]
  },
  "3": {
    title: "Client Agent",
    role: "Target Client Intelligence Agent",
    description: "Evaluates matching vacancies, filters candidate locations, and scores client priorities.",
    inputs: ["candidate_skills", "candidate_location"],
    outputs: ["matched_jobs", "client_health_scores"],
    telemetry: "Operational · Average Latency: 510ms",
    terminalLogs: [
      "INFO: ClientAgent scanning active roles.",
      "DEBUG: Checking clients table for matching positions.",
      "INFO: Found 3 candidate job descriptions with matching skills.",
      "SUCCESS: Target list populated."
    ]
  },
  "4": {
    title: "Knowledge Agent",
    role: "Universal Knowledge Retrospective Searcher",
    description: "Performs global search on emails, CRM entries, recruiter notes, and interview feedback records.",
    inputs: ["candidate_id", "client_id"],
    outputs: ["raw_knowledge_items"],
    telemetry: "Operational · Average Latency: 880ms",
    terminalLogs: [
      "INFO: KnowledgeAgent initializing semantic retrieval.",
      "DEBUG: Searching meeting notes, email threads & crm...",
      "INFO: Located 5 matching knowledge records.",
      "SUCCESS: Records transferred to hybrid RAG node."
    ]
  },
  "5": {
    title: "Hybrid RAG Engine",
    role: "Context Re-ranker & Embedder",
    description: "Combines Vector Similarity search and BM25 keywords search to rank knowledge sources.",
    inputs: ["raw_knowledge_items"],
    outputs: ["ranked_knowledge_items", "retrieval_trace"],
    telemetry: "Operational · Average Latency: 450ms",
    terminalLogs: [
      "INFO: HybridRAG engine loading raw items.",
      "DEBUG: Reranking with LLM semantic weighting...",
      "INFO: Re-ranked top items. RAG score calculated.",
      "SUCCESS: Context vectors mapped."
    ]
  },
  "6": {
    title: "Planner Memory Loop",
    role: "Self-Learning Memory Coordinator",
    description: "Queries past placements and recruiter notes to compute memory learning boosts/penalties.",
    inputs: ["candidate_id", "client_id", "job_id"],
    outputs: ["memory_score", "learning_score", "memory_trace"],
    telemetry: "Operational · Average Latency: 320ms",
    terminalLogs: [
      "INFO: MemoryLoop checking history logs.",
      "DEBUG: Found 2 past placements at client.",
      "INFO: Placement success rate is 100%. Appending memory boost.",
      "SUCCESS: Memory score evaluated."
    ]
  },
  "7": {
    title: "Business Rules Engine",
    role: "Deterministic Policy Guard",
    description: "Applies corporate business policies like Hiring Freeze, Suppression checks, and Priority updates.",
    inputs: ["client_context", "candidate_data"],
    outputs: ["score_adjustment", "blocked", "suppressed", "business_rule_trace"],
    telemetry: "Operational · Average Latency: 120ms",
    terminalLogs: [
      "INFO: BusinessRules check initiated.",
      "DEBUG: Checking Client Health and Hiring Freeze state...",
      "WARN: Rule Triggered: CLIENT_HIRING_FREEZE -> Suppress match confidence to 0%.",
      "SUCCESS: Policy adjustments finalized."
    ]
  },
  "8": {
    title: "Action Planner Agent",
    role: "Confidence Scorer Node",
    description: "Combines all agent context inputs to compute the final match score and build explainability paths.",
    inputs: ["candidate_fit_score", "top_knowledge_score", "memory_score", "client_health", "rule_adjustment"],
    outputs: ["top_recommendation", "confidence", "evidence_tree"],
    telemetry: "Operational · Average Latency: 780ms",
    terminalLogs: [
      "INFO: ActionPlanner assembling final match parameters.",
      "DEBUG: DecisionScorer weights loaded: Candidate: 35%, RAG: 25%, Memory: 20%.",
      "INFO: Match confidence scored at 88%.",
      "SUCCESS: evidence_tree object generated."
    ]
  },
  "9": {
    title: "HITL Gate Node",
    role: "Human-in-the-Loop Interrupt Gate",
    description: "Halts graph execution, updates Redis state, and waits for a recruiter approve/reject command.",
    inputs: ["top_recommendation", "session_id"],
    outputs: ["hitl_status", "recruiter_decision"],
    telemetry: "Pending Recruiter Action",
    terminalLogs: [
      "INFO: HITL gate active.",
      "DEBUG: Writing interrupt state to Redis memory saver.",
      "WARN: Pausing graph execution. Awaiting respondHITL callback..."
    ]
  }
};

export default function PlannerPage() {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("1");
  const [terminalOutput, setTerminalOutput] = useState<string[]>(AGENT_DETAILS["1"].terminalLogs);
  const [isRunningDry, setIsRunningDry] = useState(false);

  // Traversal simulation state
  const [activeNodeId, setActiveNodeId] = useState<string | null>(null);
  const [completedNodeIds, setCompletedNodeIds] = useState<string[]>([]);
  const [isSimulating, setIsSimulating] = useState(false);

  const startSimulation = () => {
    if (isSimulating) return;
    setIsSimulating(true);
    setCompletedNodeIds([]);
    setActiveNodeId("1");
    setSelectedNodeId("1");
    setTerminalOutput(AGENT_DETAILS["1"].terminalLogs);

    let idx = 1;
    const interval = setInterval(() => {
      if (idx < NODES.length) {
        const prevId = NODES[idx - 1].id;
        const nextId = NODES[idx].id;
        setCompletedNodeIds((prev) => [...prev, prevId]);
        setActiveNodeId(nextId);
        setSelectedNodeId(nextId);
        setTerminalOutput(AGENT_DETAILS[nextId].terminalLogs);
        idx++;
      } else {
        setCompletedNodeIds((prev) => [...prev, NODES[NODES.length - 1].id]);
        setActiveNodeId(null);
        clearInterval(interval);
        setIsSimulating(false);
      }
    }, 1500);
  };

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
    setTerminalOutput(AGENT_DETAILS[node.id]?.terminalLogs || []);
  }, []);

  const handleDryRun = () => {
    setIsRunningDry(true);
    setTerminalOutput([]);
    
    const logs = AGENT_DETAILS[selectedNodeId]?.terminalLogs || [];
    let currentLine = 0;
    
    const interval = setInterval(() => {
      if (currentLine < logs.length) {
        setTerminalOutput((prev) => [...prev, logs[currentLine]]);
        currentLine++;
      } else {
        clearInterval(interval);
        setIsRunningDry(false);
      }
    }, 800);
  };

  // Map nodes and edges dynamically according to simulation state
  const nodes = NODES.map((node) => {
    let status: "idle" | "running" | "completed" = "idle";
    if (isSimulating) {
      if (activeNodeId === node.id) {
        status = "running";
      } else if (completedNodeIds.includes(node.id)) {
        status = "completed";
      }
    } else {
      // Static defaults when not simulating
      if (node.id === "8") status = "running";
      else if (Number(node.id) < 8) status = "completed";
    }
    return {
      ...node,
      data: {
        ...node.data,
        status,
      },
    };
  });

  const edges = EDGES.map((edge) => {
    const isSourceCompleted = completedNodeIds.includes(edge.source) || (!isSimulating && Number(edge.source) < 8);
    const isSourceActive = activeNodeId === edge.source || (!isSimulating && edge.source === "8");
    return {
      ...edge,
      animated: isSourceActive || isSourceCompleted,
      style: {
        stroke: isSourceCompleted ? "#22c55e" : isSourceActive ? "#6c63ff" : "rgba(255,255,255,0.06)",
        strokeWidth: isSourceActive || isSourceCompleted ? 2.5 : 1.5,
      },
    };
  });

  const details = AGENT_DETAILS[selectedNodeId] || AGENT_DETAILS["1"];

  return (
    <div className="h-full flex flex-col bg-[#F7F5EF] text-[#4E5D5A]">
      <div className="px-6 py-4 border-b border-[var(--color-context-border)] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h1 className="text-[#4E5D5A] font-semibold text-sm">AI Planner</h1>
          <span className="text-[#6A756F]/40">·</span>
          <span className="text-xs text-[#6A756F]">Interactive Orchestration Tool</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={startSimulation}
            disabled={isSimulating}
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1D8F88] hover:bg-[#1D8F88]/80 disabled:bg-[#4E5D5A]/10 disabled:text-[#6A756F] text-[#F7F5EF] text-xs font-semibold transition-colors"
          >
            {isSimulating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Simulating...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5" />
                Simulate Traversal
              </>
            )}
          </button>
          <div className="flex items-center gap-2 bg-[#1D8F88]/10 border border-[#1D8F88]/20 px-3 py-1.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-[#1D8F88] status-pulse" />
            <span className="text-[10px] text-[#1D8F88] font-mono font-medium">Graph Engine Active</span>
          </div>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* React Flow Workspace */}
        <div className="flex-1 relative bg-[#F7F5EF]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodeClick={onNodeClick}
            fitView
            fitViewOptions={{ padding: 0.2 }}
            minZoom={0.3}
            maxZoom={1.5}
            attributionPosition="bottom-right"
          >
            <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="rgba(78, 93, 90, 0.15)" />
            <Controls />
            <MiniMap
              nodeColor={(node) => {
                const status = (node.data as any).status;
                if (status === "completed") return "#1D8F88";
                if (status === "running") return "#F9A66C";
                return "rgba(78, 93, 90, 0.1)";
              }}
              maskColor="rgba(247,245,239,0.85)"
            />
          </ReactFlow>
          <div className="absolute top-4 left-4 bg-[#F4F1EA]/90 border border-[#4E5D5A]/10 rounded-xl p-3 max-w-xs backdrop-blur pointer-events-none shadow-sm">
            <p className="text-[#4E5D5A] text-xs font-semibold flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#1D8F88]" /> Interactive Mode
            </p>
            <p className="text-[#6A756F] text-[10px] mt-1 leading-relaxed">
              Click any node in the orchestration graph to inspect its parameters, schemas, and simulate execution.
            </p>
          </div>
        </div>

        {/* Selected Node Sidebar inspector */}
        <div className="w-96 border-l border-[var(--color-context-border)] bg-[#F4F1EA] flex flex-col overflow-y-auto">
          <div className="p-5 border-b border-[var(--color-context-border)]">
            <div className="flex items-center gap-2 text-[#6A756F] text-xs mb-1">
              <Cpu className="w-3.5 h-3.5" />
              <span>ORCHESTRATION AGENT INSTANCE</span>
            </div>
            <h2 className="text-[#4E5D5A] text-lg font-semibold">{details.title}</h2>
            <p className="text-[#1D8F88] text-xs mt-0.5">{details.role}</p>
            <p className="text-[#6A756F] text-xs mt-3 leading-relaxed">{details.description}</p>
          </div>

          <div className="p-5 space-y-4 border-b border-[var(--color-context-border)]">
            {/* Inputs / Outputs */}
            <div>
              <span className="text-[#6A756F] text-[10px] font-mono uppercase tracking-wider block mb-2">Input Schemas</span>
              <div className="flex flex-wrap gap-1">
                {details.inputs.map((inp) => (
                  <span key={inp} className="px-2 py-0.5 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded text-[#4E5D5A] text-[10px] font-mono">{inp}</span>
                ))}
              </div>
            </div>

            <div>
              <span className="text-[#6A756F] text-[10px] font-mono uppercase tracking-wider block mb-2">Output Context</span>
              <div className="flex flex-wrap gap-1">
                {details.outputs.map((out) => (
                  <span key={out} className="px-2 py-0.5 bg-[#1D8F88]/10 border border-[#1D8F88]/20 rounded text-[#1D8F88] text-[10px] font-mono">{out}</span>
                ))}
              </div>
            </div>

            <div>
              <span className="text-[#6A756F] text-[10px] font-mono uppercase tracking-wider block mb-1.5">Health & Latency</span>
              <p className="text-[#4E5D5A] text-xs font-mono">{details.telemetry}</p>
            </div>
          </div>

          {/* Interactive Agent Dry-Run Simulator */}
          <div className="flex-1 p-5 flex flex-col justify-end">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[#6A756F] text-[10px] font-mono uppercase tracking-wider flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-[#6A756F]/60" /> Node Execution Logs
              </span>
              <button
                onClick={handleDryRun}
                disabled={isRunningDry}
                className="bg-[#1D8F88]/10 hover:bg-[#1D8F88]/20 border border-[#1D8F88]/20 text-[#1D8F88] text-[10px] font-medium px-2 py-1 rounded flex items-center gap-1 transition-all disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" /> Dry Run
              </button>
            </div>

            <div className="flex-1 bg-[#EFE8DE] border border-[#4E5D5A]/10 rounded-lg p-3 font-mono text-[10px] space-y-1.5 overflow-y-auto max-h-48 min-h-32 shadow-inner">
              {terminalOutput.map((log, i) => (
                <div key={i} className={
                  log.startsWith("SUCCESS") ? "text-[#1D8F88]" :
                  log.startsWith("WARN") ? "text-[#F9A66C] font-semibold" :
                  log.startsWith("DEBUG") ? "text-[#6A756F]/70" :
                  "text-[#4E5D5A]"
                }>
                  {log}
                </div>
              ))}
              {isRunningDry && (
                <div className="flex items-center gap-1.5 text-[#1D8F88]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#1D8F88] status-pulse" />
                  Running simulation...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
