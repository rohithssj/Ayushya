"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { MessageSquare, X, ArrowRight, LifeBuoy } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export const SupportBox: React.FC = () => {
  const { t } = useLanguage();
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    // Automatically minimize on small screens to prevent covering mobile UI
    if (typeof window !== "undefined" && window.innerWidth < 640) {
      setIsMinimized(true);
    }
  }, []);

  if (isMinimized) {
    return (
      <div className="fixed bottom-6 left-6 z-40 animate-fade-slide-in-1">
        <button
          onClick={() => setIsMinimized(false)}
          className="flex items-center gap-2.5 px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-full bg-[#080D0A]/95 hover:bg-[#0D1611] text-[#F3E5AB] border border-[#D4AF37]/35 shadow-[0_8px_25px_rgba(0,0,0,0.7),0_0_15px_rgba(8,127,91,0.2)] backdrop-blur-xl transition-all hover:scale-105 group cursor-pointer"
          title={t("support.title", "Need Support?")}
        >
          <div className="w-5 h-5 rounded-full bg-[#087F5B]/30 flex items-center justify-center">
            <MessageSquare className="w-3 h-3 text-[#34D399]" />
          </div>
          <span className="text-xs font-semibold text-[#F4F8F5] font-sans hidden sm:inline">
            {t("support.title", "Need Support?")}
          </span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 left-6 z-40 w-[240px] rounded-2xl bg-[#080D0A]/95 border border-[#D4AF37]/30 shadow-[0_20px_45px_rgba(0,0,0,0.85),0_0_20px_rgba(8,127,91,0.15)] backdrop-blur-2xl p-4 animate-fade-slide-in-1">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#D4AF37]/15 pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-[#087F5B]/20 border border-[#087F5B]/40 flex items-center justify-center text-[#10B981]">
            <LifeBuoy className="w-3.5 h-3.5" />
          </div>
          <h4 className="text-[11px] font-bold text-[#F3E5AB] uppercase tracking-wider font-mono">
            {t("support.title", "Need Support?")}
          </h4>
        </div>
        <button
          onClick={() => setIsMinimized(true)}
          className="p-1 text-[#A3B3A9] hover:text-[#F3E5AB] hover:bg-white/[0.06] rounded-lg transition-colors cursor-pointer"
          title="Minimize support widget"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Description */}
      <p className="text-xs text-[#A3B3A9] leading-relaxed mb-3.5">
        {t("support.desc", "Can't find what you need? Our regulatory & IP expert team can assist.")}
      </p>

      {/* CTA Button */}
      <Link
        href="/help"
        className="w-full btn-primary-glow inline-flex items-center justify-center gap-1.5 text-xs font-bold px-3.5 py-2.5 rounded-xl text-white transition-all group"
      >
        <span>{t("support.btn", "Request Human Assistance")}</span>
        <ArrowRight className="w-3.5 h-3.5 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
      </Link>
    </div>
  );
};
