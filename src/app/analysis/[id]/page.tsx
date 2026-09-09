"use client";

import React, { useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { Chatbot } from "@/components/Chatbot/Chatbot";
import { useLanguage } from "@/i18n/LanguageContext";
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
} from "lucide-react";

export default function AnalysisResultsDashboard() {
  const params = useParams();
  const searchParams = useSearchParams();
  const { t } = useLanguage();

  // TODO: Replace query-based analysis data with backend analysis ID once /api/analyze is implemented.
  const rawId = (params?.id as string) || "ashwagandha-wellness";
  const jurisdiction = searchParams?.get("jurisdiction") || "India";
  const customName = searchParams?.get("name");
  const customCategory = searchParams?.get("category") || "Ayurveda-Aahar";

  const productName = customName
    ? customName
    : rawId
        .split("-")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");

  const [activeTab, setActiveTab] = useState<
    "overview" | "ip" | "regulations" | "compliance" | "biodiversity" | "sources"
  >("overview");

  const [isChatOpen, setIsChatOpen] = useState(false);

  const [sourceTypeFilter, setSourceTypeFilter] = useState("All");
  const [sourceJurisdictionFilter, setSourceJurisdictionFilter] = useState("All");

  const tabs = [
    { id: "overview", label: t("dashboard.tab.overview", "Overview"), icon: Layers },
    { id: "ip", label: t("dashboard.tab.ip", "IP Protection"), icon: ShieldCheck },
    { id: "regulations", label: t("dashboard.tab.regulations", "Regulations"), icon: FileText },
    { id: "compliance", label: t("dashboard.tab.compliance", "Compliance Checklist"), icon: CheckSquare },
    { id: "biodiversity", label: t("dashboard.tab.biodiversity", "Biodiversity & TK"), icon: Leaf },
    { id: "sources", label: t("dashboard.tab.sources", "Sources & Citations"), icon: BookOpen },
  ];

  const statutorySources = [
    { title: "The Patents Act, 1970 — Section 3(p)", type: "Law", jurisdiction: "India", section: "Section 3(p) Traditional Knowledge", link: "https://ipindia.gov.in" },
    { title: "The Patents Act, 1970 — Section 3(e)", type: "Law", jurisdiction: "India", section: "Section 3(e) Mere Admixture", link: "https://ipindia.gov.in" },
    { title: "Biological Diversity Act, 2002 — Section 3 & 6", type: "Law", jurisdiction: "India", section: "ABS Approval Mechanisms", link: "https://nbaindia.org" },
    { title: "FSSAI (Ayurveda Aahar) Regulations, 2022", type: "Regulation", jurisdiction: "India", section: "Regulation 4 & Schedule I", link: "https://www.fssai.gov.in" },
    { title: "Drugs and Cosmetics Rules, 1945 — Rule 158B", type: "Regulation", jurisdiction: "India", section: "ASU Drug Manufacturing License", link: "https://ayush.gov.in" },
    { title: "WIPO Nagoya Protocol Guidance on TK", type: "International", jurisdiction: "International", section: "Prior Informed Consent", link: "https://www.wipo.int" },
  ];

  const filteredSources = statutorySources.filter((s) => {
    const typeMatch = sourceTypeFilter === "All" || s.type === sourceTypeFilter;
    const jurMatch = sourceJurisdictionFilter === "All" || s.jurisdiction === sourceJurisdictionFilter;
    return typeMatch && jurMatch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6 relative pb-32">
      {/* Dashboard Header */}
      <div className="p-6 sm:p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/30 shadow-[0_0_40px_rgba(0,0,0,0.8)] backdrop-blur-xl space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-[#D4AF37]">
              <span>{t("dashboard.idLabel", "Analysis ID:")} #{rawId}</span>
              <span>•</span>
              <span className="flex items-center gap-1 bg-[#050806] px-2 py-0.5 rounded border border-[#D4AF37]/30">
                <Globe className="w-3.5 h-3.5 text-[#087F5B]" /> {jurisdiction} {t("dashboard.jurisdictionSuffix", "Jurisdiction")}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
              {productName}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-3.5 py-1.5 rounded-full bg-[#0F1813] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-bold font-mono">
              {t("dashboard.evidenceLevel", "Evidence Level:")} <strong className="text-[#A8B5AC]">{t("dashboard.evidenceDemo", "Pending backend retrieval")}</strong>
            </div>
            <div className="px-3.5 py-1.5 rounded-full bg-[#0F1813] text-[#A8B5AC] text-xs font-bold font-mono border border-[#D4AF37]/40">
              {t("dashboard.confidence", "AI RAG Confidence:")} <strong className="text-[#D4AF37]">{t("dashboard.confidenceDemo", "Not calculated (Demo)")}</strong>
            </div>
          </div>
        </div>

        {/* Prominent DEMO / MOCK Label Banner */}
        <div className="p-4 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-start gap-3 text-xs text-[#D4AF37]">
          <AlertTriangle className="w-5 h-5 text-[#D4AF37] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold uppercase tracking-wider font-mono">
              {t("dashboard.demoBannerTitle", "DEMO / MOCK — Not evidence-backed")}
            </p>
            <p className="text-[#A8B5AC] font-sans">
              {t(
                "dashboard.demoBannerDesc",
                "This dashboard displays sample mock results for UI evaluation. Findings, section references, and classifications have not been retrieved by the RAG backend and do not constitute legal advice."
              )}
            </p>
          </div>
        </div>

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
                <p className="text-xl font-bold text-[#F4F8F5]">{customCategory}</p>
                <p className="text-xs text-[#A8B5AC]">{t("dashboard.overview.regulatedUnder", "Regulated under FSSAI / AYUSH Guidelines")}</p>
              </div>

              {/* Card 2: Confidence Indicator Placeholder */}
              <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
                <div className="flex items-center justify-between text-[11px] font-bold font-mono">
                  <span className="text-[#D4AF37] uppercase tracking-wider">{t("dashboard.overview.confidenceLabel", "AI RAG Confidence")}</span>
                  <span className="text-[#D4AF37] font-sans">{t("dashboard.overview.confidenceNotCalc", "Not calculated (Demo)")}</span>
                </div>
                <div className="w-full bg-[#0F1813] h-3 rounded-full overflow-hidden border border-[#D4AF37]/20">
                  <div className="bg-gradient-to-r from-[#D4AF37]/20 via-[#087F5B]/30 to-[#D4AF37]/20 h-full rounded-full w-full opacity-60" />
                </div>
                <p className="text-xs text-[#A8B5AC]">{t("dashboard.overview.confidencePlaceholderDesc", "Score will be calculated from retrieved evidence when backend RAG is connected")}</p>
              </div>

              {/* Card 3: Key Legal Status Placeholder */}
              <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
                <span className="text-[11px] font-bold text-[#D4AF37] uppercase font-mono tracking-wider">
                  {t("dashboard.overview.patentability", "Patentability Assessment")}
                </span>
                <p className="text-lg font-bold text-[#D4AF37]">{t("dashboard.overview.section3pDemo", "Potentially applicable — Demo")}</p>
                <p className="text-xs text-[#A8B5AC]">{t("dashboard.overview.priorArtDemo", "Example result — Requires verification against TKDL")}</p>
              </div>
            </div>

            {/* Metric Overview Grid */}
            <div className="grid md:grid-cols-4 gap-4">
              {[
                { title: t("dashboard.metrics.ipTitle", "IP Rights"), status: t("dashboard.metrics.ipStatus", "Demo assessment"), color: "text-[#D4AF37]" },
                { title: t("dashboard.metrics.fssaiTitle", "FSSAI Status"), status: t("dashboard.metrics.fssaiStatus", "Potentially applicable — Demo"), color: "text-[#D4AF37]" },
                { title: t("dashboard.metrics.nbaTitle", "NBA Approval"), status: t("dashboard.metrics.nbaStatus", "Potentially applicable — Demo"), color: "text-[#D4AF37]" },
                { title: t("dashboard.metrics.tkdlTitle", "TKDL Prior Art"), status: t("dashboard.metrics.tkdlStatus", "Example result — Requires verification"), color: "text-[#D4AF37]" },
              ].map((m, i) => (
                <div key={i} className="p-4 rounded-xl bg-[#0F1813] border border-[#D4AF37]/20 space-y-1">
                  <span className="text-[10px] text-[#D4AF37] font-mono uppercase font-bold">{m.title}</span>
                  <p className={`text-xs font-bold ${m.color}`}>{m.status}</p>
                </div>
              ))}
            </div>

            {/* Intelligence Summary */}
            <div className="p-6 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
                  {t("dashboard.overview.executiveSummary", "Executive Legal Summary")}
                </h3>
                <span className="text-[10px] text-[#A8B5AC] font-mono border border-[#D4AF37]/30 px-2 py-0.5 rounded">
                  {t("dashboard.overview.demoBadge", "Demo Preview")}
                </span>
              </div>
              <p className="text-sm text-[#F4F8F5] leading-relaxed">
                <span className="text-[#D4AF37] font-semibold">[Demo Assessment]:</span> For <strong>{productName}</strong> evaluated under <strong>{jurisdiction}</strong> jurisdiction, {t("dashboard.overview.summaryBody", "classical herbs documented in Ayurvedic texts are categorized under Traditional Knowledge safeguards. Patenting requires proving synergistic bio-enhancement beyond mere admixture (Section 3e/3p). Commercialization must comply with statutory FSSAI and AYUSH licensing guidelines.")}
              </p>
            </div>
          </div>
        )}

        {/* IP TAB */}
        {activeTab === "ip" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-[#F4F8F5]">{t("dashboard.ip.title", "Intellectual Property Protection Assessment")}</h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0F1813] px-2.5 py-1 rounded-full border border-[#D4AF37]/30">
                {t("dashboard.demoBadge", "Demo Assessment")}
              </span>
            </div>
            <div className="grid gap-4">
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#D4AF37]">{t("dashboard.ip.trademarkTitle", "Trademark & Brand Identity Protection")}</span>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/40">
                    {t("dashboard.ip.trademarkDemoBadge", "Demo Assessment — Requires Verification")}
                  </span>
                </div>
                <p className="text-xs text-[#A8B5AC]">
                  {t("dashboard.ip.trademarkBodyDemo", "Preliminary sample assessment: Distinctive product name, logo, and trade dress may potentially be eligible for registration under the Trademarks Act, 1999, subject to trademark search.")}
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-[#D4AF37]">{t("dashboard.ip.sec3pTitle", "Section 3(p) Traditional Knowledge Consideration")}</span>
                  <span className="px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/40">
                    {t("dashboard.ip.sec3pDemoBadge", "Potentially applicable — Demo")}
                  </span>
                </div>
                <p className="text-xs text-[#A8B5AC]">
                  {t("dashboard.ip.sec3pBodyDemo", "Example assessment: Section 3(p) of the Patents Act 1970 may exclude traditional Ayurvedic formulations unless non-obvious synergistic efficacy is evidenced. Requires verification against TKDL.")}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* REGULATIONS TAB */}
        {activeTab === "regulations" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <h3 className="text-lg font-bold text-[#F4F8F5]">{t("dashboard.regulations.title", "Applicable Regulatory Frameworks")}</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <h4 className="font-bold text-sm text-[#D4AF37]">FSSAI — Ayurveda Aahar Regulations 2022</h4>
                <p className="text-xs text-[#A8B5AC]">
                  Complies with Food Safety and Standards (Ayurveda Aahar) Regulations, 2022. Labeling must carry official mandatory insignia.
                </p>
              </div>
              <div className="p-5 rounded-2xl bg-[#050806] border border-[#D4AF37]/20 space-y-2">
                <h4 className="font-bold text-sm text-[#D4AF37]">Ministry of AYUSH — Rule 158B</h4>
                <p className="text-xs text-[#A8B5AC]">
                  Manufacturing license under Drugs & Cosmetics Rules 1945 Rule 158B if marketed with therapeutic disease claims.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* COMPLIANCE TAB */}
        {activeTab === "compliance" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-lg font-bold text-[#F4F8F5]">{t("dashboard.compliance.title", "Regulatory Compliance Dashboard")}</h3>
              <span className="text-xs font-mono text-[#D4AF37] bg-[#0F1813] px-2.5 py-1 rounded-full border border-[#D4AF37]/30">
                {t("dashboard.compliance.demoNote", "Demo checklist — Not determined")}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#050806] border border-[#D4AF37]/20 text-xs text-[#A8B5AC]">
              {t("dashboard.compliance.banner", "Sample regulatory checklist items below illustrate the compliance schema. Actual status requires verification against applicable regulatory filings.")}
            </div>
            <div className="space-y-3">
              {[
                { title: `FSSAI Food Business License for ${productName} (Reg. 4)`, status: t("dashboard.compliance.demoStatus", "Not determined — Demo"), icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "Ayurveda Aahar Mandatory Packaging Insignia", status: t("dashboard.compliance.demoStatus", "Not determined — Demo"), icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "NBA Biological Resource Access Clearance (BD Act Sec 3)", status: t("dashboard.compliance.reviewDemo", "Requires verification — Demo"), icon: AlertTriangle, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "TKDL Prior Art Verification & Exclusion Check", status: t("dashboard.compliance.demoStatus", "Not determined — Demo"), icon: Clock, color: "text-[#D4AF37] bg-[#050806]" },
                { title: "Heavy Metal & Pesticide Residue Certificate (API Vol 1)", status: t("dashboard.compliance.demoStatus", "Not determined — Demo"), icon: Clock, color: "text-[#A8B5AC] bg-[#050806]" },
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
            <h3 className="text-lg font-bold text-[#F4F8F5]">{t("dashboard.biodiversity.title", "Biodiversity & Traditional Knowledge (TK) Analysis")}</h3>
            <p className="text-xs text-[#A8B5AC] leading-relaxed">
              {t("dashboard.biodiversity.body", "Because Indian biological resources are utilized in this formulation, applying for intellectual property rights or exporting commercial batches requires filing Form I with the National Biodiversity Authority (NBA) under the Biological Diversity Act, 2002.")}
            </p>
          </div>
        )}

        {/* SOURCES TAB */}
        {activeTab === "sources" && (
          <div className="space-y-6 animate-fade-slide-in-1">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className="text-lg font-bold text-[#F4F8F5]">{t("dashboard.sources.title", "Authoritative Statutory Source Database")}</h3>

              <div className="flex items-center gap-3 text-xs">
                <div className="flex items-center gap-1 text-[#A8B5AC]">
                  <Filter className="w-3.5 h-3.5 text-[#D4AF37]" />
                  <span>{t("dashboard.sources.filterType", "Type:")}</span>
                  <select
                    value={sourceTypeFilter}
                    onChange={(e) => setSourceTypeFilter(e.target.value)}
                    className="bg-[#050806] text-[#F4F8F5] border border-[#D4AF37]/30 rounded-lg px-2 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">{t("dashboard.sources.allTypes", "All Types")}</option>
                    <option value="Law">{t("dashboard.sources.law", "Law / Act")}</option>
                    <option value="Regulation">{t("dashboard.sources.regulation", "Regulation")}</option>
                    <option value="International">{t("dashboard.sources.international", "International")}</option>
                  </select>
                </div>

                <div className="flex items-center gap-1 text-[#A8B5AC]">
                  <span>{t("dashboard.sources.filterJurisdiction", "Jurisdiction:")}</span>
                  <select
                    value={sourceJurisdictionFilter}
                    onChange={(e) => setSourceJurisdictionFilter(e.target.value)}
                    className="bg-[#050806] text-[#F4F8F5] border border-[#D4AF37]/30 rounded-lg px-2 py-1 cursor-pointer font-sans"
                  >
                    <option value="All">{t("dashboard.sources.allJurisdictions", "All Jurisdictions")}</option>
                    <option value="India">India</option>
                    <option value="International">International</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Demo Sources Notice Banner */}
            <div className="p-4 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-start gap-3 text-xs text-[#D4AF37]">
              <AlertTriangle className="w-5 h-5 text-[#D4AF37] shrink-0 mt-0.5" />
              <div className="space-y-1">
                <p className="font-bold font-mono uppercase">
                  {t("dashboard.sources.demoNoticeTitle", "Demo sources — actual sources will be provided by the RAG backend.")}
                </p>
                <p className="text-[#A8B5AC] font-sans">
                  {t(
                    "dashboard.sources.demoNoticeDesc",
                    "The statutory entries below demonstrate the source catalog layout and citation card schema. They are not retrieved legal evidence for your specific formulation."
                  )}
                </p>
              </div>
            </div>

            <div className="grid gap-3">
              {filteredSources.map((s, idx) => (
                <a
                  key={idx}
                  href={s.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-4 rounded-xl bg-[#050806] border border-[#D4AF37]/20 hover:border-[#087F5B] text-xs text-[#D4AF37] font-mono transition-colors"
                >
                  <div>
                    <p className="font-bold text-[#F4F8F5] text-xs font-sans">{s.title}</p>
                    <p className="text-[11px] text-[#D4AF37] font-mono">{s.section} | Jurisdiction: {s.jurisdiction}</p>
                  </div>
                  <ExternalLink className="w-4 h-4 text-[#718078]" />
                </a>
              ))}
            </div>
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
            analysisId={rawId}
            productName={productName}
            jurisdiction={jurisdiction}
            onClose={() => setIsChatOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
