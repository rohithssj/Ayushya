"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, ArrowRight, Globe, Menu, X, Check } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";
import { LanguageCode } from "@/i18n/translations";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { language, setLanguage, t, supportedLanguages } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const navItems = [
    { label: t("nav.home", "Home"), href: "/" },
    { label: t("nav.howItWorks", "How It Works"), href: "/#how-it-works" },
    { label: t("nav.analyzeProduct", "Analyze Product"), href: "/analyze" },
    { label: t("nav.askAyushya", "Ask AYUSHYA"), href: "/assistant" },
    { label: t("nav.humanAdvisory", "Human Advisory"), href: "/help" },
  ];

  const currentLangObj = supportedLanguages.find((l) => l.code === language) || supportedLanguages[0];

  return (
    <header className="sticky top-0 z-30 w-full bg-[#050806]/85 backdrop-blur-xl border-b border-[#D4AF37]/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-16">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-[#087F5B]/20 border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] shadow-[0_0_15px_rgba(8,127,91,0.3)] group-hover:scale-105 transition-transform">
            <Shield className="w-5 h-5 text-[#087F5B]" />
          </div>
          <div>
            <span className="font-bold text-lg tracking-wider text-[#F4F8F5] font-sans">
              AYUSHYA
            </span>
            <span className="block text-[9px] uppercase tracking-widest text-[#D4AF37] font-semibold font-mono">
              {t("nav.subtitle", "IP & Regulatory Intelligence")}
            </span>
          </div>
        </Link>

        {/* Center Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1 bg-[#0A100C] p-1.5 rounded-full border border-[#D4AF37]/20 backdrop-blur">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/" && item.href !== "/#how-it-works" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-[#087F5B] text-[#F4F8F5] border border-[#D4AF37]/40 shadow-md"
                    : "text-[#A8B5AC] hover:text-[#F4F8F5] hover:bg-white/5"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* Right CTA Actions */}
        <div className="hidden md:flex items-center gap-3">
          {/* Custom Luxury Language Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              onBlur={() => setTimeout(() => setIsDropdownOpen(false), 200)}
              className="flex items-center gap-2 text-xs bg-[#0A100C] border border-[#D4AF37]/30 hover:border-[#087F5B] rounded-full px-3 py-1.5 text-[#F4F8F5] transition-all shadow-[0_0_10px_rgba(8,127,91,0.1)] hover:shadow-[0_0_15px_rgba(8,127,91,0.3)] cursor-pointer"
              aria-label="Select Language"
            >
              <Globe className="w-3.5 h-3.5 text-[#D4AF37]" />
              <span className="font-medium text-xs text-[#F4F8F5]">{currentLangObj.nativeName}</span>
              <span className="text-[10px] text-[#D4AF37] opacity-80 font-mono">({currentLangObj.code.toUpperCase()})</span>
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-2xl bg-[#0A100C]/95 border border-[#D4AF37]/30 shadow-[0_0_30px_rgba(0,0,0,0.9)] backdrop-blur-xl py-2 z-50 animate-fade-slide-in-1">
                <div className="px-3 py-1 border-b border-[#D4AF37]/20 mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#D4AF37] font-mono">
                    Select Language / భాష / भाषा
                  </span>
                </div>
                {supportedLanguages.map((lang) => {
                  const isSelected = language === lang.code;
                  return (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setLanguage(lang.code as LanguageCode);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3.5 py-2 text-xs transition-colors cursor-pointer ${
                        isSelected
                          ? "bg-[#087F5B]/30 text-[#D4AF37] font-bold border-l-2 border-[#D4AF37]"
                          : "text-[#A8B5AC] hover:text-[#F4F8F5] hover:bg-white/5"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span>{lang.nativeName}</span>
                        <span className="text-[10px] text-[#718078] font-mono">({lang.name})</span>
                      </div>
                      {isSelected && <Check className="w-3.5 h-3.5 text-[#D4AF37]" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Primary CTA Button */}
          <Link
            href="/analyze"
            className="btn-primary-glow inline-flex items-center gap-2 px-4.5 py-2 rounded-full text-xs font-bold font-sans tracking-wide"
          >
            <span>{t("nav.startAnalysis", "Start Analysis")}</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#D4AF37]" />
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 text-[#A8B5AC] hover:text-[#D4AF37] rounded-lg"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="w-6 h-6 text-[#D4AF37]" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#050806] border-b border-[#D4AF37]/20 px-4 py-4 space-y-3">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl text-sm font-medium text-[#A8B5AC] hover:text-[#D4AF37] hover:bg-white/5"
            >
              {item.label}
            </Link>
          ))}

          {/* Mobile Language Selector */}
          <div className="pt-3 border-t border-[#D4AF37]/20 space-y-2">
            <span className="text-xs font-bold text-[#D4AF37] flex items-center gap-1.5 font-mono">
              <Globe className="w-3.5 h-3.5 text-[#087F5B]" />
              {t("nav.language", "Language")}:
            </span>
            <div className="grid grid-cols-3 gap-2">
              {supportedLanguages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setLanguage(lang.code as LanguageCode);
                  }}
                  className={`py-2 px-2 rounded-xl text-xs font-semibold text-center border transition-all ${
                    language === lang.code
                      ? "bg-[#087F5B] border-[#D4AF37] text-white shadow-md"
                      : "bg-[#0A100C] border-[#D4AF37]/20 text-[#A8B5AC]"
                  }`}
                >
                  {lang.nativeName}
                </button>
              ))}
            </div>
          </div>

          <Link
            href="/analyze"
            onClick={() => setMobileMenuOpen(false)}
            className="w-full btn-primary-glow flex items-center justify-center gap-2 py-2.5 text-xs font-bold rounded-xl text-center mt-2"
          >
            <span>{t("nav.startAnalysis", "Start Analysis")}</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#D4AF37]" />
          </Link>
        </div>
      )}
    </header>
  );
};
