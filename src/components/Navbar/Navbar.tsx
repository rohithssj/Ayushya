"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Shield, ArrowRight, Globe, Menu, X, Check, Sparkles } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";
import { LanguageCode } from "@/i18n/translations";

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const { language, setLanguage, t, supportedLanguages } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState<string>("home");

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);

      // Dynamic active section detection for homepage anchor sections
      if (pathname === "/") {
        const howItWorksEl = document.getElementById("how-it-works");
        if (howItWorksEl) {
          const rect = howItWorksEl.getBoundingClientRect();
          // Active when how-it-works is in the primary reading area of viewport
          if (rect.top <= 250 && rect.bottom >= 200) {
            setActiveSection("how-it-works");
            return;
          }
        }
        setActiveSection("home");
      } else {
        setActiveSection("");
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [pathname]);

  const navItems = [
    { label: t("nav.home", "Home"), href: "/", id: "home" },
    { label: t("nav.howItWorks", "How It Works"), href: "/#how-it-works", id: "how-it-works" },
    { label: t("nav.analyzeProduct", "Analyze Product"), href: "/analyze", id: "analyze" },
    { label: t("nav.askAyushya", "Ask AYUSHYA"), href: "/assistant", id: "assistant" },
    { label: t("nav.humanAdvisory", "Human Advisory"), href: "/help", id: "help" },
  ];

  const isItemActive = (item: (typeof navItems)[0]) => {
    if (pathname === "/") {
      if (item.id === "how-it-works") {
        return activeSection === "how-it-works";
      }
      if (item.id === "home") {
        return activeSection === "home";
      }
      return false;
    }
    return pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
  };

  const currentLangObj = supportedLanguages.find((l) => l.code === language) || supportedLanguages[0];

  return (
    <header
      className={`sticky top-0 z-50 w-full transition-all duration-300 ${
        isScrolled
          ? "bg-[#040705]/92 backdrop-blur-2xl border-b border-[rgba(212,175,55,0.25)] shadow-[0_12px_40px_rgba(0,0,0,0.85)] py-2"
          : "bg-[#040705]/65 backdrop-blur-lg border-b border-white/[0.05] shadow-none py-3"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between h-14 sm:h-16">
        {/* Brand Logo Emblem */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-br from-[#087F5B]/30 via-[#040705] to-[#040705] border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] shadow-[0_0_20px_rgba(8,127,91,0.25)] group-hover:border-[#D4AF37]/90 group-hover:scale-105 group-hover:shadow-[0_0_25px_rgba(212,175,55,0.35)] transition-all duration-300">
            <Image
              src="/ayushya-icon.svg"
              alt="AYUSHYA Brand Emblem"
              width={32}
              height={32}
              className="w-full h-full object-contain group-hover:scale-105 transition-transform"
              priority
            />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-wider text-[#F4F8F5] font-display">
                AYUSHYA
              </span>
              <span className="inline-flex items-center px-1.5 py-0.2 rounded text-[9px] font-mono font-bold bg-[#087F5B]/25 text-[#34D399] border border-[#087F5B]/50 shadow-[0_0_10px_rgba(16,185,129,0.3)]">
                AI
              </span>
            </div>
            <span className="text-[10px] uppercase tracking-widest text-[#D4AF37] font-semibold font-mono">
              {t("nav.subtitle", "IP & Regulatory Intelligence")}
            </span>
          </div>
        </Link>

        {/* Center Desktop Navigation */}
        <nav className="hidden lg:flex items-center gap-1 bg-[#090F0B]/85 p-1.5 rounded-full border border-[rgba(212,175,55,0.22)] shadow-[0_4px_20px_rgba(0,0,0,0.5)] backdrop-blur-xl">
          {navItems.map((item) => {
            const active = isItemActive(item);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative px-4 py-2 rounded-full text-xs font-semibold tracking-wide transition-all duration-300 group cursor-pointer ${
                  active
                    ? "bg-gradient-to-r from-[#087F5B] to-[#059669] text-white border border-[#D4AF37]/60 shadow-[0_2px_18px_rgba(8,127,91,0.5)] font-bold scale-[1.02]"
                    : "text-[#A3B3A9] hover:text-[#F4F8F5] hover:bg-white/[0.08]"
                }`}
              >
                <span className="relative z-10 flex items-center gap-1.5">
                  {item.label}
                  {active && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#F3E5AB] animate-pulse" />
                  )}
                </span>
                {/* Subtle active / hover micro-indicator */}
                {!active && (
                  <span className="absolute bottom-1 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-gradient-to-r from-[#10B981] via-[#34D399] to-[#D4AF37] rounded-full group-hover:w-3/5 transition-all duration-300 opacity-0 group-hover:opacity-100 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Right Actions */}
        <div className="hidden sm:flex items-center gap-3">
          {/* Custom Luxury Language Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              onBlur={() => setTimeout(() => setIsDropdownOpen(false), 250)}
              className="flex items-center gap-2 text-xs bg-[#090F0B] border border-[rgba(212,175,55,0.25)] hover:border-[#10B981] rounded-full px-3.5 py-2 text-[#F4F8F5] transition-all shadow-sm hover:shadow-[0_0_15px_rgba(16,185,129,0.25)] cursor-pointer active:scale-95"
              aria-label="Select Language"
            >
              <Globe className="w-3.5 h-3.5 text-[#D4AF37]" />
              <span className="font-medium text-xs text-[#F4F8F5]">{currentLangObj.nativeName}</span>
              <span className="text-[10px] text-[#D4AF37] opacity-90 font-mono">({currentLangObj.code.toUpperCase()})</span>
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2.5 w-52 rounded-2xl bg-[#080D0A]/95 border border-[#D4AF37]/35 shadow-[0_15px_40px_rgba(0,0,0,0.9)] backdrop-blur-2xl py-2 z-50 animate-fade-slide-in-1">
                <div className="px-3.5 py-1.5 border-b border-[#D4AF37]/15 mb-1.5">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#D4AF37] font-mono flex items-center gap-1.5">
                    <Sparkles className="w-3 h-3 text-[#10B981]" />
                    Language / భాష / भाषा
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
                      className={`w-full flex items-center justify-between px-3.5 py-2.5 text-xs transition-all cursor-pointer ${
                        isSelected
                          ? "bg-[#087F5B]/25 text-[#F3E5AB] font-bold border-l-3 border-[#D4AF37]"
                          : "text-[#A3B3A9] hover:text-[#F4F8F5] hover:bg-white/[0.06]"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-sans">{lang.nativeName}</span>
                        <span className="text-[10px] text-[#6C7D73] font-mono">({lang.name})</span>
                      </div>
                      {isSelected && <Check className="w-4 h-4 text-[#D4AF37]" />}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Primary CTA Button */}
          <Link
            href="/analyze"
            className="btn-primary-glow inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-xs font-bold tracking-wider group"
          >
            <span>{t("nav.startAnalysis", "Start Analysis")}</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="lg:hidden p-2 text-[#A3B3A9] hover:text-[#D4AF37] rounded-xl hover:bg-white/[0.05] transition-colors cursor-pointer"
          aria-label="Toggle Navigation"
        >
          {mobileMenuOpen ? <X className="w-6 h-6 text-[#D4AF37]" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-[#040705]/98 border-b border-[#D4AF37]/30 px-5 py-5 space-y-4 backdrop-blur-2xl animate-fade-slide-in-1 shadow-[0_20px_50px_rgba(0,0,0,0.9)]">
          <div className="space-y-1">
            {navItems.map((item) => {
              const active = isItemActive(item);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center justify-between px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                    active
                      ? "bg-gradient-to-r from-[#087F5B] to-[#059669] text-white border border-[#D4AF37]/50 shadow-md font-bold"
                      : "text-[#A3B3A9] hover:text-[#F4F8F5] hover:bg-white/[0.06]"
                  }`}
                >
                  <span>{item.label}</span>
                  {active && <span className="w-2 h-2 rounded-full bg-[#F3E5AB] animate-pulse" />}
                </Link>
              );
            })}
          </div>

          {/* Mobile Language Selector */}
          <div className="pt-4 border-t border-[#D4AF37]/15 space-y-2.5">
            <span className="text-xs font-bold text-[#D4AF37] flex items-center gap-2 font-mono">
              <Globe className="w-3.5 h-3.5 text-[#10B981]" />
              {t("nav.language", "Select Language")}:
            </span>
            <div className="grid grid-cols-3 gap-2">
              {supportedLanguages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setLanguage(lang.code as LanguageCode);
                  }}
                  className={`py-2.5 px-2 rounded-xl text-xs font-semibold text-center border transition-all cursor-pointer ${
                    language === lang.code
                      ? "bg-[#087F5B] border-[#D4AF37] text-white shadow-md font-bold"
                      : "bg-[#080D0A] border-[#D4AF37]/20 text-[#A3B3A9] hover:text-white"
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
            className="w-full btn-primary-glow flex items-center justify-center gap-2 py-3 text-xs font-bold rounded-xl text-center shadow-lg"
          >
            <span>{t("nav.startAnalysis", "Start Analysis")}</span>
            <ArrowRight className="w-4 h-4 text-[#F3E5AB]" />
          </Link>
        </div>
      )}
    </header>
  );
};
