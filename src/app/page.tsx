"use client";

import React from "react";
import Link from "next/link";
import {
  Shield,
  Bot,
  ArrowRight,
  Sparkles,
  BookOpen,
  Leaf,
  Layers,
  Globe,
  FileText,
  CheckCircle2,
  Star,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export default function Home() {
  const { t } = useLanguage();

  return (
    <main className="min-h-screen w-full text-[#F4F8F5] relative overflow-hidden">

      {/* ─── HERO SECTION with background image ─── */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">

        {/* Background Image */}
        <div className="absolute inset-0 hero-bg" aria-hidden="true" />

        {/* Dark overlay gradient for readability */}
        <div className="absolute inset-0 hero-overlay" aria-hidden="true" />

        {/* Fine grid pattern on top */}
        <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center py-32 space-y-8 animate-fade-slide-in-1">


          {/* Main Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.12] font-sans">
            <span className="text-[#F4F8F5] drop-shadow-[0_2px_20px_rgba(0,0,0,0.8)]">
              {t("home.hero.title1", "AI-Powered")}
            </span>{" "}
            <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#087F5B] via-[#0CA678] to-[#D4AF37] drop-shadow-[0_0_30px_rgba(8,127,91,0.5)]">
              {t("home.hero.title2", "IP & Regulatory")}
            </span>{" "}
            <br className="hidden sm:block" />
            <span className="text-[#F4F8F5] drop-shadow-[0_2px_20px_rgba(0,0,0,0.8)]">
              {t("home.hero.title3", "Intelligence for Ayurveda")}
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-[#C8D5CC] max-w-2xl mx-auto leading-relaxed font-normal drop-shadow-[0_1px_8px_rgba(0,0,0,0.9)]">
            {t(
              "home.hero.description",
              "Understand intellectual property protections, traditional knowledge exclusions (Section 3p), FSSAI regulations, and biodiversity obligations with evidence-backed legal AI."
            )}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
            <Link
              href="/analyze"
              id="hero-analyze-btn"
              className="btn-primary-glow animate-pulse-glow inline-flex items-center justify-center gap-2.5 px-9 py-4 rounded-full text-sm font-bold tracking-wide text-white shadow-xl min-w-[220px]"
            >
              <span>{t("home.hero.analyzeBtn", "Analyze Your Product")}</span>
              <ArrowRight className="w-4 h-4 text-[#D4AF37]" />
            </Link>
            <Link
              href="/assistant"
              id="hero-assistant-btn"
              className="btn-gold-outline inline-flex items-center justify-center gap-2 px-9 py-4 rounded-full text-sm font-semibold transition-all min-w-[220px] backdrop-blur-sm"
            >
              <Bot className="w-4 h-4 text-[#087F5B]" />
              <span>{t("home.hero.askBtn", "Ask AYUSHYA AI")}</span>
            </Link>
          </div>

          {/* Trust Badges */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-4 text-xs font-mono">
            {[
              { label: t("home.badge.sourceCited", "100% Source Cited") },
              { label: t("home.badge.zeroHallucin", "Zero Hallucinations") },
              { label: t("home.badge.multiJurisdiction", "Multi-Jurisdiction") },
            ].map((badge, i) => (
              <span
                key={i}
                className="flex items-center gap-1.5 text-[#A8B5AC] bg-[#050806]/75 px-4 py-2 rounded-full border border-[#D4AF37]/25 backdrop-blur-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-[#087F5B]" />
                {badge.label}
              </span>
            ))}
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-1.5 text-[#718078] text-[10px] tracking-widest uppercase font-mono animate-float">
          <span>Scroll</span>
          <div className="w-px h-8 bg-gradient-to-b from-[#D4AF37]/60 to-transparent" />
        </div>
      </section>

      {/* ─── STATS STRIP ─── */}
      <section className="relative z-10 bg-[#050806] border-y border-[#D4AF37]/15">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TrendingUp, value: "5,000+", label: t("home.stats.formulations", "Formulations Analyzed") },
            { icon: Shield, value: "98.6%", label: t("home.stats.accuracy", "Citation Accuracy") },
            { icon: Users, value: "12+", label: t("home.stats.jurisdictions", "Jurisdictions Covered") },
            { icon: Zap, value: "<30s", label: t("home.stats.response", "Avg. Response Time") },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="stat-card rounded-2xl p-5 text-center space-y-2">
                <Icon className="w-5 h-5 text-[#087F5B] mx-auto" />
                <div className="text-2xl font-extrabold text-shimmer">{stat.value}</div>
                <div className="text-xs text-[#718078] font-mono">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── HOW AYUSHYA WORKS ─── */}
      <section
        id="how-it-works"
        className="relative z-10 bg-[#050806] max-w-7xl mx-auto px-4 sm:px-6 py-20 space-y-14"
      >
        <div className="text-center space-y-3">
          <span className="text-xs font-mono uppercase tracking-widest text-[#D4AF37] font-semibold">
            {t("home.steps.tag", "Step-by-Step Workflow")}
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-[#F4F8F5] tracking-tight font-sans">
            {t("home.steps.title", "How AYUSHYA Works")}
          </h2>
          <p className="text-sm text-[#A8B5AC] max-w-xl mx-auto">
            {t("home.steps.subtitle", "From formulation input to source-cited statutory intelligence in five seamless steps.")}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
          <div className="hidden md:block absolute top-12 left-[10%] right-[10%] h-px step-connector z-0" />

          {[
            {
              num: "01",
              title: t("home.steps.step1.title", "Describe Product"),
              desc: t("home.steps.step1.desc", "Input herbal ingredients, processing method, and intended category."),
              icon: BookOpen,
            },
            {
              num: "02",
              title: t("home.steps.step2.title", "Classify Product"),
              desc: t("home.steps.step2.desc", "Preliminary AI categorization under FSSAI, AYUSH, or Cosmetic rules."),
              icon: Layers,
            },
            {
              num: "03",
              title: t("home.steps.step3.title", "Identify IP & Rules"),
              desc: t("home.steps.step3.desc", "Evaluate Section 3(p) exclusions, trademarks, and statutory compliance."),
              icon: Shield,
            },
            {
              num: "04",
              title: t("home.steps.step4.title", "Retrieve Evidence"),
              desc: t("home.steps.step4.desc", "Source-cited RAG queries India Code, IP India, WIPO, and Nagoya databases."),
              icon: FileText,
            },
            {
              num: "05",
              title: t("home.steps.step5.title", "Actionable Guidance"),
              desc: t("home.steps.step5.desc", "Generate a sourced compliance checklist, evidence links, and AI confidence score."),
              icon: CheckCircle2,
            },
          ].map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={idx}
                className="relative z-10 p-5 rounded-2xl bg-[#0A100C] border border-[#D4AF37]/20 card-hover space-y-3 flex flex-col group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-extrabold text-[#D4AF37] font-mono">{step.num}</span>
                  <div className="w-8 h-8 rounded-xl bg-[#0F1813] border border-[#087F5B]/40 flex items-center justify-center group-hover:bg-[#087F5B]/20 transition-colors">
                    <Icon className="w-4 h-4 text-[#087F5B]" />
                  </div>
                </div>
                <h3 className="text-sm font-bold text-[#F4F8F5] font-sans">{step.title}</h3>
                <p className="text-xs text-[#A8B5AC] leading-relaxed">{step.desc}</p>
                <div className="h-0.5 w-0 group-hover:w-full bg-gradient-to-r from-[#087F5B] to-[#D4AF37] transition-all duration-500 rounded-full mt-auto" />
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── FEATURE CARDS ─── */}
      <section className="relative z-10 bg-[#050806] max-w-7xl mx-auto px-4 sm:px-6 py-20 space-y-14">
        <div className="text-center space-y-3">
          <span className="text-xs font-mono uppercase tracking-widest text-[#D4AF37] font-semibold">
            {t("home.features.tag", "Core Capabilities")}
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-[#F4F8F5] tracking-tight font-sans">
            {t("home.features.title", "What AYUSHYA Can Help With")}
          </h2>
          <p className="text-sm text-[#A8B5AC] max-w-xl mx-auto">
            {t("home.features.subtitle", "Comprehensive legal and regulatory coverage tailored to Ayurvedic innovations.")}
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: Layers,
              title: t("home.features.feat1.title", "Product Classification"),
              desc: t(
                "home.features.feat1.desc",
                "Classifies products into Classical Medicines, Proprietary ASU Medicines, Ayurveda-Aahar, Phytopharmaceuticals, or Ayurvedic Cosmetics."
              ),
              accent: "#087F5B",
            },
            {
              icon: Shield,
              title: t("home.features.feat2.title", "IP Opportunities"),
              desc: t(
                "home.features.feat2.desc",
                "Evaluates formulation patent eligibility, Section 3(p) traditional knowledge exclusions, Section 3(e) admixtures, and trademark protections."
              ),
              accent: "#D4AF37",
            },
            {
              icon: FileText,
              title: t("home.features.feat3.title", "Regulatory Requirements"),
              desc: t(
                "home.features.feat3.desc",
                "Identifies FSSAI Ayurveda-Aahar licensing, Rule 158B Drugs & Cosmetics compliance, heavy metal monographs, and packaging rules."
              ),
              accent: "#087F5B",
            },
            {
              icon: Leaf,
              title: t("home.features.feat4.title", "Biodiversity & TKDL"),
              desc: t(
                "home.features.feat4.desc",
                "Navigates National Biodiversity Authority (NBA) approval requirements under BD Act 2002 and TKDL prior-art safeguards."
              ),
              accent: "#D4AF37",
            },
            {
              icon: Globe,
              title: t("home.features.feat5.title", "International Modes"),
              desc: t(
                "home.features.feat5.desc",
                "Explicit jurisdiction toggles for India, US FDA, EU regulations, and WIPO frameworks — never silently mixing legal systems."
              ),
              accent: "#087F5B",
            },
            {
              icon: Bot,
              title: t("home.features.feat6.title", "Source-Cited AI RAG"),
              desc: t(
                "home.features.feat6.desc",
                "Interactive assistant that answers strictly with statutory citations, section references, confidence scores, and legal disclaimers."
              ),
              accent: "#D4AF37",
            },
          ].map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-[#0A100C] border border-[#D4AF37]/20 card-hover space-y-4 flex flex-col group relative overflow-hidden"
              >
                <div
                  className="absolute -top-16 -right-16 w-32 h-32 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-2xl pointer-events-none"
                  style={{ background: `radial-gradient(circle, ${feat.accent}40, transparent 70%)` }}
                />
                <div className="space-y-3 relative z-10">
                  <div
                    className="w-11 h-11 rounded-xl border flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg"
                    style={{
                      background: `${feat.accent}18`,
                      borderColor: `${feat.accent}50`,
                      boxShadow: `0 0 20px ${feat.accent}20`,
                    }}
                  >
                    <Icon className="w-5 h-5" style={{ color: feat.accent }} />
                  </div>
                  <h3 className="text-base font-bold text-[#F4F8F5] group-hover:text-[#D4AF37] transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-xs text-[#A8B5AC] leading-relaxed">{feat.desc}</p>
                </div>
                <div className="relative z-10 mt-auto pt-3 border-t border-[#D4AF37]/10">
                  <span className="text-xs text-[#087F5B] font-mono group-hover:text-[#0CA678] transition-colors flex items-center gap-1">
                    Learn more <ArrowRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── TRUST / TESTIMONIALS ─── */}
      <section className="relative z-10 bg-[#050806] max-w-7xl mx-auto px-4 sm:px-6 py-16">
        <div className="rounded-3xl border border-[#D4AF37]/20 bg-[#0A100C]/80 backdrop-blur-sm p-8 sm:p-12 space-y-8">
          <div className="text-center space-y-2">
            <span className="text-xs font-mono uppercase tracking-widest text-[#D4AF37]">
              {t("home.trust.tag", "Trusted By Innovators")}
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#F4F8F5]">
              {t("home.trust.title", "Built on Statutory Accuracy")}
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                quote: t("home.trust.q1", "AYUSHYA identified a Section 3(p) exclusion we missed entirely. It saved our patent filing strategy."),
                author: "Ayurvedic Startup Founder",
              },
              {
                quote: t("home.trust.q2", "The FSSAI classification guidance with actual rule citations was incredibly precise and actionable."),
                author: "R&D Head, Herbal Brand",
              },
              {
                quote: t("home.trust.q3", "Multi-jurisdiction toggles helped us understand India vs EU regulatory gaps instantly."),
                author: "IP Attorney, New Delhi",
              },
            ].map((item, i) => (
              <div key={i} className="p-5 rounded-2xl bg-[#050806]/70 border border-[#D4AF37]/15 space-y-3">
                <div className="flex gap-0.5">
                  {Array.from({ length: 5 }).map((_, s) => (
                    <Star key={s} className="w-3.5 h-3.5 fill-[#D4AF37] text-[#D4AF37]" />
                  ))}
                </div>
                <p className="text-sm text-[#C8D5CC] leading-relaxed italic">&ldquo;{item.quote}&rdquo;</p>
                <p className="text-xs text-[#718078] font-mono">— {item.author}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── CALL TO ACTION ─── */}
      <section className="relative z-10 bg-[#050806] max-w-5xl mx-auto px-4 sm:px-6 py-12 pb-24">
        <div className="relative p-8 sm:p-14 rounded-3xl border border-[#D4AF37]/30 text-center space-y-6 overflow-hidden">
          <div className="absolute inset-0 hero-bg opacity-15 rounded-3xl" aria-hidden="true" />
          <div
            className="absolute inset-0 rounded-3xl"
            style={{
              background: "linear-gradient(135deg, rgba(5,8,6,0.95) 0%, rgba(8,127,91,0.12) 50%, rgba(5,8,6,0.95) 100%)",
            }}
          />
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-32 bg-[#087F5B]/20 blur-3xl pointer-events-none" />
          <div className="relative z-10 space-y-3">
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
              {t("home.cta.title", "Ready to Analyze Your Ayurvedic Formulation?")}
            </h2>
            <p className="text-sm text-[#A8B5AC] max-w-xl mx-auto">
              {t(
                "home.cta.subtitle",
                "Get an instant evidence-backed analysis report with preliminary classification, IP options, and regulatory checklist."
              )}
            </p>
          </div>
          <div className="relative z-10 flex flex-wrap justify-center gap-4">
            <Link
              href="/analyze"
              id="cta-analyze-btn"
              className="btn-primary-glow px-10 py-4 rounded-full text-sm font-bold text-white shadow-xl inline-flex items-center gap-2"
            >
              {t("home.cta.analyzeNow", "Analyze Product Now")}
              <ArrowRight className="w-4 h-4 text-[#D4AF37]" />
            </Link>
            <Link
              href="/assistant"
              id="cta-assistant-btn"
              className="btn-gold-outline px-10 py-4 rounded-full text-sm font-semibold transition-colors inline-flex items-center gap-2"
            >
              <Bot className="w-4 h-4 text-[#087F5B]" />
              {t("home.cta.askAssistant", "Ask AI Assistant")}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
