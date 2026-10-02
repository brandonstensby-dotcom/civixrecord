import React, { useState, useEffect } from "react";
import { CheckCircle2, XCircle, Clock, AlertTriangle, Users, FileText, Search, Filter } from "lucide-react";

export type MotionStatus = "PENDING" | "CARRIED" | "DEFEATED" | "TABLED";

export interface MotionItem {
  motion_id: string;
  timestamp_start: number;
  timestamp_end: number;
  mover: string;
  seconder?: string | null;
  motion_text: string;
  motion_type: string;
  outcome: MotionStatus;
  votes_for: string[];
  votes_against: string[];
}

interface MotionLiveFeedProps {
  onSelectMotion?: (motion: MotionItem) => void;
  externalMotions?: MotionItem[];
}

const INITIAL_MOCK_MOTIONS: MotionItem[] = [
  {
    motion_id: "MOT-2026-104",
    timestamp_start: 124.5,
    timestamp_end: 188.0,
    mover: "Councillor M. Henderson",
    seconder: "Councillor S. Thorne",
    motion_text: "That Council adopt the proposed 2027 Capital Infrastructure Budget with amendments to Section 4.2 regarding secondary road rehabilitation.",
    motion_type: "MAIN",
    outcome: "CARRIED",
    votes_for: [
      "Mayor E. Vance",
      "Councillor M. Henderson",
      "Councillor S. Thorne",
      "Councillor D. Wright",
      "Councillor K. Patel",
    ],
    votes_against: [
      "Councillor R. Kowalski",
      "Councillor A. Sterling",
    ],
  },
  {
    motion_id: "MOT-2026-105",
    timestamp_start: 245.0,
    timestamp_end: 290.2,
    mover: "Councillor R. Kowalski",
    seconder: "Councillor A. Sterling",
    motion_text: "That the motion be amended to reduce arterial street paving expenditure by $450,000 and defer stormwater channel upgrades to Q3 2027.",
    motion_type: "AMENDMENT",
    outcome: "DEFEATED",
    votes_for: [
      "Councillor R. Kowalski",
      "Councillor A. Sterling",
    ],
    votes_against: [
      "Mayor E. Vance",
      "Councillor M. Henderson",
      "Councillor S. Thorne",
      "Councillor D. Wright",
      "Councillor K. Patel",
    ],
  },
  {
    motion_id: "MOT-2026-106",
    timestamp_start: 360.0,
    timestamp_end: 410.5,
    mover: "Councillor D. Wright",
    seconder: "Councillor K. Patel",
    motion_text: "That Council direct Administration to execute statutory public hearings pursuant to MGA Section 606 regarding Bylaw 24-09.",
    motion_type: "PROCEDURAL",
    outcome: "CARRIED",
    votes_for: [
      "Mayor E. Vance",
      "Councillor M. Henderson",
      "Councillor S. Thorne",
      "Councillor D. Wright",
      "Councillor K. Patel",
      "Councillor R. Kowalski",
      "Councillor A. Sterling",
    ],
    votes_against: [],
  },
  {
    motion_id: "MOT-2026-107",
    timestamp_start: 530.0,
    timestamp_end: 580.0,
    mover: "Councillor K. Patel",
    seconder: "Councillor M. Henderson",
    motion_text: "That Council grant First Reading to Bylaw 24-11 (Municipal Land Use District Rezoning - Parcel 4801).",
    motion_type: "MAIN",
    outcome: "PENDING",
    votes_for: [
      "Mayor E. Vance",
      "Councillor M. Henderson",
      "Councillor K. Patel",
    ],
    votes_against: [],
  },
];

export const MotionLiveFeed: React.FC<MotionLiveFeedProps> = ({
  onSelectMotion,
  externalMotions,
}) => {
  const [motions, setMotions] = useState<MotionItem[]>(externalMotions || INITIAL_MOCK_MOTIONS);
  const [filterStatus, setFilterStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  useEffect(() => {
    if (externalMotions && externalMotions.length > 0) {
      setMotions(externalMotions);
    }
  }, [externalMotions]);

  const filteredMotions = motions.filter((m) => {
    const matchesFilter = filterStatus === "ALL" || m.outcome === filterStatus;
    const matchesSearch =
      m.motion_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.mover.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.motion_id.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (outcome: MotionStatus) => {
    switch (outcome) {
      case "CARRIED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3.5 h-3.5" />
            CARRIED
          </span>
        );
      case "DEFEATED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3.5 h-3.5" />
            DEFEATED
          </span>
        );
      case "PENDING":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30 animate-pulse">
            <Clock className="w-3.5 h-3.5" />
            PENDING VOTE
          </span>
        );
      case "TABLED":
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-500/20 text-slate-300 border border-slate-500/30">
            <AlertTriangle className="w-3.5 h-3.5" />
            TABLED
          </span>
        );
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-xl backdrop-blur-md flex flex-col h-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-base font-semibold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Civic Motions & Roll-Call Registry
            <span className="px-2 py-0.5 text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full font-mono">
              {filteredMotions.length} Motions
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Autonomous extraction of parliamentary motions, movers, and roll-call votes
          </p>
        </div>

        {/* Filters and search */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-48">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search motions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-2.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 p-1 rounded-lg">
            <Filter className="w-3.5 h-3.5 text-slate-400 ml-1" />
            {(["ALL", "CARRIED", "DEFEATED", "PENDING"] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-2 py-0.5 text-xs rounded font-medium transition ${
                  filterStatus === status
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Motions List */}
      <div className="mt-4 space-y-3.5 overflow-y-auto pr-1 flex-1 max-h-[520px]">
        {filteredMotions.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-sm">
            No motions matching active filter criteria.
          </div>
        ) : (
          filteredMotions.map((motion) => (
            <div
              key={motion.motion_id}
              onClick={() => onSelectMotion?.(motion)}
              className="bg-slate-950/70 hover:bg-slate-950 border border-slate-800/80 hover:border-slate-700 rounded-xl p-4 transition cursor-pointer shadow-sm"
            >
              <div className="flex items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-indigo-300">
                    {motion.motion_id}
                  </span>
                  <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase bg-slate-800 text-slate-300 rounded border border-slate-700">
                    {motion.motion_type}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    [{formatTime(motion.timestamp_start)} - {formatTime(motion.timestamp_end)}]
                  </span>
                </div>

                {getStatusBadge(motion.outcome)}
              </div>

              {/* Motion Text Body */}
              <p className="text-sm text-slate-200 font-normal leading-relaxed mb-3">
                "{motion.motion_text}"
              </p>

              {/* Mover & Seconder */}
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-400 mb-3 pb-3 border-b border-slate-900">
                <span className="flex items-center gap-1.5">
                  <span className="text-slate-500">Mover:</span>
                  <strong className="text-slate-200 font-medium">{motion.mover}</strong>
                </span>
                {motion.seconder && (
                  <span className="flex items-center gap-1.5">
                    <span className="text-slate-500">Seconder:</span>
                    <strong className="text-slate-200 font-medium">{motion.seconder}</strong>
                  </span>
                )}
              </div>

              {/* Roll-call breakdown */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-slate-400 font-medium">
                    <Users className="w-3.5 h-3.5 text-slate-500" />
                    Roll-Call Division:
                  </span>
                  <div className="font-mono text-xs flex items-center gap-2">
                    <span className="text-emerald-400 font-semibold">
                      +{motion.votes_for.length} In Favor
                    </span>
                    <span className="text-slate-600">/</span>
                    <span className="text-rose-400 font-semibold">
                      -{motion.votes_against.length} Opposed
                    </span>
                  </div>
                </div>

                {/* Vote Chips */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {motion.votes_for.map((voter) => (
                    <span
                      key={voter}
                      className="px-2 py-0.5 rounded text-[11px] bg-emerald-950/40 text-emerald-300 border border-emerald-800/40"
                    >
                      ✓ {voter}
                    </span>
                  ))}
                  {motion.votes_against.map((voter) => (
                    <span
                      key={voter}
                      className="px-2 py-0.5 rounded text-[11px] bg-rose-950/40 text-rose-300 border border-rose-800/40"
                    >
                      ✗ {voter}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
