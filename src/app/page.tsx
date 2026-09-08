"use client";

import React from "react";
import Link from "next/link";
import { FloatingPathsBackground } from "@/components/ui/floating-paths";
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
} from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export default function Home() {
  const { t } = useLanguage();

  return (
    <main className="min-h-screen w-full bg-[#050806] text-[#F4F8F5] relative overflow-hidden bg-radial-glow">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />

      {/* Hero Section wrapped with FloatingPathsBackground */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 pt-16 pb-20 space-y-16">
        <FloatingPathsBackground position={-1} className="py-12 rounded-3xl">
          <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10 px-4">
            {/* Top Badge */}
            <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-[#0A100C] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-mono tracking-wide shadow-[0_0_20px_rgba(8,127,91,0.15)]">
              <Sparkles className="w-4 h-4 text-[#087F5B]" />
              <span>{t("home.badge", "AI-Powered IP & Regulatory Intelligence")}</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#F4F8F5] tracking-tight leading-[1.18] font-sans">
              {t("home.hero.title1", "AI-Powered")}{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#087F5B] via-[#0CA678] to-[#D4AF37] drop-shadow-[0_0_25px_rgba(8,127,91,0.3)]">
                {t("home.hero.title2", "IP & Regulatory Intelligence")}
              </span>{" "}
              <br />
              {t("home.hero.title3", "for Ayurveda")}
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-[#A8B5AC] max-w-2xl mx-auto font-normal leading-relaxed">
              {t(
                "home.hero.description",
                "Understand intellectual property protections, traditional knowledge exclusions (Section 3p), FSSAI regulations, and biodiversity obligations with evidence-backed legal AI."
              )}
            </p>

            {/* Hero Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
              <Link
                href="/analyze"
                className="btn-primary-glow inline-flex items-center justify-center gap-2.5 px-8 py-4 rounded-full text-sm font-bold tracking-wide text-white shadow-xl min-w-[200px]"
              >
                <span>{t("home.hero.analyzeBtn", "Analyze Your Product")}</span>
                <ArrowRight className="w-4.5 h-4.5 text-[#D4AF37]" />
              </Link>
              <Link
                href="/assistant"
                className="btn-gold-outline inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full text-sm font-semibold transition-all min-w-[200px]"
              >
                <Bot className="w-4.5 h-4.5 text-[#087F5B]" />
                <span>{t("home.hero.askBtn", "Ask AYUSHYA AI")}</span>
              </Link>
            </div>

            {/* Trust Highlights Badges */}
            <div className="pt-6 flex flex-wrap items-center justify-center gap-6 text-xs text-[#718078] font-mono">
              <span className="flex items-center gap-1.5 text-[#A8B5AC] bg-[#0A100C]/80 px-3.5 py-1.5 rounded-full border border-[#D4AF37]/20">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#087F5B]" /> {t("home.badge.sourceCited", "100% Source Cited")}
              </span>
              <span className="flex items-center gap-1.5 text-[#A8B5AC] bg-[#0A100C]/80 px-3.5 py-1.5 rounded-full border border-[#D4AF37]/20">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#087F5B]" /> {t("home.badge.zeroHallucin", "Zero Hallucinations")}
              </span>
              <span className="flex items-center gap-1.5 text-[#A8B5AC] bg-[#0A100C]/80 px-3.5 py-1.5 rounded-full border border-[#D4AF37]/20">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#087F5B]" /> {t("home.badge.multiJurisdiction", "Multi-Jurisdiction")}
              </span>
            </div>
          </div>
        </FloatingPathsBackground>
      </section>

      {/* How AYUSHYA Works (5 Steps) */}
      <section id="how-it-works" className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16 space-y-12">
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
          <div className="hidden md:block absolute top-12 left-[10%] right-[10%] h-[1px] bg-gradient-to-r from-transparent via-[#D4AF37]/40 to-transparent z-0" />

          {[
            {
              num: "01",
              title: t("home.steps.step1.title", "Describe Product"),
              desc: t("home.steps.step1.desc", "Input herbal ingredients, processing method, and intended category."),
            },
            {
              num: "02",
              title: t("home.steps.step2.title", "Classify Product"),
              desc: t("home.steps.step2.desc", "Preliminary AI categorization under FSSAI, AYUSH, or Cosmetic rules."),
            },
            {
              num: "03",
              title: t("home.steps.step3.title", "Identify IP & Rules"),
              desc: t("home.steps.step3.desc", "Evaluate Section 3(p) exclusions, trademarks, and statutory compliance."),
            },
            {
              num: "04",
              title: t("home.steps.step4.title", "Retrieve Evidence"),
              desc: t("home.steps.step4.desc", "Source-cited RAG queries India Code, IP India, WIPO, and Nagoya databases."),
            },
            {
              num: "05",
              title: t("home.steps.step5.title", "Actionable Guidance"),
              desc: t("home.steps.step5.desc", "Generate a sourced compliance checklist, evidence links, and AI confidence score."),
            },
          ].map((step, idx) => (
            <div
              key={idx}
              className="relative z-10 p-5 rounded-2xl bg-[#0A100C] border border-[#D4AF37]/20 card-hover space-y-3 flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-extrabold text-[#D4AF37] font-mono">{step.num}</span>
                  <div className="w-2 h-2 rounded-full bg-[#087F5B]" />
                </div>
                <h3 className="text-sm font-bold text-[#F4F8F5] font-sans">{step.title}</h3>
                <p className="text-xs text-[#A8B5AC] leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Cards */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-16 space-y-12">
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
            },
            {
              icon: Shield,
              title: t("home.features.feat2.title", "IP Opportunities"),
              desc: t(
                "home.features.feat2.desc",
                "Evaluates formulation patent eligibility, Section 3(p) traditional knowledge exclusions, Section 3(e) admixtures, and trademark protections."
              ),
            },
            {
              icon: FileText,
              title: t("home.features.feat3.title", "Regulatory Requirements"),
              desc: t(
                "home.features.feat3.desc",
                "Identifies FSSAI Ayurveda-Aahar licensing, Rule 158B Drugs & Cosmetics compliance, heavy metal monographs, and packaging rules."
              ),
            },
            {
              icon: Leaf,
              title: t("home.features.feat4.title", "Biodiversity & TKDL"),
              desc: t(
                "home.features.feat4.desc",
                "Navigates National Biodiversity Authority (NBA) approval requirements under BD Act 2002 and TKDL prior-art safeguards."
              ),
            },
            {
              icon: Globe,
              title: t("home.features.feat5.title", "International Modes"),
              desc: t(
                "home.features.feat5.desc",
                "Explicit jurisdiction toggles for India, US FDA, EU regulations, and WIPO frameworks — never silently mixing legal systems."
              ),
            },
            {
              icon: Bot,
              title: t("home.features.feat6.title", "Source-Cited AI RAG"),
              desc: t(
                "home.features.feat6.desc",
                "Interactive assistant that answers strictly with statutory citations, section references, confidence scores, and legal disclaimers."
              ),
            },
          ].map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-[#0A100C] border border-[#D4AF37]/20 card-hover space-y-4 flex flex-col justify-between group"
              >
                <div className="space-y-3">
                  <div className="w-10 h-10 rounded-xl bg-[#0F1813] border border-[#D4AF37]/30 flex items-center justify-center text-[#087F5B] group-hover:scale-105 transition-transform shadow-[0_0_15px_rgba(8,127,91,0.2)]">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-[#F4F8F5] group-hover:text-[#D4AF37] transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-xs text-[#A8B5AC] leading-relaxed">{feat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Call to Action Banner */}
      <section className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-12">
        <div className="p-8 sm:p-12 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/30 shadow-[0_0_60px_rgba(8,127,91,0.2)] text-center space-y-6 relative overflow-hidden">
          <div className="absolute inset-0 bg-radial-glow opacity-50 pointer-events-none" />
          <div className="relative z-10 space-y-3">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
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
              className="btn-primary-glow px-8 py-3.5 rounded-full text-sm font-bold text-white shadow-xl"
            >
              {t("home.cta.analyzeNow", "Analyze Product Now")}
            </Link>
            <Link
              href="/assistant"
              className="btn-gold-outline px-8 py-3.5 rounded-full text-sm font-semibold transition-colors"
            >
              {t("home.cta.askAssistant", "Ask AI Assistant")}
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
