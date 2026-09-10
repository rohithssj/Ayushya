"use client";

import React, { useState, useEffect } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Chatbot } from "@/components/Chatbot/Chatbot";
import { useLanguage } from "@/i18n/LanguageContext";
import { getStoredAnalysis } from "@/services/analysisService";
import type { AnalysisApiResponse } from "@/features/rag/types/analysis_api";
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
} from "lucide-react";
import Link from "next/link";

export default function AnalysisResultsDashboard() {
  const params = useParams();
  const searchParams = useSearchParams();
  const { t } = useLanguage();

  const rawId = (params?.id as string) || "formulation";
  const urlJurisdiction = searchParams?.get("jurisdiction") || "India";
  const customName = searchParams?.get("name");
  const customCategory = searchParams?.get("category") || "Ayurveda-Aahar";

  const [analysisData, setAnalysisData] = useState<AnalysisApiResponse | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "ip" | "regulations" | "compliance" | "biodiversity" | "sources"
  >("overview");

  const [isChatOpen, setIsChatOpen] = useState(false);
  const [sourceTypeFilter, setSourceTypeFilter] = useState("All");
  const [sourceJurisdictionFilter, setSourceJurisdictionFilter] = useState("All");

  useEffect(() => {
    const stored = getStoredAnalysis(rawId);
    if (stored) {
      setAnalysisData(stored);
    }
  }, [rawId]);

  const productName = analysisData?.productName || customName || rawId
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
  const groundedAnswer = analysisData?.answer;

  const rawEvidence = analysisData?.evidence?.selected || [];

  const tabs = [
    { id: "overview", label: t("dashboard.tab.overview", "Overview"), icon: Layers },
    { id: "ip", label: t("dashboard.tab.ip", "IP Protection"), icon: ShieldCheck },
    { id: "regulations", label: t("dashboard.tab.regulations", "Regulations"), icon: FileText },
    { id: "compliance", label: t("dashboard.tab.compliance", "Compliance Checklist"), icon: CheckSquare },
    { id: "biodiversity", label: t("dashboard.tab.biodiversity", "Biodiversity & TK"), icon: Leaf },
    { id: "sources", label: `${t("dashboard.tab.sources", "Sources & Citations")} (${rawEvidence.length})`, icon: BookOpen },
  ];

  const filteredSources = rawEvidence.filter((ev) => {
    const cit = ev.citation;
    const typeMatch = sourceTypeFilter === "All" || (cit.domain && cit.domain.toLowerCase().includes(sourceTypeFilter.toLowerCase()));
    const jurMatch = sourceJurisdictionFilter === "All" || (cit.jurisdiction && cit.jurisdiction.toLowerCase() === sourceJurisdictionFilter.toLowerCase());
    return typeMatch && jurMatch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6 relative pb-32">
      {/* Dashboard Header */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/30 shadow-[0_0_40px_rgba(0,0,0,0.8)] backdrop-blur-xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-[#D4AF37]">
              <span>{t("dashboard.idLabel", "Analysis ID:")} #{analysisData?.id || rawId}</span>
              <span>•</span>
              <span className="flex items-center gap-1 bg-[#050806] px-2 py-0.5 rounded border border-[#D4AF37]/30">
                <Globe className="w-3.5 h-3.5 text-[#087F5B]" /> {jurisdiction} {t("dashboard.jurisdictionSuffix", "Jurisdiction")}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
              {productName}
            </h1>
            <p className="text-xs text-[#A8B5AC] font-mono">
              Classification: <strong className="text-[#D4AF37]">{category}</strong> ({form}) • {ingredients.length} Ingredients Listed
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3.5 py-1.5 rounded-full bg-[#0F1813] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-bold font-mono">
              Evidence Level:{" "}
              <strong className={evidenceStrength === "strong" ? "text-emerald-400" : evidenceStrength === "moderate" ? "text-yellow-400" : "text-amber-500"}>
                {evidenceStrength.toUpperCase()}
              </strong>
            </div>
            <div className="px-3.5 py-1.5 rounded-full bg-[#0F1813] text-[#A8B5AC] text-xs font-bold font-mono border border-[#D4AF37]/40">
              Citations: <strong className="text-[#D4AF37]">{rawEvidence.length} Grounded</strong>
            </div>
          </div>
        </div>

        {/* Abstention / Human Assistance Banner */}
        {abstained ? (
          <div className="p-4 rounded-2xl bg-amber-950/40 border border-amber-500/50 flex items-start gap-3 text-xs text-amber-200">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold uppercase tracking-wider font-mono">
                Authoritative Evidence Notice — Abstention Recommended
              </p>
              <p className="text-amber-300 font-sans">
                {analysisData?.abstention_reason || "AYUSHYA could not find sufficient authoritative statutory evidence for this specific formulation query in the ingested corpus."}
              </p>
              <div className="pt-2">
                <Link
                  href="/help"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#087F5B] text-white font-bold text-xs hover:scale-105 transition-all"
                >
                  <HelpCircle className="w-3.5 h-3.5" /> Request Human / Professional Review
                </Link>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-4 rounded-2xl bg-[#087F5B]/10 border border-[#D4AF37]/30 flex items-start gap-3 text-xs text-[#D4AF37]">
            <CheckCircle2 className="w-5 h-5 text-[#087F5B] shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-bold uppercase tracking-wider font-mono">
                AI Evidence-Grounded Legal Intelligence
              </p>
              <p className="text-[#A8B5AC] font-sans">
                The analysis below is grounded strictly in retrieved statutory provisions from Indian & International legal frameworks. This is decision-support intelligence, not a binding legal opinion.
              </p>
            </div>
          </div>
        )}

        {/* Dynamic Tab Bar */}
        <div className="flex items-center gap-1 border-b border-[#D4AF37]/20 pt-2 overflow-x-auto scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-bold rounded-t-xl transition-all border-b-2 whitespace-nowrap font-sans cursor-pointer ${
                  isActive
                    ? "border-[#D4AF37] bg-[#087F5B] text-white shadow-[0_0_15px_rgba(8,127,91,0.3)]"
                    : "border-transparent text-[#A8B5AC] hover:text-[#F4F8F5] hover:bg-white/5"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-[#D4AF37]" : "text-[#718078]"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Panels */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#0A100C]/90 border border-[#D4AF37]/20 shadow-2xl backdrop-blur-xl">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <div className="space-y-8 animate-fade-slide-in-1">
            {/* Top Stat Cards */}
            <div className="grid md:grid-cols-3 gap-6">
              {/* Card 1: Product Classification */}
              <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
                <span className="text-[11px] font-bold text-[#D4AF37] uppercase font-mono tracking-wider">
                  {t("dashboard.overview.classification", "Product Classification")}
                </span>
                <p className="text-xl font-bold text-[#F4F8F5]">{category}</p>
                <p className="text-xs text-[#A8B5AC]">Target regulatory framework: FSSAI / AYUSH Guidelines</p>
              </div>

              {/* Card 2: Real Evidence Level */}
              <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
                <div className="flex items-center justify-between text-[11px] font-bold font-mono">
                  <span className="text-[#D4AF37] uppercase tracking-wider">Evidence Strength</span>
                  <span className="text-[#D4AF37] uppercase">{evidenceStrength}</span>
                </div>
                <div className="w-full bg-[#0F1813] h-3 rounded-full overflow-hidden border border-[#D4AF37]/20">
                  <div
                    className={`h-full rounded-full ${
                      evidenceStrength === "strong"
                        ? "w-full bg-[#087F5B]"
                        : evidenceStrength === "moderate"
                        ? "w-2/3 bg-[#D4AF37]"
                        : "w-1/3 bg-amber-600"
                    }`}
                  />
                </div>
                <p className="text-xs text-[#A8B5AC] font-mono">
                  {rawEvidence.length} authoritative chunk(s) evaluated
                </p>
              </div>

              {/* Card 3: Key Legal Status */}
              <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
                <span className="text-[11px] font-bold text-[#D4AF37] uppercase font-mono tracking-wider">
                  Review Recommendation
                </span>
                <p className="text-lg font-bold text-[#D4AF37]">
                  {requiresHumanReview ? "Professional Review Recommended" : "Standard Legal Intelligence"}
                </p>
                <p className="text-xs text-[#A8B5AC]">
                  Based on Section 3(p) TK & Biodiversity provisions
                </p>
              </div>
            </div>

            {/* Grounded Legal Intelligence Summary */}
            <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
                  Executive Statutory & Intelligence Summary
                </h3>
                <span className="text-[10px] text-[#A8B5AC] font-mono border border-[#D4AF37]/30 px-2 py-0.5 rounded">
                  Grounded AI Intelligence
                </span>
              </div>
              <div className="text-sm text-[#F4F8F5] leading-relaxed whitespace-pre-wrap font-sans">
                {groundedAnswer ? (
                  groundedAnswer
                ) : abstained ? (
                  <p className="text-[#A8B5AC] italic">
                    AYUSHYA abstained from generating a legal conclusion because retrieved evidence is insufficient for binding claims. Please consult the &ldquo;Sources &amp; Citations&rdquo; tab or request human review.
                  </p>
                ) : (
                  <p className="text-[#A8B5AC]">
                    For <strong>{productName}</strong> evaluated under <strong>{jurisdiction}</strong> jurisdiction, classical herbs documented in Ayurvedic texts are categorized under Traditional Knowledge safeguards. Patenting requires proving synergistic bio-enhancement beyond mere admixture (Section 3e/3p). Commercialization must comply with statutory FSSAI and AYUSH licensing guidelines.
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
              <h3 className="text-lg font-bold text-[#F4F8F5]">Intellectual Property Protection Assessment</h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0F1813] px-2.5 py-1 rounded-full border border-[#D4AF37]/30">
                Statutory Intelligence
              </span>
            </div>
            <div className="grid gap-4">
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#D4AF37]">Patent Act, 1970 — Section 3(p) & 3(e) Exclusions</span>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/40">
                    Statutory Bar Check
                  </span>
                </div>
                <p className="text-xs text-[#A8B5AC] leading-relaxed">
                  Inventions which in effect are traditional knowledge or an aggregation or duplication of known properties of traditionally known component(s) are non-patentable under Section 3(p). Novel extraction processes or demonstrated synergistic formulations may be eligible subject to examination.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#D4AF37]">Trademark & Brand Identity (Trade Marks Act, 1999)</span>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/40">
                    Brand Protection
                  </span>
                </div>
                <p className="text-xs text-[#A8B5AC]">
                  Distinctive brand names for &ldquo;{productName}&rdquo; can be registered under Class 5 (Pharmaceuticals/ASU) or Class 30/29 (Ayurveda Aahar/Dietary). Generic botanical names are unregistrable as descriptive marks.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* REGULATIONS TAB */}
        {activeTab === "regulations" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <h3 className="text-lg font-bold text-[#F4F8F5]">Applicable Regulatory Frameworks</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <h4 className="font-bold text-sm text-[#D4AF37]">FSSAI — Ayurveda Aahar Regulations 2022</h4>
                <p className="text-xs text-[#A8B5AC]">
                  Applies if marketed as food/dietary supplement prepared according to authoritative Ayurvedic texts listed in Schedule A of FSSAI regulations.
                </p>
              </div>
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <h4 className="font-bold text-sm text-[#D4AF37]">Drugs & Cosmetics Rules 1945 — Rule 158B</h4>
                <p className="text-xs text-[#A8B5AC]">
                  Manufacturing license required from State AYUSH Licensing Authority if marketed with medicinal/therapeutic claims.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* COMPLIANCE TAB */}
        {activeTab === "compliance" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-lg font-bold text-[#F4F8F5]">Regulatory Compliance Checklist</h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0F1813] px-2.5 py-1 rounded-full border border-[#D4AF37]/30">
                Decision Support Checklist
              </span>
            </div>
            <div className="space-y-3">
              {[
                { title: `FSSAI / State AYUSH License for ${productName}`, status: "Statutory Requirement", icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "Ayurveda Aahar Official Logo & Mandatory Packaging Declaration", status: "Mandatory for Food", icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "National Biodiversity Authority (NBA) Form I / ABS Clearance", status: "Biological Resource Check", icon: AlertTriangle, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "TKDL Prior Art Verification (Patent Applications)", status: "Exclusion Defense", icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "Pharmacopoeial Monograph Standards (API Compliance)", status: "Quality Benchmark", icon: Clock, color: "text-[#A8B5AC] bg-[#050806]" },
              ].map((item, i) => {
                const Icon = item.icon;
                return (
                  <div key={i} className="flex items-center justify-between p-4 rounded-xl bg-[#050806] border border-[#D4AF37]/20 text-xs">
                    <div className="flex items-center gap-3">
                      <Icon className={`w-4 h-4 ${item.color}`} />
                      <span className="text-[#F4F8F5] font-medium">{item.title}</span>
                    </div>
                    <span className={`px-3 py-1 rounded-full font-bold text-[11px] border border-[#D4AF37]/30 ${item.color}`}>
                      {item.status}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* BIODIVERSITY TAB */}
        {activeTab === "biodiversity" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <h3 className="text-lg font-bold text-[#F4F8F5]">Biodiversity & Traditional Knowledge (TK) Analysis</h3>
            <p className="text-xs text-[#A8B5AC] leading-relaxed">
              Under the Biological Diversity Act, 2002 (and 2024 Rules), utilizing Indian biological resources for commercial utilization or applying for IP rights based on research on biological resources requires obtaining prior approval from the National Biodiversity Authority (NBA) and compliance with Access and Benefit Sharing (ABS) mechanisms.
            </p>
          </div>
        )}

        {/* SOURCES & CITATIONS TAB */}
        {activeTab === "sources" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className="text-lg font-bold text-[#F4F8F5]">
                Retrieved Statutory Evidence ({rawEvidence.length} Citations)
              </h3>

              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1 text-[#A8B5AC]">
                  <Filter className="w-3.5 h-3.5 text-[#D4AF37]" />
                  <span>Domain:</span>
                  <select
                    value={sourceTypeFilter}
                    onChange={(e) => setSourceTypeFilter(e.target.value)}
                    className="bg-[#050806] text-[#F4F8F5] border border-[#D4AF37]/30 rounded-lg px-2 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">All Domains</option>
                    <option value="patents">Patents</option>
                    <option value="biodiversity">Biodiversity</option>
                    <option value="ayurveda-aahar">Ayurveda Aahar</option>
                    <option value="drugs-cosmetics">Drugs & Cosmetics</option>
                    <option value="treaties">Treaties</option>
                  </select>
                </div>

                <div className="flex items-center gap-1 text-[#A8B5AC]">
                  <span>Jurisdiction:</span>
                  <select
                    value={sourceJurisdictionFilter}
                    onChange={(e) => setSourceJurisdictionFilter(e.target.value)}
                    className="bg-[#050806] text-[#F4F8F5] border border-[#D4AF37]/30 rounded-lg px-2 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">All Jurisdictions</option>
                    <option value="india">India</option>
                    <option value="international">International</option>
                  </select>
                </div>
              </div>
            </div>

            {filteredSources.length === 0 ? (
              <div className="p-8 text-center text-xs text-[#A8B5AC] bg-[#050806] rounded-2xl border border-[#D4AF37]/20">
                No statutory evidence chunks match the current filter.
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
                      className="p-4 rounded-xl bg-[#050806] border border-[#D4AF37]/20 hover:border-[#087F5B] text-xs transition-colors space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-bold text-[#F4F8F5] text-sm font-sans">{cit.title}</p>
                          <p className="text-[11px] text-[#D4AF37] font-mono mt-0.5">
                            {secStr || "Statutory Provision"} • Jurisdiction: {cit.jurisdiction} • Authority: {cit.authority || "Official Authority"}
                          </p>
                        </div>
                        {cit.source_url && (
                          <a
                            href={cit.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#A8B5AC] hover:text-[#D4AF37] p-1"
                            title="View Official Source"
                          >
                            <ExternalLink className="w-4 h-4 text-[#D4AF37]" />
                          </a>
                        )}
                      </div>

                      {ev.text && (
                        <div className="p-3 rounded-lg bg-[#0A100C] border border-[#D4AF37]/10 text-xs text-[#A8B5AC] font-mono leading-relaxed">
                          {ev.text.length > 300 ? `${ev.text.substring(0, 300)}...` : ev.text}
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
      <div className="fixed bottom-5 right-5 z-40">
        {!isChatOpen ? (
          <button
            onClick={() => setIsChatOpen(true)}
            className="btn-primary-glow flex items-center gap-2.5 px-5 py-3 rounded-full text-white font-bold text-sm shadow-2xl transition-all border border-[#D4AF37]/40 group cursor-pointer"
          >
            <Bot className="w-5 h-5 text-[#D4AF37] group-hover:rotate-12 transition-transform" />
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
