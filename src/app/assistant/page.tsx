"use client";

import React from "react";
import { Chatbot } from "@/components/Chatbot/Chatbot";
import { Sparkles, ShieldAlert } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export default function FullPageAssistant() {
  const { t } = useLanguage();

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/30 shadow-2xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0F1813] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-mono font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-[#087F5B]" />
            <span>{t("chat.fullPageTag", "Full-Page RAG Legal Assistant")}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
            {t("chat.fullPageTitle", "Ask AYUSHYA Intelligence")}
          </h1>
          <p className="text-xs text-[#A8B5AC]">
            {t("chat.fullPageDesc", "Evidence-backed legal intelligence for your Ayurveda product grounded in Indian & International frameworks.")}
          </p>
        </div>

        <div className="flex items-center gap-2 p-3 rounded-2xl bg-[#050806] border border-[#D4AF37]/30 text-[#D4AF37] text-xs max-w-sm">
          <ShieldAlert className="w-4 h-4 shrink-0 text-[#D4AF37]" />
          <span>{t("chat.decisionNotice", "Decision-support information based on available evidence. Not legal advice.")}</span>
        </div>
      </div>

      {/* Full-Page Chatbot Instance */}
      <Chatbot mode="fullPage" jurisdiction="India" />
    </div>
  );
}
