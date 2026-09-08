"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MessageSquare, X, ArrowRight, LifeBuoy } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export const SupportBox: React.FC = () => {
  const { t } = useLanguage();
  const [isMinimized, setIsMinimized] = useState(false);

  if (isMinimized) {
    return (
      <div className="fixed bottom-5 left-5 z-40 animate-fade-slide-in-1">
        <button
          onClick={() => setIsMinimized(false)}
          className="flex items-center gap-2.5 px-4 py-2.5 rounded-full bg-[#0A100C]/95 hover:bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/40 shadow-[0_0_25px_rgba(8,127,91,0.25)] backdrop-blur-md transition-all hover:scale-105 group cursor-pointer"
          title={t("support.title", "Need Support?")}
        >
          <MessageSquare className="w-4 h-4 text-[#087F5B] group-hover:animate-bounce" />
          <span className="text-xs font-semibold text-[#F4F8F5] font-sans">{t("support.title", "Need Support?")}</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-5 left-5 z-40 w-[290px] sm:w-[320px] rounded-2xl bg-[#0A100C]/95 border border-[#D4AF37]/30 shadow-[0_0_40px_rgba(0,0,0,0.9)] backdrop-blur-xl p-4 animate-fade-slide-in-1">
      <div className="flex items-center justify-between border-b border-[#D4AF37]/20 pb-2.5 mb-2.5">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-[#087F5B]/20 border border-[#D4AF37]/30 flex items-center justify-center text-[#D4AF37]">
            <LifeBuoy className="w-4 h-4 text-[#087F5B]" />
          </div>
          <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
            💬 {t("support.title", "Need Support?")}
          </h4>
        </div>
        <button
          onClick={() => setIsMinimized(true)}
          className="p-1 text-[#A8B5AC] hover:text-[#D4AF37] hover:bg-white/5 rounded-lg transition-colors cursor-pointer"
          title="Minimize support widget"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <p className="text-xs text-[#A8B5AC] leading-relaxed mb-3">
        {t("support.desc", "Can't find what you need? Our regulatory & IP expert team can assist with complex formulation claims.")}
      </p>

      <Link
        href="/help"
        className="w-full btn-primary-glow inline-flex items-center justify-center gap-2 text-xs font-bold px-4 py-2.5 rounded-xl text-white transition-all"
      >
        <span>{t("support.btn", "Request Human Assistance")}</span>
        <ArrowRight className="w-3.5 h-3.5 text-[#D4AF37]" />
      </Link>
    </div>
  );
};
