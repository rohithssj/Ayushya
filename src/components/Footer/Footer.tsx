"use client";

import React from "react";
import Link from "next/link";
import { Shield, ExternalLink } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export const Footer: React.FC = () => {
  const { t } = useLanguage();

  return (
    <footer className="w-full border-t border-[#D4AF37]/20 bg-[#050806] text-[#A8B5AC] text-xs py-12 px-4 sm:px-6 relative z-10">
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Info */}
          <div className="space-y-3 md:col-span-2">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#0A100C] border border-[#D4AF37]/40 flex items-center justify-center text-[#087F5B]">
                <Shield className="w-4 h-4" />
              </div>
              <span className="font-bold text-base text-[#F4F8F5] tracking-wider font-sans">
                AYUSHYA
              </span>
            </div>
            <p className="text-xs text-[#A8B5AC] max-w-md leading-relaxed">
              {t(
                "footer.desc",
                "AI-Powered Intellectual Property & Regulatory Intelligence for Ayurveda. Grounded in authoritative Indian statutes, FSSAI regulations, AYUSH guidelines, and WIPO Nagoya protocol frameworks."
              )}
            </p>
          </div>

          {/* Quick Navigation */}
          <div className="space-y-2.5">
            <h4 className="font-bold text-[#D4AF37] uppercase tracking-wider text-[11px] font-mono">
              {t("footer.navHeader", "Platform Navigation")}
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/" className="hover:text-[#D4AF37] transition-colors">
                  {t("footer.navHome", "Home & Overview")}
                </Link>
              </li>
              <li>
                <Link href="/analyze" className="hover:text-[#D4AF37] transition-colors">
                  {t("footer.navAnalyzer", "Formulation Analyzer")}
                </Link>
              </li>
              <li>
                <Link href="/assistant" className="hover:text-[#D4AF37] transition-colors">
                  {t("footer.navAssistant", "Ask AYUSHYA AI Assistant")}
                </Link>
              </li>
              <li>
                <Link href="/help" className="hover:text-[#D4AF37] transition-colors">
                  {t("footer.navHelp", "Human Legal Advisory")}
                </Link>
              </li>
            </ul>
          </div>

          {/* Key Legal Sources */}
          <div className="space-y-2.5">
            <h4 className="font-bold text-[#D4AF37] uppercase tracking-wider text-[11px] font-mono">
              {t("footer.statutoryHeader", "Statutory Frameworks")}
            </h4>
            <ul className="space-y-2 text-xs font-mono">
              <li>
                <a href="https://ipindia.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-[#D4AF37] flex items-center gap-1">
                  <span>Patents Act 1970 §3(p)</span>
                  <ExternalLink className="w-3 h-3 text-[#718078]" />
                </a>
              </li>
              <li>
                <a href="https://nbaindia.org" target="_blank" rel="noopener noreferrer" className="hover:text-[#D4AF37] flex items-center gap-1">
                  <span>Biological Diversity Act 2002</span>
                  <ExternalLink className="w-3 h-3 text-[#718078]" />
                </a>
              </li>
              <li>
                <a href="https://www.fssai.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-[#D4AF37] flex items-center gap-1">
                  <span>FSSAI Ayurveda-Aahar 2022</span>
                  <ExternalLink className="w-3 h-3 text-[#718078]" />
                </a>
              </li>
              <li>
                <a href="https://ayush.gov.in" target="_blank" rel="noopener noreferrer" className="hover:text-[#D4AF37] flex items-center gap-1">
                  <span>Drugs & Cosmetics Rules 1945</span>
                  <ExternalLink className="w-3 h-3 text-[#718078]" />
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Disclaimer & Bottom Rights */}
        <div className="pt-6 border-t border-[#D4AF37]/20 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-[#718078]">
          <p className="max-w-2xl">
            <strong className="text-[#D4AF37]">Legal Notice:</strong> {t("footer.legalNotice", "AYUSHYA provides decision-support information based on retrieved statutory evidence and is not a substitute for professional legal or regulatory advice.")}
          </p>
          <p className="shrink-0 font-mono text-[#D4AF37]">
            &copy; 2026 AYUSHYA • {t("footer.rights", "All Rights Reserved")}
          </p>
        </div>
      </div>
    </footer>
  );
};
