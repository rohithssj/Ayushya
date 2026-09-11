"use client";

import React, { useState, useEffect } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Chatbot } from "@/components/Chatbot/Chatbot";
import { useLanguage } from "@/i18n/LanguageContext";
import { getStoredAnalysis } from "@/services/analysisService";
import type {
  AnalysisApiResponse,
  IPAssessmentItem,
  RegulatoryAssessmentItem,
  ComplianceItem,
} from "@/features/rag/types/analysis_api";
import {
  FileText,
  ShieldCheck,
  CheckSquare,
  Globe,
  Bot,
  AlertTriangle,
  ExternalLink,
  BookOpen,
  Leaf,
  Layers,
  Filter,
  CheckCircle2,
  Clock,
  HelpCircle,
  Info,
  Scale,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";

// ---------------------------------------------------------------------------
// Helper: Evidence strength badge
// ---------------------------------------------------------------------------
function EvidenceBadge({ strength }: { strength: string }) {
  const color =
    strength === "strong"
      ? "text-emerald-400 border-emerald-500/40 bg-emerald-950/30"
      : strength === "moderate"
      ? "text-yellow-400 border-yellow-500/40 bg-yellow-950/30"
      : strength === "weak"
      ? "text-amber-400 border-amber-500/40 bg-amber-950/30"
      : "text-slate-400 border-slate-500/40 bg-slate-950/30";
  return (
    <span
      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase border ${color}`}
    >
      {strength}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Helper: Priority badge for compliance items
// ---------------------------------------------------------------------------
function PriorityBadge({ priority }: { priority: string }) {
  const color =
    priority === "high"
      ? "text-red-400 border-red-500/40 bg-red-950/30"
      : priority === "medium"
      ? "text-amber-400 border-amber-500/40 bg-amber-950/30"
      : "text-slate-400 border-slate-500/40 bg-slate-950/30";
  return (
    <span
      className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase border ${color}`}
    >
      {priority}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Helper: Insufficient evidence state
// ---------------------------------------------------------------------------
function InsufficientEvidenceState({ dimension }: { dimension: string }) {
  return (
    <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] flex items-start gap-3 text-xs text-[#A3B3A9]">
      <Info className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />
      <div className="space-y-1">
        <p className="font-bold text-[#F3E5AB] uppercase tracking-wider font-mono">
          Insufficient Evidence — {dimension}
        </p>
        <p>
          AYUSHYA could not establish sufficient authoritative evidence for this
          analysis dimension from the ingested corpus. Professional verification
          is recommended.
        </p>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export default function AnalysisResultsDashboard() {
  const params = useParams();
  const searchParams = useSearchParams();
  const { t } = useLanguage();

  const rawId = (params?.id as string) || "formulation";
  const urlJurisdiction = searchParams?.get("jurisdiction") || "India";
  const customName = searchParams?.get("name");
  const customCategory = searchParams?.get("category") || "Ayurveda-Aahar";

  const [analysisData, setAnalysisData] = useState<AnalysisApiResponse | null>(
    null
  );
  const [isLoaded, setIsLoaded] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "overview" | "ip" | "regulations" | "compliance" | "biodiversity" | "sources"
  >("overview");

  const [isChatOpen, setIsChatOpen] = useState(false);
  const [sourceTypeFilter, setSourceTypeFilter] = useState("All");
  const [sourceJurisdictionFilter, setSourceJurisdictionFilter] =
    useState("All");

  useEffect(() => {
    let stored = getStoredAnalysis(rawId);
    if (!stored && rawId !== "latest") {
      stored = getStoredAnalysis("latest");
    }
    if (stored) {
      setAnalysisData(stored);
    }
    setIsLoaded(true);
  }, [rawId]);

  if (!isLoaded) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <div className="w-12 h-12 mx-auto rounded-full border-2 border-[#D4AF37]/30 border-t-[#087F5B] animate-spin" />
        <p className="text-sm font-mono text-[#D4AF37]">Loading analysis data...</p>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 space-y-6 text-center">
        <div className="p-8 sm:p-10 rounded-3xl bg-[#080D0A]/90 border border-[rgba(212,175,55,0.3)] shadow-2xl space-y-6 backdrop-blur-2xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-amber-950/30 border border-amber-500/40 flex items-center justify-center text-amber-400">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl font-extrabold text-[#F4F8F5] font-display">Analysis Result Unavailable</h2>
            <p className="text-sm text-[#A3B3A9] max-w-md mx-auto font-sans">
              No analysis result for ID <code className="text-[#D4AF37] font-mono">#{rawId}</code> could be found in your current session.
            </p>
            <p className="text-xs text-[#6C7D73] max-w-md mx-auto font-sans">
              This can happen if you navigated directly to this link in a new browser tab or if session storage expired.
            </p>
          </div>
          <div className="pt-2 flex justify-center gap-4">
            <Link
              href="/analyze"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#087F5B] to-[#059669] hover:opacity-90 text-white font-bold text-xs transition-all shadow-lg font-sans"
            >
              ← Analyze Product Formulation
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const productName =
    analysisData?.productName ||
    customName ||
    rawId
      .split("-")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");

  const jurisdiction = analysisData?.jurisdiction || urlJurisdiction;
  const category = analysisData?.category || customCategory;
  const form = analysisData?.form || "Tablet";
  const ingredients = analysisData?.ingredients || [];

  const evidenceStrength = analysisData?.evidence_strength || "insufficient";
  const abstained = analysisData?.abstained ?? false;
  const requiresHumanReview = analysisData?.requires_human_review ?? true;

  // Use grounded_summary first, fall back to answer for backward compat
  const groundedAnswer = analysisData?.grounded_summary ?? analysisData?.answer;

  const rawEvidence = analysisData?.evidence?.selected || [];
  const domainsQueried = analysisData?.domains_queried || [];
  const queryCount = analysisData?.query_count || 0;

  // Structured fields from real API
  const classification = analysisData?.classification;
  const ipAssessment = analysisData?.ip_assessment || [];
  const regulatoryAssessment = analysisData?.regulatory_assessment || [];
  const tkBiodiversity = analysisData?.tk_biodiversity;
  const complianceChecklist = analysisData?.compliance_checklist || [];

  const tabs = [
    {
      id: "overview",
      label: t("dashboard.tab.overview", "Overview"),
      icon: Layers,
    },
    {
      id: "ip",
      label: t("dashboard.tab.ip", "IP Protection"),
      icon: ShieldCheck,
    },
    {
      id: "regulations",
      label: t("dashboard.tab.regulations", "Regulations"),
      icon: FileText,
    },
    {
      id: "compliance",
      label: t("dashboard.tab.compliance", "Compliance Checklist"),
      icon: CheckSquare,
    },
    {
      id: "biodiversity",
      label: t("dashboard.tab.biodiversity", "Biodiversity & TK"),
      icon: Leaf,
    },
    {
      id: "sources",
      label: `${t("dashboard.tab.sources", "Sources & Citations")} (${rawEvidence.length})`,
      icon: BookOpen,
    },
  ];

  const filteredSources = rawEvidence.filter((ev) => {
    const cit = ev.citation;
    const typeMatch =
      sourceTypeFilter === "All" ||
      (cit.domain &&
        cit.domain.toLowerCase().includes(sourceTypeFilter.toLowerCase()));
    const jurMatch =
      sourceJurisdictionFilter === "All" ||
      (cit.jurisdiction &&
        cit.jurisdiction.toLowerCase() ===
          sourceJurisdictionFilter.toLowerCase());
    return typeMatch && jurMatch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-8 relative pb-36">
      {/* Background ambient light */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#087F5B]/10 blur-[130px] pointer-events-none -z-10" />

      {/* Dashboard Header Container */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#080D0A]/90 border border-[rgba(212,175,55,0.22)] shadow-2xl backdrop-blur-2xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5 text-xs font-mono text-[#D4AF37]">
              <span className="bg-[#0D1611] px-2.5 py-1 rounded-full border border-[#D4AF37]/30">
                {t("dashboard.idLabel", "Analysis ID:")} #{analysisData?.id || rawId}
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 bg-[#0D1611] px-2.5 py-1 rounded-full border border-[#D4AF37]/30 text-[#F4F8F5]">
                <Globe className="w-3.5 h-3.5 text-[#10B981]" />
                <span>{jurisdiction} {t("dashboard.jurisdictionSuffix", "Jurisdiction")}</span>
              </span>
              {domainsQueried.length > 0 && (
                <span className="text-[#6C7D73]">
                  {queryCount} targeted queries
                </span>
              )}
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
              {productName}
            </h1>
            <p className="text-xs text-[#A3B3A9] font-mono">
              {classification ? (
                <>
                  User-selected classification:{" "}
                  <strong className="text-[#F3E5AB]">
                    {classification.user_selected}
                  </strong>{" "}
                  <span className="text-[#6C7D73]">
                    (preliminary, subject to verification)
                  </span>{" "}
                  • {form} • {ingredients.length} Ingredients Listed
                </>
              ) : (
                <>
                  Classification:{" "}
                  <strong className="text-[#F3E5AB]">{category}</strong> (
                  {form}) • {ingredients.length} Ingredients Listed
                </>
              )}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="px-3.5 py-1.5 rounded-full bg-[#0D1611] border border-[#D4AF37]/30 text-xs font-bold font-mono text-[#D4AF37]">
              {t("dashboard.evidenceLevel", "Evidence Level:")}{" "}
              <strong className={evidenceStrength === "strong" ? "text-emerald-400" : evidenceStrength === "moderate" ? "text-yellow-400" : "text-amber-500"}>
                {evidenceStrength.toUpperCase()}
              </strong>
            </div>
            <div className="px-3.5 py-1.5 rounded-full bg-[#0D1611] text-[#A3B3A9] text-xs font-bold font-mono border border-[#D4AF37]/30">
              Citations: <strong className="text-[#D4AF37]">{rawEvidence.length} Grounded</strong>
            </div>
          </div>
        </div>

        {/* Abstention / Grounded Banner */}
        {abstained ? (
          <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-500/50 flex items-start gap-3 text-xs text-amber-200">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold uppercase tracking-wider font-mono">
                Authoritative Evidence Notice — Abstention Recommended
              </p>
              <p className="text-amber-300 font-sans">
                {analysisData?.abstention_reason ||
                  "AYUSHYA could not find sufficient authoritative statutory evidence for this specific formulation query in the ingested corpus."}
              </p>
              <div className="pt-2">
                <Link
                  href="/help"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#087F5B] text-white font-bold text-xs hover:scale-105 transition-all shadow-sm"
                >
                  <HelpCircle className="w-3.5 h-3.5" /> Request Human /
                  Professional Review
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-2xl bg-[#087F5B]/10 border border-[#D4AF37]/30 flex items-start gap-3 text-xs text-[#D4AF37]">
            <CheckCircle2 className="w-5 h-5 text-[#10B981] shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold uppercase tracking-wider font-mono text-[#F3E5AB]">
                AI Evidence-Grounded Legal Intelligence
              </p>
              <p className="text-[#A3B3A9] font-sans leading-relaxed">
                The analysis below is grounded strictly in retrieved statutory provisions from Indian & International legal frameworks. This is <strong>preliminary decision-support intelligence</strong>, not a binding legal opinion. All classifications and assessments are subject to verification.
              </p>
            </div>
          </div>
        )}

        {/* Human Review Banner */}
        {requiresHumanReview && !abstained && (
          <div className="p-3 rounded-xl bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-center gap-3 text-xs text-[#D4AF37]">
            <AlertCircle className="w-4 h-4 text-[#D4AF37] shrink-0" />
            <span>
              <strong>Professional Review Recommended:</strong> Evidence
              strength or classification uncertainty warrants consultation with a
              qualified IP attorney, regulatory consultant, or AYUSH facilitator.
            </span>
            <Link
              href="/help"
              className="ml-auto shrink-0 px-3.5 py-1.5 rounded-xl bg-[#087F5B] text-white font-bold text-xs hover:scale-105 transition-all shadow-sm"
            >
              Get Review
            </Link>
          </div>
        )}

        {/* Dynamic Modern Tab Bar */}
        <div className="flex items-center gap-1.5 border-b border-[rgba(212,175,55,0.18)] pt-2 overflow-x-auto scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-bold rounded-t-xl transition-all border-b-2 whitespace-nowrap cursor-pointer ${
                  isActive
                    ? "border-[#D4AF37] bg-gradient-to-r from-[#087F5B] to-[#059669] text-white shadow-[0_2px_15px_rgba(8,127,91,0.4)]"
                    : "border-transparent text-[#A3B3A9] hover:text-[#F4F8F5] hover:bg-white/[0.04]"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#F3E5AB]" : "text-[#6C7D73]"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Panels */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#080D0A]/90 border border-[rgba(212,175,55,0.2)] shadow-2xl backdrop-blur-2xl">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-8 animate-fade-slide-in-1">
            {/* Stat Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Card 1: Preliminary Classification */}
              <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-3 shadow-sm">
                <span className="text-[11px] font-bold text-[#F3E5AB] uppercase font-mono tracking-wider">
                  {t("dashboard.overview.classification", "Preliminary Classification")}
                </span>
                <p className="text-xl font-bold text-[#F4F8F5] font-display">
                  {classification?.user_selected || category}
                </p>
                <p className="text-xs text-amber-400 font-mono">
                  ⚠ Preliminary — subject to verification
                </p>
                {classification?.evidence_strength && (
                  <EvidenceBadge strength={classification.evidence_strength} />
                )}
              </div>

              {/* Card 2: Real Evidence Level */}
              <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-3 shadow-sm">
                <div className="flex items-center justify-between text-[11px] font-bold font-mono">
                  <span className="text-[#F3E5AB] uppercase tracking-wider">Evidence Strength</span>
                  <span className="text-[#D4AF37] uppercase">{evidenceStrength}</span>
                </div>
                <div className="w-full bg-[#0D1611] h-2.5 rounded-full overflow-hidden border border-[#D4AF37]/20">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      evidenceStrength === "strong"
                        ? "w-full bg-gradient-to-r from-[#087F5B] to-[#10B981]"
                        : evidenceStrength === "moderate"
                        ? "w-2/3 bg-[#D4AF37]"
                        : "w-1/3 bg-amber-600"
                    }`}
                  />
                </div>
                <p className="text-xs text-[#A3B3A9] font-mono">
                  {rawEvidence.length} authoritative chunk(s) evaluated
                </p>
                {domainsQueried.length > 0 && (
                  <p className="text-[10px] text-[#6C7D73] font-mono">
                    Domains: {domainsQueried.join(", ")}
                  </p>
                )}
              </div>

              {/* Card 3: Key Review Recommendation */}
              <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-2.5 shadow-sm">
                <span className="text-[11px] font-bold text-[#F3E5AB] uppercase font-mono tracking-wider">
                  Review Recommendation
                </span>
                <p className="text-lg font-bold text-[#D4AF37] font-display">
                  {requiresHumanReview ? "Professional Review Recommended" : "Standard Legal Intelligence"}
                </p>
                <p className="text-xs text-[#A3B3A9]">
                  Based on evidence strength and classification uncertainty
                </p>
              </div>
            </div>

            {/* Preliminary Classification Assessment Card */}
            {classification && (
              <div className="p-6 rounded-2xl bg-[#040705] border border-amber-500/20 space-y-3 shadow-md">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider font-mono">
                    Preliminary Classification Assessment
                  </h3>
                  <span className="text-[10px] text-[#A3B3A9] font-mono border border-amber-500/30 px-2 py-0.5 rounded">
                    ⚠ Not an Official Determination
                  </span>
                </div>
                <p className="text-sm text-[#F4F8F5] leading-relaxed font-sans">
                  {classification.preliminary_assessment}
                </p>
                <p className="text-xs text-[#6C7D73] font-mono">
                  User-selected:{" "}
                  <strong className="text-[#D4AF37]">
                    {classification.user_selected}
                  </strong>{" "}
                  • Evidence:{" "}
                  <EvidenceBadge strength={classification.evidence_strength} />
                  {classification.requires_verification && (
                    <span className="ml-2 text-amber-400">
                      • Verification required
                    </span>
                  )}
                </p>
              </div>
            )}

            {/* Grounded Legal Intelligence Summary */}
            <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-3 shadow-md">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-[#F3E5AB] uppercase tracking-wider font-mono flex items-center gap-2">
                  <Scale className="w-4 h-4 text-[#10B981]" />
                  <span>Executive Statutory & Intelligence Summary</span>
                </h3>
                <span className="text-[10px] text-[#A3B3A9] font-mono border border-[#D4AF37]/30 px-2.5 py-0.5 rounded-full bg-[#0D1611]">
                  Evidence-Grounded · Preliminary
                </span>
              </div>
              <div className="text-sm text-[#F4F8F5] leading-relaxed whitespace-pre-wrap font-sans">
                {groundedAnswer ? (
                  groundedAnswer
                ) : abstained ? (
                  <p className="text-[#A3B3A9] italic">
                    AYUSHYA abstained from generating a legal conclusion because retrieved evidence is insufficient for binding claims. Please consult the &ldquo;Sources &amp; Citations&rdquo; tab or request human review.
                  </p>
                ) : (
                  <p className="text-[#A3B3A9]">
                    No grounded analysis available.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* IP TAB */}
        {activeTab === "ip" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-[#F4F8F5] font-display">
                Intellectual Property Protection Assessment
              </h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0D1611] px-3 py-1 rounded-full border border-[#D4AF37]/35">
                Preliminary · Evidence-Backed
              </span>
            </div>

            {ipAssessment.length > 0 ? (
              <div className="grid gap-4">
                {ipAssessment.map((item: IPAssessmentItem, idx: number) => (
                  <div
                    key={idx}
                    className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-3 shadow-md"
                  >
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <span className="font-bold text-sm text-[#F3E5AB]">
                        {item.ip_type}
                      </span>
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[11px] font-bold border font-mono ${
                            item.relevance === "potentially_relevant"
                              ? "bg-[#0D1611] text-emerald-400 border-emerald-500/30"
                              : item.relevance === "low_relevance"
                              ? "bg-[#0D1611] text-amber-400 border-amber-500/30"
                              : "bg-[#0D1611] text-slate-400 border-slate-500/30"
                          }`}
                        >
                          {item.relevance.replace(/_/g, " ")}
                        </span>
                        <EvidenceBadge strength={item.evidence_strength} />
                        {item.requires_verification && (
                          <span className="px-2.5 py-1 rounded-full text-[11px] font-bold border font-mono bg-amber-950/20 text-amber-300 border-amber-500/30">
                            verification required
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-[#F4F8F5] leading-relaxed font-sans">
                      <strong>Preliminary Assessment: </strong>
                      {item.preliminary_assessment}
                    </p>
                    {item.reasoning && (
                      <p className="text-xs text-[#A3B3A9] leading-relaxed font-sans">
                        <em>Reasoning: </em>
                        {item.reasoning}
                      </p>
                    )}
                    {item.supporting_citation_ids.length > 0 && (
                      <p className="text-[10px] text-[#6C7D73] font-mono">
                        Evidence: {item.supporting_citation_ids.join(", ")}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <InsufficientEvidenceState dimension="IP Protection" />
            )}

            {/* Always show the preliminary disclaimer */}
            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 font-sans">
              <strong>Preliminary AI Notice:</strong> IP assessments above are
              preliminary and evidence-based. They do not constitute legal
              advice, a guarantee of IP registration, or a formal legal opinion.
              Consult a registered patent attorney or IP professional for
              binding determinations.
            </div>
          </div>
        )}

        {/* REGULATIONS TAB */}
        {activeTab === "regulations" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <h3 className="text-lg font-bold text-[#F4F8F5] font-display">
              Applicable Regulatory Frameworks
            </h3>
            <p className="text-xs text-[#A3B3A9]">
              The frameworks listed below are{" "}
              <strong>potentially applicable</strong> based on retrieved
              evidence. This is not a compliance determination.
            </p>

            {regulatoryAssessment.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-5">
                {regulatoryAssessment.map(
                  (item: RegulatoryAssessmentItem, idx: number) => (
                    <div
                      key={idx}
                      className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-2.5 shadow-md"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-bold text-sm text-[#F3E5AB]">
                          {item.framework}
                        </h4>
                        <EvidenceBadge strength={item.evidence_strength} />
                      </div>
                      {item.requires_verification && (
                        <p className="text-[10px] text-amber-300 font-mono uppercase">
                          Preliminary assessment — verification required
                        </p>
                      )}
                      <p className="text-xs text-[#A3B3A9] leading-relaxed">
                        <em>Why potentially applicable: </em>
                        {item.why_applicable}
                      </p>
                      {item.relevant_provisions.length > 0 && (
                        <ul className="list-disc list-inside space-y-1">
                          {item.relevant_provisions.map((prov, pi) => (
                            <li
                              key={pi}
                              className="text-xs text-[#F4F8F5] leading-relaxed"
                            >
                              {prov}
                            </li>
                          ))}
                        </ul>
                      )}
                      {item.supporting_citation_ids.length > 0 && (
                        <p className="text-[10px] text-[#6C7D73] font-mono">
                          Evidence: {item.supporting_citation_ids.join(", ")}
                        </p>
                      )}
                    </div>
                  )
                )}
              </div>
            ) : (
              <InsufficientEvidenceState dimension="Regulatory Frameworks" />
            )}

            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 font-sans">
              <strong>Preliminary AI Notice:</strong> Regulatory assessments are
              based on retrieved statutory evidence and are preliminary. Product
              classification, licensing requirements, and compliance
              determinations must be verified with the appropriate regulatory
              authority (FSSAI, CDSCO, State AYUSH Licensing Authority, etc.).
            </div>
          </div>
        )}

        {/* COMPLIANCE TAB */}
        {activeTab === "compliance" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-lg font-bold text-[#F4F8F5] font-display">
                Preliminary Compliance Checklist
              </h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0D1611] px-3 py-1 rounded-full border border-[#D4AF37]/30">
                Decision Support Checklist
              </span>
            </div>
            <p className="text-xs text-[#A3B3A9]">
              Checklist items are derived from retrieved statutory evidence.
              Items not supported by evidence are not included.
            </p>

            {complianceChecklist.length > 0 ? (
              <div className="space-y-3">
                {complianceChecklist.map(
                  (item: ComplianceItem, idx: number) => (
                    <div
                      key={idx}
                      className="p-4.5 rounded-xl bg-[#040705] border border-[rgba(212,175,55,0.18)] hover:border-[#D4AF37]/40 text-xs space-y-2 transition-colors shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <PriorityBadge priority={item.priority} />
                          <span className="text-[#F4F8F5] font-medium">
                            {item.action}
                          </span>
                        </div>
                        <span className="shrink-0 px-2.5 py-0.5 rounded-full text-[10px] font-mono text-[#10B981] border border-[#10B981]/30 bg-[#10B981]/10">
                          {item.legal_area}
                        </span>
                      </div>
                      {item.requires_verification && (
                        <p className="text-[10px] text-amber-300 font-mono pl-12 uppercase">
                          Preliminary checklist item — verification required
                        </p>
                      )}
                      <p className="text-[#A3B3A9] text-xs pl-12 leading-relaxed">
                        {item.reason}
                      </p>
                      {item.supporting_citation_id && (
                        <p className="text-[10px] text-[#6C7D73] font-mono pl-12">
                          Evidence: {item.supporting_citation_id}
                        </p>
                      )}
                    </div>
                  )
                )}
              </div>
            ) : (
              <InsufficientEvidenceState dimension="Compliance Checklist" />
            )}

            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 font-sans">
              <strong>Preliminary AI Notice:</strong> This checklist is for
              orientation only. Specific licensing, approval, or compliance
              requirements must be confirmed with the relevant regulatory
              authority before commercialisation.
            </div>
          </div>
        )}

        {/* BIODIVERSITY & TK TAB */}
        {activeTab === "biodiversity" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <h3 className="text-lg font-bold text-[#F4F8F5] font-display">
              Biodiversity & Traditional Knowledge Considerations
            </h3>

            {tkBiodiversity ? (
              <>
                {tkBiodiversity.insufficient ? (
                  <InsufficientEvidenceState dimension="Biodiversity & TK" />
                ) : (
                  <div className="space-y-4">
                    {/* TK Considerations */}
                    <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-2.5 shadow-md">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-sm text-[#F3E5AB]">
                          Traditional Knowledge Considerations
                        </h4>
                        <EvidenceBadge
                          strength={tkBiodiversity.evidence_strength}
                        />
                      </div>
                      {tkBiodiversity.requires_verification && (
                        <p className="text-[10px] text-amber-300 font-mono uppercase">
                          Preliminary assessment — verification required
                        </p>
                      )}
                      <p className="text-xs text-[#A3B3A9] leading-relaxed font-sans">
                        {tkBiodiversity.tk_considerations}
                      </p>
                    </div>

                    {/* Biodiversity Considerations */}
                    <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-2.5 shadow-md">
                      <h4 className="font-bold text-sm text-[#F3E5AB]">
                        Biological Diversity Act Considerations
                      </h4>
                      <p className="text-xs text-[#A3B3A9] leading-relaxed font-sans">
                        {tkBiodiversity.biodiversity_considerations}
                      </p>
                    </div>

                    {/* ABS Note */}
                    {tkBiodiversity.abs_note && (
                      <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-2.5 shadow-md">
                        <h4 className="font-bold text-sm text-[#F3E5AB]">
                          Access and Benefit Sharing (ABS) Note
                        </h4>
                        <p className="text-xs text-[#A3B3A9] leading-relaxed font-sans">
                          {tkBiodiversity.abs_note}
                        </p>
                      </div>
                    )}

                    {tkBiodiversity.supporting_citation_ids.length > 0 && (
                      <p className="text-[10px] text-[#6C7D73] font-mono">
                        Evidence:{" "}
                        {tkBiodiversity.supporting_citation_ids.join(", ")}
                      </p>
                    )}
                  </div>
                )}
              </>
            ) : (
              <>
                {/* Fallback: show general note when no structured TK data */}
                <div className="p-6 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.2)] space-y-3 shadow-md">
                  <p className="text-xs text-[#A3B3A9] leading-relaxed font-sans">
                    AYUSHYA queries biodiversity and traditional knowledge
                    dimensions when ingredients suggest use of Indian biological
                    resources. Specific ABS and TK evidence was{" "}
                    {abstained
                      ? "not evaluated due to overall evidence insufficiency"
                      : "not surfaced with sufficient strength from the ingested corpus for this formulation"}
                    . Consult an IP/ABS professional for detailed guidance.
                  </p>
                </div>
              </>
            )}

            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300 font-sans">
              <strong>Preliminary AI Notice:</strong> TK and biodiversity
              assessments are based strictly on retrieved evidence. AYUSHYA does
              not verify TKDL entries, confirm ABS approval requirements, or
              make binding biodiversity law determinations. Consult the National
              Biodiversity Authority (NBA) and a qualified IP/ABS advisor.
            </div>
          </div>
        )}

        {/* SOURCES & CITATIONS TAB */}
        {activeTab === "sources" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className="text-lg font-bold text-[#F4F8F5] font-display">
                Retrieved Statutory Evidence ({rawEvidence.length} Citations)
              </h3>

              <div className="flex flex-wrap items-center gap-3 text-xs">
                <div className="flex items-center gap-1.5 text-[#A3B3A9]">
                  <Filter className="w-3.5 h-3.5 text-[#10B981]" />
                  <span>Domain:</span>
                  <select
                    value={sourceTypeFilter}
                    onChange={(e) => setSourceTypeFilter(e.target.value)}
                    className="bg-[#040705] text-[#F4F8F5] border border-[rgba(212,175,55,0.25)] rounded-lg px-2.5 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">All Domains</option>
                    <option value="patents">Patents</option>
                    <option value="biodiversity">Biodiversity</option>
                    <option value="ayurveda-aahar">Ayurveda Aahar</option>
                    <option value="drugs-cosmetics">Drugs & Cosmetics</option>
                    <option value="trademarks">Trademarks</option>
                    <option value="treaties">Treaties</option>
                    <option value="gi">GI</option>
                  </select>
                </div>

                <div className="flex items-center gap-1.5 text-[#A3B3A9]">
                  <span>Jurisdiction:</span>
                  <select
                    value={sourceJurisdictionFilter}
                    onChange={(e) => setSourceJurisdictionFilter(e.target.value)}
                    className="bg-[#040705] text-[#F4F8F5] border border-[rgba(212,175,55,0.25)] rounded-lg px-2.5 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">All Jurisdictions</option>
                    <option value="india">India</option>
                    <option value="international">International</option>
                  </select>
                </div>
              </div>
            </div>

            {filteredSources.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#A3B3A9] bg-[#040705] rounded-2xl border border-[rgba(212,175,55,0.2)]">
                {rawEvidence.length === 0
                  ? "No statutory evidence was retrieved for this analysis."
                  : "No statutory evidence chunks match the current filter."}
              </div>
            ) : (
              <div className="grid gap-3">
                {filteredSources.map((ev, idx) => {
                  const cit = ev.citation;
                  const parts: string[] = [];
                  if (cit.section) parts.push(cit.section);
                  if (cit.section_title) parts.push(cit.section_title);
                  if (cit.subsection) parts.push(`(${cit.subsection})`);
                  if (cit.chapter) parts.push(`[${cit.chapter}]`);
                  if (cit.page_start) parts.push(`p. ${cit.page_start}`);
                  const secStr = parts.join(" — ");

                  return (
                    <div
                      key={idx}
                      className="p-5 rounded-2xl bg-[#040705] border border-[rgba(212,175,55,0.18)] hover:border-[#10B981] text-xs transition-colors space-y-3 shadow-md group"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-bold text-[#F4F8F5] text-sm font-sans group-hover:text-[#F3E5AB] transition-colors">
                            {cit.title}
                          </p>
                          <p className="text-[11px] text-[#D4AF37] font-mono mt-0.5">
                            {secStr || "Statutory Provision"} • Jurisdiction:{" "}
                            {cit.jurisdiction} • Authority:{" "}
                            {cit.authority || "Official Authority"}
                          </p>
                          <p className="text-[10px] text-[#6C7D73] font-mono mt-0.5">
                            ID: {cit.citation_id}
                            {cit.domain && ` • Domain: ${cit.domain}`}
                          </p>
                        </div>
                        {cit.source_url && (
                          <a
                            href={cit.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#6C7D73] group-hover:text-[#10B981] group-hover:translate-x-0.5 transition-all p-1"
                            title="View Official Source"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>

                      {ev.text && (
                        <div className="p-3.5 rounded-xl bg-[#090F0B] border border-white/[0.06] text-xs text-[#A3B3A9] font-mono leading-relaxed">
                          {ev.text.length > 300
                            ? `${ev.text.substring(0, 300)}...`
                            : ev.text}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Floating Ask AYUSHYA Button on Bottom-Right */}
      <div className="fixed bottom-6 right-6 z-40">
        {!isChatOpen ? (
          <button
            onClick={() => setIsChatOpen(true)}
            className="btn-primary-glow flex items-center gap-2.5 px-5 py-3 rounded-full text-white font-bold text-sm shadow-2xl transition-all border border-[#D4AF37]/45 group cursor-pointer"
          >
            <Bot className="w-5 h-5 text-[#F3E5AB] group-hover:rotate-12 transition-transform" />
            <span>🤖 {t("chat.openBtn", "Ask AYUSHYA")}</span>
          </button>
        ) : (
          <Chatbot
            mode="floating"
            analysisId={analysisData?.id || rawId}
            productName={productName}
            jurisdiction={jurisdiction}
            onClose={() => setIsChatOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
