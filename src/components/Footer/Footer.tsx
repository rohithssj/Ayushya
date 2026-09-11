"use client";

import React from "react";
import Link from "next/link";
import { Shield, ExternalLink, Scale, Sparkles } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export const Footer: React.FC = () => {
  const { t } = useLanguage();

  return (
    <footer className="w-full border-t border-[rgba(212,175,55,0.18)] bg-[#040705] text-[#A3B3A9] text-xs py-14 px-4 sm:px-6 relative z-20">
      {/* Top subtle ambient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 max-w-4xl h-px bg-gradient-to-r from-transparent via-[#D4AF37]/40 to-transparent" />

      <div className="max-w-7xl mx-auto space-y-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Brand Info */}
          <div className="space-y-4 md:col-span-2">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#087F5B]/30 to-[#040705] border border-[#D4AF37]/35 flex items-center justify-center text-[#10B981] shadow-[0_0_15px_rgba(8,127,91,0.2)]">
                <Shield className="w-4.5 h-4.5" />
              </div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg text-[#F4F8F5] tracking-wider font-display">
                  AYUSHYA
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#087F5B]/20 text-[#34D399] border border-[#087F5B]/40 font-bold">
                  v1.0
                </span>
              </div>
            </div>
            <p className="text-xs text-[#A3B3A9] max-w-md leading-relaxed">
              {t(
                "footer.desc",
                "AI-Powered Intellectual Property & Regulatory Intelligence for Ayurveda. Grounded in authoritative Indian statutes, FSSAI regulations, AYUSH guidelines, and WIPO Nagoya protocol frameworks."
              )}
            </p>
            <div className="flex items-center gap-3 pt-2 text-[11px] text-[#6C7D73] font-mono">
              <span className="flex items-center gap-1.5 text-[#34D399]">
                <Sparkles className="w-3 h-3" />
                RAG Sourced Intelligence
              </span>
              <span>•</span>
              <span className="flex items-center gap-1.5 text-[#D4AF37]">
                <Scale className="w-3 h-3" />
                Statutory Verified
              </span>
            </div>
          </div>

          {/* Quick Navigation */}
          <div className="space-y-3">
            <h4 className="font-bold text-[#F3E5AB] uppercase tracking-wider text-[11px] font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#087F5B]" />
              {t("footer.navHeader", "Platform Navigation")}
            </h4>
            <ul className="space-y-2.5 text-xs">
              <li>
                <Link href="/" className="hover:text-[#F4F8F5] hover:translate-x-1 inline-flex items-center gap-1.5 transition-all text-[#A3B3A9]">
                  <span>{t("footer.navHome", "Home & Overview")}</span>
                </Link>
              </li>
              <li>
                <Link href="/analyze" className="hover:text-[#F4F8F5] hover:translate-x-1 inline-flex items-center gap-1.5 transition-all text-[#A3B3A9]">
                  <span>{t("footer.navAnalyzer", "Formulation Analyzer")}</span>
                </Link>
              </li>
              <li>
                <Link href="/assistant" className="hover:text-[#F4F8F5] hover:translate-x-1 inline-flex items-center gap-1.5 transition-all text-[#A3B3A9]">
                  <span>{t("footer.navAssistant", "Ask AYUSHYA AI Assistant")}</span>
                </Link>
              </li>
              <li>
                <Link href="/help" className="hover:text-[#F4F8F5] hover:translate-x-1 inline-flex items-center gap-1.5 transition-all text-[#A3B3A9]">
                  <span>{t("footer.navHelp", "Human Legal Advisory")}</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Key Legal Sources */}
          <div className="space-y-3">
            <h4 className="font-bold text-[#F3E5AB] uppercase tracking-wider text-[11px] font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]" />
              {t("footer.statutoryHeader", "Statutory Frameworks")}
            </h4>
            <ul className="space-y-2.5 text-xs font-mono">
              <li>
                <a
                  href="https://ipindia.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#F3E5AB] flex items-center justify-between group transition-colors"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform">Patents Act 1970 §3(p)</span>
                  <ExternalLink className="w-3 h-3 text-[#6C7D73] group-hover:text-[#D4AF37] transition-colors" />
                </a>
              </li>
              <li>
                <a
                  href="https://nbaindia.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#F3E5AB] flex items-center justify-between group transition-colors"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform">Biological Diversity Act 2002</span>
                  <ExternalLink className="w-3 h-3 text-[#6C7D73] group-hover:text-[#D4AF37] transition-colors" />
                </a>
              </li>
              <li>
                <a
                  href="https://www.fssai.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#F3E5AB] flex items-center justify-between group transition-colors"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform">FSSAI Ayurveda-Aahar 2022</span>
                  <ExternalLink className="w-3 h-3 text-[#6C7D73] group-hover:text-[#D4AF37] transition-colors" />
                </a>
              </li>
              <li>
                <a
                  href="https://ayush.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[#F3E5AB] flex items-center justify-between group transition-colors"
                >
                  <span className="group-hover:translate-x-0.5 transition-transform">Drugs & Cosmetics Rules 1945</span>
                  <ExternalLink className="w-3 h-3 text-[#6C7D73] group-hover:text-[#D4AF37] transition-colors" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer & Bottom Rights */}
        <div className="pt-8 border-t border-[rgba(212,175,55,0.14)] flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-[#6C7D73]">
          <p className="max-w-2xl leading-relaxed">
            <strong className="text-[#D4AF37] font-semibold">Legal Notice:</strong>{" "}
            {t(
              "footer.legalNotice",
              "AYUSHYA provides decision-support information based on retrieved statutory evidence and is not a substitute for professional legal or regulatory advice."
            )}
          </p>
          <div className="shrink-0 flex items-center gap-2 font-mono text-[#D4AF37]">
            <span>&copy; 2026 AYUSHYA</span>
            <span>•</span>
            <span className="text-[#A3B3A9]">{t("footer.rights", "All Rights Reserved")}</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
