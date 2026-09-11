"use client";

import React from "react";
import { Chatbot } from "@/components/Chatbot/Chatbot";
import { Sparkles, ShieldAlert, Scale } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";
import { CosmicStars } from "@/components/ui/cosmic-stars";

export default function FullPageAssistant() {
  const { t } = useLanguage();

  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-8 relative">
      {/* Page-Specific Animated Cosmic Starfield (Exclusively on Assistant) */}
      <CosmicStars />

      {/* Ambient background glow */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#087F5B]/15 blur-[120px] pointer-events-none -z-10" />

      {/* Top Header Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 p-6 sm:p-8 rounded-3xl bg-[#080D0A]/90 border border-[rgba(212,175,55,0.22)] shadow-2xl backdrop-blur-2xl">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0D1611] border border-[#D4AF37]/35 text-[#F3E5AB] text-xs font-mono font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-[#10B981]" />
            <span>{t("chat.fullPageTag", "Full-Page RAG Legal Assistant")}</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
            {t("chat.fullPageTitle", "Ask AYUSHYA Intelligence")}
          </h1>
          <p className="text-xs sm:text-sm text-[#A3B3A9] max-w-xl leading-relaxed">
            {t("chat.fullPageDesc", "Evidence-backed legal intelligence for your Ayurveda product grounded in Indian & International frameworks.")}
          </p>
        </div>

        <div className="flex items-start sm:items-center gap-3 p-3.5 rounded-2xl bg-[#040705] border border-[#D4AF37]/30 text-[#F3E5AB] text-xs max-w-sm shadow-sm">
          <ShieldAlert className="w-4.5 h-4.5 shrink-0 text-[#D4AF37] mt-0.5 sm:mt-0" />
          <span className="leading-relaxed font-sans">{t("chat.decisionNotice", "Decision-support information based on available evidence. Not legal advice.")}</span>
        </div>
      </div>

      {/* Full-Page Chatbot Instance */}
      <Chatbot mode="fullPage" jurisdiction="India" />
    </div>
  );
}
