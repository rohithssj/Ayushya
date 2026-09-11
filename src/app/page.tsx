"use client";

import React, { useState, useEffect } from "react";
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
  TrendingUp,
  Users,
  Zap,
  Scale,
  Check,
} from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";
import HeroLotusContainer from "@/components/Hero/HeroLotusContainer";

export default function Home() {
  const { t } = useLanguage();

  // Scroll tracking specifically for the Hero section transition
  const [scrollY, setScrollY] = useState(0);

  // Vertical timeline state for "How AYUSHYA Works"
  const [activeStep, setActiveStep] = useState(0);
  const [stepVisibility, setStepVisibility] = useState<boolean[]>([true, false, false, false, false]);
  const [timelineProgress, setTimelineProgress] = useState(0);

  useEffect(() => {
    let ticking = false;
    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const currentY = window.scrollY;
          setScrollY(currentY);

          // Calculate vertical timeline progress & step activation
          const timelineEl = document.getElementById("how-it-works-timeline");
          if (timelineEl) {
            const rect = timelineEl.getBoundingClientRect();
            const vh = window.innerHeight;

            // Height & distance calculation for dynamic vertical line
            const totalH = rect.height;
            const scrollDistance = (vh * 0.55) - rect.top;
            const progress = Math.max(0, Math.min(100, (scrollDistance / totalH) * 100));
            setTimelineProgress(progress);

            // Check each step element position
            const stepEls = timelineEl.querySelectorAll<HTMLElement>("[data-step-index]");
            let currentActive = 0;
            const newVis: boolean[] = [];

            stepEls.forEach((el, idx) => {
              const elRect = el.getBoundingClientRect();
              // Become visible when entering lower half of viewport
              const isVis = elRect.top < vh * 0.88;
              newVis[idx] = isVis;

              // Step becomes active when crossing central reading line
              if (elRect.top <= vh * 0.52) {
                currentActive = idx;
              }
            });

            setStepVisibility((prev) => {
              const next = [...prev];
              newVis.forEach((v, idx) => {
                if (v) next[idx] = true;
              });
              return next;
            });

            setActiveStep(currentActive);
          }

          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Smooth scroll-driven opacity, scale, and parallax specifically for Hero
  const heroOpacity = Math.max(0, Math.min(1, 1 - scrollY / 550));
  const heroScale = 1 + Math.min(scrollY * 0.00035, 0.07);
  const heroTranslateY = Math.min(scrollY * 0.22, 120);

  return (
    <div className="min-h-screen w-full text-[#F4F8F5] relative overflow-hidden">
      {/* Ambient background light gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-b from-[#087F5B]/20 via-[#D4AF37]/5 to-transparent blur-[140px] pointer-events-none -z-10" />
      <div className="absolute top-[800px] right-0 w-[500px] h-[500px] bg-[#087F5B]/10 blur-[130px] pointer-events-none -z-10" />

      {/* ─── HERO SECTION WITH SPECIFIC ARTWORK & SMOOTH SCROLL TRANSITION ─── */}
      <section className="relative min-h-[95vh] flex items-center justify-center overflow-hidden pt-12 pb-24">
        {/* Specifically Rendered Ayurvedic Illustration Artwork with Scroll Transition */}
        <div
          className="absolute inset-0 z-0 pointer-events-none transition-opacity duration-300 ease-out will-change-transform overflow-hidden"
          style={{
            opacity: heroOpacity,
            transform: `translateY(${heroTranslateY}px) scale(${heroScale})`,
          }}
          aria-hidden="true"
        >
          <img
            src="/hero-ayurveda-artwork.png"
            alt="Ayurvedic IP & Regulatory Intelligence Artwork"
            className="w-full h-full object-cover object-center sm:object-[center_35%]"
          />

          {/* Center radial vignette for maximum text readability */}
          <div
            className="absolute inset-0"
            style={{
              background:
                "radial-gradient(ellipse at 50% 48%, rgba(4,7,5,0.82) 0%, rgba(4,7,5,0.55) 45%, rgba(4,7,5,0.2) 75%, transparent 100%)",
            }}
          />

          {/* Smooth bottom fade-out transition into the next section */}
          <div
            className="absolute inset-x-0 bottom-0 h-44"
            style={{
              background: "linear-gradient(to bottom, transparent 0%, rgba(4,7,5,0.7) 40%, #040705 100%)",
            }}
          />

          {/* Smooth top fade for seamless navbar integration */}
          <div
            className="absolute inset-x-0 top-0 h-28"
            style={{
              background: "linear-gradient(to bottom, #040705 0%, rgba(4,7,5,0.6) 40%, transparent 100%)",
            }}
          />
        </div>

        {/* Engineering Grid Overlay */}
        <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none z-1" />

        {/* Content */}
        <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-8 animate-fade-slide-in-1">
          {/* Top Tag Badge */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#080D0A]/90 border border-[#D4AF37]/35 text-[#F3E5AB] text-xs font-mono font-medium shadow-[0_0_25px_rgba(8,127,91,0.25)] backdrop-blur-md">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[#059669]" />
            </span>
            <span>Statutory Legal AI • India & International Jurisdictions</span>
          </div>

          {/* Main Headline with 3D Ayurvedic Lotus Flower Centered Directly in Background */}
          <div className="relative flex items-center justify-center">
            {/* 3D Interactive Ayurvedic Lotus Flower (Middel Backside of Title Text) */}
            <div
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[340px] sm:w-[480px] md:w-[600px] lg:w-[720px] xl:w-[820px] h-[340px] sm:h-[480px] md:h-[600px] lg:h-[720px] xl:h-[820px] pointer-events-none -z-10 select-none transition-opacity duration-300"
              style={{
                opacity: heroOpacity,
              }}
              aria-hidden="true"
            >
              <HeroLotusContainer />
            </div>

            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.12] font-display relative z-10">
              <span className="text-[#F4F8F5] drop-shadow-[0_4px_30px_rgba(0,0,0,0.95)]">
                {t("home.hero.title1", "AI-Powered")}
              </span>{" "}
              <br className="hidden sm:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#10B981] via-[#34D399] to-[#D4AF37] drop-shadow-[0_0_40px_rgba(8,127,91,0.5)]">
                {t("home.hero.title2", "IP & Regulatory")}
              </span>{" "}
              <br className="hidden sm:block" />
              <span className="text-[#F4F8F5] drop-shadow-[0_4px_30px_rgba(0,0,0,0.95)]">
                {t("home.hero.title3", "Intelligence for Ayurveda")}
              </span>
            </h1>
          </div>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-[#A3B3A9] max-w-2xl mx-auto leading-relaxed font-normal drop-shadow-[0_2px_12px_rgba(0,0,0,0.9)]">
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
              className="btn-primary-glow animate-pulse-glow inline-flex items-center justify-center gap-2.5 px-9 py-4 rounded-full text-sm font-bold tracking-wider text-white shadow-2xl min-w-[230px] group"
            >
              <span>{t("home.hero.analyzeBtn", "Analyze Your Product")}</span>
              <ArrowRight className="w-4 h-4 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/assistant"
              id="hero-assistant-btn"
              className="btn-gold-outline inline-flex items-center justify-center gap-2.5 px-9 py-4 rounded-full text-sm font-semibold transition-all min-w-[230px] group"
            >
              <Bot className="w-4 h-4 text-[#10B981] group-hover:scale-110 transition-transform" />
              <span>{t("home.hero.askBtn", "Ask AYUSHYA AI")}</span>
            </Link>
          </div>

          {/* Trust Badges */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-3 text-xs font-mono">
            {[
              { label: t("home.badge.sourceCited", "100% Source Cited") },
              { label: t("home.badge.zeroHallucin", "Zero Hallucinations") },
              { label: t("home.badge.multiJurisdiction", "Multi-Jurisdiction") },
            ].map((badge, i) => (
              <span
                key={i}
                className="flex items-center gap-2 text-[#A3B3A9] bg-[#080D0A]/90 px-4 py-2 rounded-full border border-[#D4AF37]/25 backdrop-blur-md shadow-sm"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-[#10B981]" />
                <span>{badge.label}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2 text-[#6C7D73] text-[10px] tracking-widest uppercase font-mono animate-float">
          <span>Scroll</span>
          <div className="w-px h-8 bg-gradient-to-b from-[#D4AF37]/70 to-transparent" />
        </div>
      </section>

      {/* ─── STATS STRIP (ORIGINAL DESIGN MAINTAINED) ─── */}
      <section className="relative z-10 border-y border-[rgba(212,175,55,0.15)] bg-[#040705]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 grid grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { icon: TrendingUp, value: "5,000+", label: t("home.stats.formulations", "Formulations Analyzed") },
            { icon: Shield, value: "98.6%", label: t("home.stats.accuracy", "Citation Accuracy") },
            { icon: Users, value: "12+", label: t("home.stats.jurisdictions", "Jurisdictions Covered") },
            { icon: Zap, value: "<30s", label: t("home.stats.response", "Avg. Response Time") },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="stat-card rounded-2xl p-6 text-center space-y-2 group">
                <div className="w-10 h-10 rounded-xl bg-[#087F5B]/15 border border-[#087F5B]/30 flex items-center justify-center mx-auto text-[#10B981] group-hover:scale-110 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <div className="text-3xl font-extrabold text-shimmer font-display">{stat.value}</div>
                <div className="text-xs text-[#6C7D73] font-mono tracking-wider">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ─── HOW AYUSHYA WORKS (MODERN VERTICAL STEP-BY-STEP TIMELINE) ─── */}
      <section
        id="how-it-works"
        className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 py-28 scroll-mt-24 space-y-16"
      >
        {/* Section Header */}
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#080D0A] border border-[#D4AF37]/30 text-[#F3E5AB] text-xs font-mono uppercase tracking-widest font-semibold shadow-[0_0_15px_rgba(212,175,55,0.15)]">
            <Sparkles className="w-3.5 h-3.5 text-[#10B981]" />
            <span>{t("home.steps.tag", "Step-by-Step Workflow")}</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
            {t("home.steps.title", "How AYUSHYA Works")}
          </h2>
          <p className="text-sm sm:text-base text-[#A3B3A9] leading-relaxed">
            {t("home.steps.subtitle", "From formulation input to source-cited statutory intelligence in five seamless steps.")}
          </p>

          {/* Dynamic Stage Indicator Capsule */}
          <div className="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-[#090F0B]/80 border border-white/[0.08] text-xs font-mono text-[#A3B3A9] backdrop-blur-md">
            <span className="text-[#D4AF37] font-bold">STAGE {activeStep + 1} OF 5</span>
            <div className="flex items-center gap-1.5">
              {[0, 1, 2, 3, 4].map((stepIdx) => (
                <span
                  key={stepIdx}
                  className={`h-1.5 rounded-full transition-all duration-300 ${
                    stepIdx === activeStep
                      ? "w-6 bg-gradient-to-r from-[#10B981] to-[#D4AF37] shadow-[0_0_8px_rgba(16,185,129,0.8)]"
                      : stepIdx < activeStep
                      ? "w-3 bg-[#10B981]"
                      : "w-1.5 bg-white/20"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Vertical Timeline Flow */}
        <div id="how-it-works-timeline" className="relative pt-6 pb-12">
          {/* Desktop Central Vertical Spine */}
          <div className="hidden lg:block absolute left-1/2 top-8 bottom-12 -translate-x-1/2 w-1 bg-white/[0.06] rounded-full overflow-hidden">
            <div
              className="w-full bg-gradient-to-b from-[#10B981] via-[#34D399] to-[#D4AF37] rounded-full transition-all duration-300 ease-out shadow-[0_0_16px_rgba(16,185,129,0.85)]"
              style={{ height: `${timelineProgress}%` }}
            />
          </div>

          {/* Mobile/Tablet Left Vertical Spine */}
          <div className="block lg:hidden absolute left-6 sm:left-8 top-8 bottom-12 -translate-x-1/2 w-1 bg-white/[0.06] rounded-full overflow-hidden">
            <div
              className="w-full bg-gradient-to-b from-[#10B981] via-[#34D399] to-[#D4AF37] rounded-full transition-all duration-300 ease-out shadow-[0_0_16px_rgba(16,185,129,0.85)]"
              style={{ height: `${timelineProgress}%` }}
            />
          </div>

          {/* Sequence of 5 Vertical Steps */}
          <div className="space-y-12 sm:space-y-16 lg:space-y-24 relative">
            {[
              {
                num: "01",
                stage: "Stage 01",
                title: t("home.steps.step1.title", "Describe Product"),
                desc: t("home.steps.step1.desc", "Input herbal ingredients, processing method, and intended category."),
                icon: BookOpen,
                deliverable: "Standardized Formulation Profile",
                tags: ["Herbal Ingredients", "Classical Shastras", "Dosage Matrix"],
              },
              {
                num: "02",
                stage: "Stage 02",
                title: t("home.steps.step2.title", "Classify Product"),
                desc: t("home.steps.step2.desc", "Preliminary AI categorization under FSSAI, AYUSH, or Cosmetic rules."),
                icon: Layers,
                deliverable: "Statutory Classification Dossier",
                tags: ["FSSAI Food/Nutra", "AYUSH Schedule T", "Cosmetics Rules 2020"],
              },
              {
                num: "03",
                stage: "Stage 03",
                title: t("home.steps.step3.title", "Identify IP & Rules"),
                desc: t("home.steps.step3.desc", "Evaluate Section 3(p) exclusions, trademarks, and statutory compliance."),
                icon: Shield,
                deliverable: "IP Eligibility & Conflict Analysis",
                tags: ["Section 3(p) Shield", "TKDL Search Exclusions", "TM Classes 05 & 30"],
              },
              {
                num: "04",
                stage: "Stage 04",
                title: t("home.steps.step4.title", "Retrieve Evidence"),
                desc: t("home.steps.step4.desc", "Source-cited RAG queries India Code, IP India, WIPO, and Nagoya databases."),
                icon: FileText,
                deliverable: "100% Sourced Statutory Citations",
                tags: ["India Code Official Gazettes", "NBA / State Biodiversity Board", "WIPO Lex Cross-Ref"],
              },
              {
                num: "05",
                stage: "Stage 05",
                title: t("home.steps.step5.title", "Actionable Guidance"),
                desc: t("home.steps.step5.desc", "Generate a sourced compliance checklist, evidence links, and AI confidence score."),
                icon: CheckCircle2,
                deliverable: "Executive Regulatory Compliance Pack",
                tags: ["Audit-Ready Checklist", "Confidence Metric", "Sourced Evidence Links"],
              },
            ].map((step, idx) => {
              const Icon = step.icon;
              const isActive = activeStep === idx;
              const isPassed = activeStep > idx;
              const isVisible = stepVisibility[idx];
              const isEven = idx % 2 === 0;

              return (
                <div
                  key={idx}
                  data-step-index={idx}
                  className="relative flex items-center"
                >
                  {/* Timeline Step Node Circle (Center on Desktop, Left on Mobile) */}
                  <div className="absolute left-6 sm:left-8 lg:left-1/2 -translate-x-1/2 z-20">
                    <div
                      className={`w-11 h-11 sm:w-13 sm:h-13 rounded-2xl flex items-center justify-center font-mono font-bold text-xs sm:text-sm transition-all duration-500 ${
                        isActive
                          ? "bg-gradient-to-br from-[#087F5B] to-[#040705] text-[#F3E5AB] border-2 border-[#D4AF37] scale-110 shadow-[0_0_28px_rgba(16,185,129,0.7)] ring-4 ring-[#10B981]/30"
                          : isPassed
                          ? "bg-[#087F5B] text-white border border-[#10B981] shadow-[0_0_15px_rgba(8,127,91,0.5)]"
                          : "bg-[#090F0B] text-[#6C7D73] border border-white/[0.12] shadow-sm"
                      }`}
                    >
                      {isPassed ? (
                        <Check className="w-5 h-5 text-[#F3E5AB] stroke-[2.5]" />
                      ) : (
                        <span>{step.num}</span>
                      )}
                    </div>
                  </div>

                  {/* Desktop Layout (Alternating Left/Right) & Mobile Layout (Right of Spine) */}
                  <div className="w-full grid grid-cols-1 lg:grid-cols-2 lg:gap-20 items-center">
                    {/* Left Column on Desktop */}
                    <div
                      className={`pl-14 sm:pl-20 lg:pl-0 ${
                        isEven ? "lg:text-right" : "lg:order-2 lg:text-left"
                      }`}
                    >
                      <div
                        className={`group relative p-6 sm:p-7 rounded-3xl transition-all duration-700 ease-out border ${
                          isActive
                            ? "bg-[#090F0B]/95 border-[#D4AF37]/80 shadow-[0_15px_45px_rgba(8,127,91,0.3)] ring-1 ring-[#D4AF37]/40 scale-[1.01]"
                            : "bg-[#090F0B]/75 border-white/[0.08] hover:border-[#10B981]/50 shadow-[0_10px_30px_rgba(0,0,0,0.5)]"
                        } ${
                          isVisible
                            ? "opacity-100 translate-y-0 scale-100"
                            : "opacity-0 translate-y-10 scale-[0.97]"
                        }`}
                      >
                        {/* Top Meta Bar */}
                        <div
                          className={`flex items-center gap-3 mb-3 ${
                            isEven ? "lg:justify-end" : "lg:justify-start"
                          }`}
                        >
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase bg-[#087F5B]/20 text-[#34D399] border border-[#087F5B]/40">
                            {step.stage}
                          </span>
                          {isActive && (
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-[#D4AF37]/15 text-[#F3E5AB] border border-[#D4AF37]/40 animate-pulse">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]" />
                              ACTIVE STEP
                            </span>
                          )}
                          {isPassed && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono text-[#10B981] bg-[#10B981]/10">
                              <Check className="w-3 h-3" /> VERIFIED
                            </span>
                          )}
                        </div>

                        {/* Title & Icon Header */}
                        <div
                          className={`flex items-start gap-4 mb-3 ${
                            isEven ? "lg:flex-row-reverse" : "flex-row"
                          }`}
                        >
                          <div
                            className={`w-11 h-11 rounded-2xl flex-shrink-0 flex items-center justify-center border transition-all duration-300 ${
                              isActive
                                ? "bg-[#087F5B]/30 border-[#D4AF37]/70 text-[#D4AF37] shadow-[0_0_15px_rgba(212,175,55,0.35)]"
                                : "bg-[#0D1611] border-[#087F5B]/30 text-[#10B981] group-hover:border-[#10B981]"
                            }`}
                          >
                            <Icon className="w-5 h-5" />
                          </div>
                          <div>
                            <h3 className="text-base sm:text-lg font-extrabold text-[#F4F8F5] font-display group-hover:text-[#F3E5AB] transition-colors">
                              {step.title}
                            </h3>
                            <span className="text-[11px] text-[#6C7D73] font-mono uppercase tracking-wider block">
                              {step.deliverable}
                            </span>
                          </div>
                        </div>

                        {/* Description */}
                        <p className="text-xs sm:text-sm text-[#A3B3A9] leading-relaxed mb-4">
                          {step.desc}
                        </p>

                        {/* Feature Badges */}
                        <div
                          className={`flex flex-wrap gap-2 pt-2 border-t border-white/[0.06] ${
                            isEven ? "lg:justify-end" : "lg:justify-start"
                          }`}
                        >
                          {step.tags.map((tag, tagIdx) => (
                            <span
                              key={tagIdx}
                              className="px-2.5 py-1 rounded-lg text-[10px] font-mono font-medium bg-[#040705] border border-white/[0.08] text-[#A3B3A9] group-hover:border-[#087F5B]/50 transition-colors"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>

                        {/* Bottom Gradient Accent Bar */}
                        <div
                          className={`h-0.5 rounded-full transition-all duration-500 mt-4 ${
                            isActive
                              ? "w-full bg-gradient-to-r from-[#10B981] via-[#34D399] to-[#D4AF37]"
                              : "w-0 group-hover:w-full bg-gradient-to-r from-[#10B981] to-[#D4AF37]"
                          }`}
                        />
                      </div>
                    </div>

                    {/* Opposite Column on Desktop (Balanced Context Pill / Deliverable preview) */}
                    <div
                      className={`hidden lg:flex items-center ${
                        isEven
                          ? "justify-start pl-8"
                          : "justify-end pr-8 lg:order-1"
                      } ${
                        isVisible
                          ? "opacity-100 translate-y-0"
                          : "opacity-0 translate-y-6"
                      } transition-all duration-700 delay-150`}
                    >
                      <div className="p-4 rounded-2xl bg-[#090F0B]/50 border border-white/[0.05] backdrop-blur-sm max-w-xs space-y-1.5 text-left">
                        <div className="flex items-center gap-2 text-[10px] uppercase font-mono tracking-wider text-[#D4AF37]">
                          <Sparkles className="w-3 h-3 text-[#10B981]" />
                          <span>Key Milestone</span>
                        </div>
                        <div className="text-xs font-bold text-[#F4F8F5] font-display">
                          {step.deliverable}
                        </div>
                        <div className="text-[11px] text-[#6C7D73] leading-snug">
                          {idx === 0 && "Validates herbal taxonomy and botanical classification against official pharmacopoeias."}
                          {idx === 1 && "Maps multi-jurisdiction regulatory boundary rules across AYUSH, FSSAI, and Cosmetics."}
                          {idx === 2 && "Screens Traditional Knowledge Digital Library (TKDL) and Section 3(p) statutory exclusions."}
                          {idx === 3 && "Performs grounded neural search over gazette notifications, treaty texts, and treaties."}
                          {idx === 4 && "Compiles actionable statutory compliance checklist with full evidence provenance."}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─── FEATURE CARDS / BENTO GRID (ORIGINAL DESIGN MAINTAINED) ─── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-24 space-y-16">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-[#080D0A] border border-[#D4AF37]/30 text-[#F3E5AB] text-xs font-mono uppercase tracking-widest font-semibold">
            <Scale className="w-3.5 h-3.5 text-[#10B981]" />
            <span>{t("home.features.tag", "Core Capabilities")}</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
            {t("home.features.title", "What AYUSHYA Can Help With")}
          </h2>
          <p className="text-sm text-[#A3B3A9] max-w-xl mx-auto">
            {t("home.features.subtitle", "Comprehensive legal and regulatory coverage tailored to Ayurvedic innovations.")}
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            {
              icon: Layers,
              title: t("home.features.feat1.title", "Product Classification"),
              desc: t(
                "home.features.feat1.desc",
                "Classifies products into Classical Medicines, Proprietary ASU Medicines, Ayurveda-Aahar, Phytopharmaceuticals, or Ayurvedic Cosmetics."
              ),
              accent: "#10B981",
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
              accent: "#10B981",
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
              accent: "#10B981",
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
                className="p-7 rounded-3xl bg-[#090F0B] border border-[rgba(212,175,55,0.18)] card-hover space-y-4 flex flex-col group relative overflow-hidden shadow-xl"
              >
                <div
                  className="absolute -top-16 -right-16 w-36 h-36 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-3xl pointer-events-none"
                  style={{ background: `radial-gradient(circle, ${feat.accent}35, transparent 70%)` }}
                />

                <div className="space-y-4 relative z-10">
                  <div
                    className="w-12 h-12 rounded-2xl border flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-md"
                    style={{
                      background: `${feat.accent}15`,
                      borderColor: `${feat.accent}40`,
                    }}
                  >
                    <Icon className="w-6 h-6" style={{ color: feat.accent }} />
                  </div>
                  <h3 className="text-lg font-bold text-[#F4F8F5] group-hover:text-[#F3E5AB] transition-colors font-display">
                    {feat.title}
                  </h3>
                  <p className="text-xs text-[#A3B3A9] leading-relaxed">{feat.desc}</p>
                </div>

                <div className="relative z-10 mt-auto pt-4 border-t border-[rgba(212,175,55,0.1)]">
                  <span className="text-xs text-[#10B981] font-mono group-hover:text-[#34D399] transition-colors flex items-center gap-1.5 font-semibold">
                    Explore Capability <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>


      {/* ─── CALL TO ACTION BANNER (ORIGINAL DESIGN MAINTAINED) ─── */}
      <section className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 py-12 pb-28">
        <div className="relative p-10 sm:p-16 rounded-3xl border border-[#D4AF37]/35 text-center space-y-8 overflow-hidden shadow-2xl bg-gradient-to-br from-[#090F0B] via-[#0D1812] to-[#040705]">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#087F5B]/25 blur-[100px] pointer-events-none" />
          <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

          <div className="relative z-10 space-y-3">
            <h2 className="text-3xl sm:text-5xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
              {t("home.cta.title", "Ready to Analyze Your Ayurvedic Formulation?")}
            </h2>
            <p className="text-sm sm:text-base text-[#A3B3A9] max-w-xl mx-auto leading-relaxed">
              {t(
                "home.cta.subtitle",
                "Get an instant evidence-backed analysis report with preliminary classification, IP options, and regulatory checklist."
              )}
            </p>
          </div>

          <div className="relative z-10 flex flex-wrap justify-center gap-4 pt-2">
            <Link
              href="/analyze"
              id="cta-analyze-btn"
              className="btn-primary-glow px-10 py-4 rounded-full text-sm font-bold text-white shadow-2xl inline-flex items-center gap-2.5 group tracking-wider"
            >
              <span>{t("home.cta.analyzeNow", "Analyze Product Now")}</span>
              <ArrowRight className="w-4 h-4 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/assistant"
              id="cta-assistant-btn"
              className="btn-gold-outline px-10 py-4 rounded-full text-sm font-semibold transition-all inline-flex items-center gap-2.5 group"
            >
              <Bot className="w-4 h-4 text-[#10B981] group-hover:scale-110 transition-transform" />
              <span>{t("home.cta.askAssistant", "Ask AI Assistant")}</span>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
