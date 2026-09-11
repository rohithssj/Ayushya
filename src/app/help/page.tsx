"use client";

import React, { useState } from "react";
import { HelpCircle, CheckCircle2, ArrowRight, ShieldCheck, Scale, Award, Lock } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

export default function HumanHelpPage() {
  const { t } = useLanguage();
  const [submitted, setSubmitted] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [inquiryType, setInquiryType] = useState("Patent Eligibility & Section 3(p) Defense");
  const [details, setDetails] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-10 relative">
      {/* Background ambient light */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#087F5B]/15 blur-[120px] pointer-events-none -z-10" />

      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#080D0A] border border-[#D4AF37]/35 text-[#F3E5AB] text-xs font-mono font-semibold uppercase tracking-wider shadow-sm">
          <HelpCircle className="w-3.5 h-3.5 text-[#10B981]" />
          <span>{t("help.tag", "Human Advisory & Legal Consultation")}</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
          {t("help.title", "Request Human Legal Assistance")}
        </h1>
        <p className="text-sm text-[#A3B3A9] max-w-xl mx-auto leading-relaxed">
          {t(
            "help.subtitle",
            "When AI confidence is low or complex traditional knowledge claims require expert review, connect directly with registered IP attorneys and AYUSH regulatory consultants."
          )}
        </p>
      </div>

      {/* Trust Credibility Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {[
          { icon: Scale, label: "Registered Patent Agents", desc: "Indian Patent Office & WIPO" },
          { icon: Award, label: "AYUSH Regulatory Counsel", desc: "FSSAI & Rule 158B Specialists" },
          { icon: Lock, label: "Privileged & Confidential", desc: "Strict Attorney-Client Secrecy" },
        ].map((badge, i) => {
          const Icon = badge.icon;
          return (
            <div key={i} className="flex items-center gap-3 p-3.5 rounded-2xl bg-[#080D0A]/80 border border-[rgba(212,175,55,0.18)] shadow-sm">
              <div className="w-8 h-8 rounded-xl bg-[#087F5B]/15 border border-[#087F5B]/30 flex items-center justify-center text-[#10B981] shrink-0">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-[#F4F8F5] font-sans">{badge.label}</p>
                <p className="text-[10px] text-[#A3B3A9] font-mono">{badge.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {submitted ? (
        <div className="p-8 sm:p-14 rounded-3xl bg-[#080D0A]/95 border border-[#D4AF37]/45 text-center space-y-6 shadow-2xl animate-fade-slide-in-1 backdrop-blur-2xl">
          <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-[#087F5B] to-[#040705] text-[#F3E5AB] border border-[#D4AF37] flex items-center justify-center mx-auto text-2xl shadow-[0_0_40px_rgba(8,127,91,0.5)]">
            <CheckCircle2 className="w-10 h-10 text-[#34D399]" />
          </div>
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#F4F8F5] font-display">
              {t("help.successTitle", "Consultation Request Received")}
            </h2>
            <p className="text-sm text-[#A3B3A9] max-w-lg mx-auto leading-relaxed">
              {t("help.successMsg", "Thank you")}, <strong className="text-white">{name}</strong>. {t("help.reachOutMsg", "Our AYUSH regulatory expert team will review your inquiry regarding")}{" "}
              <strong className="text-[#F3E5AB]">{inquiryType}</strong> and reach out to <strong className="text-white">{email}</strong> within 24 business hours.
            </p>
          </div>
          <button
            onClick={() => setSubmitted(false)}
            className="btn-gold-outline px-8 py-3 rounded-full text-xs font-bold transition-all cursor-pointer shadow-md"
          >
            {t("help.submitAnother", "Submit Another Request")}
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleSubmit}
          className="p-6 sm:p-10 rounded-3xl bg-[#080D0A]/90 border border-[rgba(212,175,55,0.22)] shadow-2xl space-y-6 backdrop-blur-2xl"
        >
          <div className="grid sm:grid-cols-2 gap-5">
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A3B3A9]">{t("help.fullName", "Full Name")}</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder={t("help.fullNamePlaceholder", "e.g. Dr. Rajesh Sharma")}
                className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all font-sans"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A3B3A9]">{t("help.email", "Email Address")}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder={t("help.emailPlaceholder", "rajesh@ayurveda-labs.in")}
                className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all font-sans"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A3B3A9]">{t("help.inquiryArea", "Inquiry Area")}</label>
            <select
              value={inquiryType}
              onChange={(e) => setInquiryType(e.target.value)}
              className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
            >
              <option value="Patent Eligibility & Section 3(p) Defense">Patent Eligibility & Section 3(p) Traditional Knowledge Defense</option>
              <option value="FSSAI Ayurveda Aahar Licensing">FSSAI Ayurveda Aahar Licensing & Food Claims</option>
              <option value="NBA Biological Diversity ABS Approval">NBA Biological Diversity ABS Clearance (Form I)</option>
              <option value="International Export Regulatory Requirements">International Export Regulatory Requirements (US FDA / EU)</option>
              <option value="General AYUSH Legal Advisory">General AYUSH Legal Advisory</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A3B3A9]">{t("help.detailsLabel", "Inquiry Details & Formulation Context")}</label>
            <textarea
              rows={4}
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              required
              placeholder={t("help.detailsPlaceholder", "Describe your formulation, specific legal doubts, or low-confidence questions flagged by AYUSHYA AI...")}
              className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all font-sans"
            />
          </div>

          {/* Privacy & Data-Use Statement */}
          <div className="flex items-start gap-3 p-4 rounded-xl bg-[#050806] border border-[rgba(212,175,55,0.18)] text-xs text-[#A3B3A9]">
            <ShieldCheck className="w-4 h-4 text-[#10B981] shrink-0 mt-0.5" />
            <span className="leading-relaxed font-sans">
              {t(
                "help.privacyNotice",
                "Your information will be used only to process your support request and may be shared with the authorized AYUSHYA support team for follow-up."
              )}
            </span>
          </div>

          <button
            type="submit"
            className="w-full btn-primary-glow py-4 px-6 rounded-2xl text-white font-bold text-sm shadow-2xl flex items-center justify-center gap-2.5 transition-all cursor-pointer tracking-wider group"
          >
            <ShieldCheck className="w-5 h-5 text-[#F3E5AB]" />
            <span>{t("help.submitBtn", "Submit for Human Expert Escalation")}</span>
            <ArrowRight className="w-4 h-4 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
          </button>
        </form>
      )}
    </div>
  );
}
