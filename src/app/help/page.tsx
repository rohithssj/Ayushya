"use client";

import React, { useState } from "react";
import { HelpCircle, CheckCircle2, ArrowRight, ShieldCheck } from "lucide-react";
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
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0A100C] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-mono font-semibold uppercase tracking-wider">
          <HelpCircle className="w-3.5 h-3.5 text-[#087F5B]" />
          <span>{t("help.tag", "Human Advisory & Legal Consultation")}</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
          {t("help.title", "Request Human Legal Assistance")}
        </h1>
        <p className="text-sm text-[#A8B5AC] max-w-xl mx-auto">
          {t(
            "help.subtitle",
            "When AI confidence is low or complex traditional knowledge claims require expert review, connect directly with registered IP attorneys and AYUSH regulatory consultants."
          )}
        </p>
      </div>

      {submitted ? (
        <div className="p-8 sm:p-12 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/40 text-center space-y-4 shadow-2xl animate-fade-slide-in-1">
          <div className="w-16 h-16 rounded-full bg-[#087F5B]/20 text-[#D4AF37] border border-[#D4AF37]/50 flex items-center justify-center mx-auto text-2xl shadow-[0_0_30px_rgba(8,127,91,0.4)]">
            <CheckCircle2 className="w-8 h-8 text-[#087F5B]" />
          </div>
          <h2 className="text-2xl font-bold text-[#F4F8F5]">{t("help.successTitle", "Consultation Request Received")}</h2>
          <p className="text-sm text-[#A8B5AC] max-w-md mx-auto leading-relaxed">
            {t("help.successMsg", "Thank you")}, <strong>{name}</strong>. {t("help.reachOutMsg", "Our AYUSH regulatory expert team will review your inquiry regarding")} <strong className="text-[#D4AF37]">{inquiryType}</strong> and reach out to <strong>{email}</strong> within 24 business hours.
          </p>
          <button
            onClick={() => setSubmitted(false)}
            className="px-6 py-3 rounded-full bg-[#050806] hover:bg-white/5 text-[#D4AF37] text-xs font-bold transition-colors border border-[#D4AF37]/30 cursor-pointer"
          >
            {t("help.submitAnother", "Submit Another Request")}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/30 shadow-2xl space-y-6 backdrop-blur-xl">
          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A8B5AC]">{t("help.fullName", "Full Name")}</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder={t("help.fullNamePlaceholder", "e.g. Dr. Rajesh Sharma")}
                className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all font-sans"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A8B5AC]">{t("help.email", "Email Address")}</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder={t("help.emailPlaceholder", "rajesh@ayurveda-labs.in")}
                className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all font-sans"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A8B5AC]">{t("help.inquiryArea", "Inquiry Area")}</label>
            <select
              value={inquiryType}
              onChange={(e) => setInquiryType(e.target.value)}
              className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
            >
              <option value="Patent Eligibility & Section 3(p) Defense">Patent Eligibility & Section 3(p) Traditional Knowledge Defense</option>
              <option value="FSSAI Ayurveda Aahar Licensing">FSSAI Ayurveda Aahar Licensing & Food Claims</option>
              <option value="NBA Biological Diversity ABS Approval">NBA Biological Diversity ABS Clearance (Form I)</option>
              <option value="International Export Regulatory Requirements">International Export Regulatory Requirements (US FDA / EU)</option>
              <option value="General AYUSH Legal Advisory">General AYUSH Legal Advisory</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A8B5AC]">{t("help.detailsLabel", "Inquiry Details & Formulation Context")}</label>
            <textarea
              rows={4}
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              required
              placeholder={t("help.detailsPlaceholder", "Describe your formulation, specific legal doubts, or low-confidence questions flagged by AYUSHYA AI...")}
              className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all font-sans"
            />
          </div>

          {/* Privacy & Data-Use Statement */}
          <div className="flex items-start gap-2.5 p-3.5 rounded-xl bg-[#050806] border border-[#D4AF37]/20 text-xs text-[#A8B5AC]">
            <ShieldCheck className="w-4 h-4 text-[#087F5B] shrink-0 mt-0.5" />
            <span>
              {t(
                "help.privacyNotice",
                "Your information will be used only to process your support request and may be shared with the authorized AYUSHYA support team for follow-up."
              )}
            </span>
          </div>

          <button
            type="submit"
            className="w-full btn-primary-glow py-4 px-6 rounded-2xl text-white font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <ShieldCheck className="w-5 h-5 text-[#D4AF37]" />
            <span>{t("help.submitBtn", "Submit for Human Expert Escalation")}</span>
            <ArrowRight className="w-4 h-4 text-[#D4AF37]" />
          </button>
        </form>
      )}
    </div>
  );
}
