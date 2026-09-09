"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Globe, ArrowRight, ShieldAlert, Plus, Trash2, Cpu, CheckCircle2, Loader2 } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

interface Ingredient {
  name: string;
  quantity: string;
  unit: string;
}

export default function AnalyzeProductPage() {
  const router = useRouter();
  const { t } = useLanguage();

  const [jurisdiction, setJurisdiction] = useState("India");
  const [productName, setProductName] = useState("Ashwagandha Wellness Tablet");
  const [form, setForm] = useState("Tablet");
  const [category, setCategory] = useState("Ayurveda-Aahar");
  const [description, setDescription] = useState(
    "Standardized extract formulation targeted for stress reduction and immunity enhancement using traditional processing methods."
  );

  const [ingredients, setIngredients] = useState<Ingredient[]>([
    { name: "Ashwagandha (Withania somnifera)", quantity: "500", unit: "mg" },
    { name: "Pipali (Piper longum)", quantity: "50", unit: "mg" },
    { name: "Black Pepper", quantity: "25", unit: "mg" },
  ]);

  const [isProcessing, setIsProcessing] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  const processingSteps = [
    t("analyze.processing.step1", "Analyzing product formulation..."),
    t("analyze.processing.step2", "Structuring product classification..."),
    t("analyze.processing.step3", "Mapping relevant regulatory frameworks..."),
    t("analyze.processing.step4", "Scanning applicable IP areas & Section 3(p)..."),
    t("analyze.processing.step5", "Preparing statutory source templates..."),
    t("analyze.processing.step6", "Preparing demo results..."),
  ];

  const handleAddIngredient = () => {
    setIngredients([...ingredients, { name: "", quantity: "", unit: "mg" }]);
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleIngredientChange = (index: number, field: keyof Ingredient, value: string) => {
    const updated = [...ingredients];
    updated[index][field] = value;
    setIngredients(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsProcessing(true);
    setStepIndex(0);
  };

  useEffect(() => {
    if (!isProcessing) return;

    const interval = setInterval(() => {
      setStepIndex((prev) => {
        if (prev < processingSteps.length - 1) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            // TODO: Replace query-based analysis data with backend analysis ID once /api/analyze is implemented.
            const analysisId = encodeURIComponent(productName.toLowerCase().replace(/[^a-z0-9]+/g, "-"));
            router.push(
              `/analysis/${analysisId}?jurisdiction=${encodeURIComponent(jurisdiction)}&category=${encodeURIComponent(
                category
              )}&name=${encodeURIComponent(productName)}`
            );
          }, 800);
          return prev;
        }
      });
    }, 600);

    return () => clearInterval(interval);
  }, [isProcessing, productName, jurisdiction, category, router, processingSteps.length]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8 relative">
      {/* Page Title */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#0A100C] border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-mono font-semibold tracking-wide">
          <Sparkles className="w-3.5 h-3.5 text-[#087F5B]" />
          <span>{t("analyze.tag", "Product Formulation Analysis")}</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#F4F8F5] tracking-tight font-sans">
          {t("analyze.title", "Analyze Product Formulation")}
        </h1>
        <p className="text-sm text-[#A8B5AC] max-w-xl mx-auto">
          {t(
            "analyze.subtitle",
            "Submit your product details for preliminary AI-assisted classification, Section 3(p) TK checks, and regulatory compliance identification."
          )}
        </p>
      </div>

      {/* Main Enterprise Form Container */}
      <form onSubmit={handleSubmit} className="p-6 sm:p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/20 shadow-2xl space-y-8 backdrop-blur-xl">
        {/* Section 1: Jurisdiction Selector */}
        <div className="space-y-3">
          <label className="block text-xs font-bold text-[#D4AF37] uppercase tracking-wider font-mono flex items-center gap-2">
            <Globe className="w-4 h-4 text-[#087F5B]" />
            {t("analyze.jurisdictionLabel", "Target Jurisdiction")}
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            {["India", "International", "United States", "European Union", "Japan"].map((j) => (
              <button
                type="button"
                key={j}
                onClick={() => setJurisdiction(j)}
                className={`px-3 py-2.5 rounded-xl text-xs font-semibold border text-center transition-all ${
                  jurisdiction === j
                    ? "bg-[#087F5B] border-[#D4AF37] text-white shadow-[0_0_15px_rgba(8,127,91,0.3)]"
                    : "bg-[#050806] border-[#D4AF37]/20 text-[#A8B5AC] hover:text-[#F4F8F5]"
                }`}
              >
                {j}
              </button>
            ))}
          </div>
        </div>

        {/* Section 2: Product Information */}
        <div className="space-y-4 pt-4 border-t border-[#D4AF37]/20">
          <h3 className="text-sm font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
            {t("analyze.section1", "1. Product Information")}
          </h3>

          <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A8B5AC]">{t("analyze.productNameLabel", "Product Name")}</label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                required
                className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all font-sans"
                placeholder={t("analyze.productNamePlaceholder", "e.g. Ashwagandha Wellness Tablet")}
              />
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A8B5AC]">{t("analyze.productFormLabel", "Product Form")}</label>
              <select
                value={form}
                onChange={(e) => setForm(e.target.value)}
                className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
              >
                <option value="Tablet">Tablet</option>
                <option value="Capsule">Capsule</option>
                <option value="Syrup / Churna">Syrup / Churna</option>
                <option value="Oil / Taila">Oil / Taila</option>
                <option value="Cosmetic Cream">Cosmetic Cream</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A8B5AC]">{t("analyze.categoryLabel", "Target Classification Category")}</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
            >
              <option value="Ayurveda-Aahar">Ayurveda-Aahar (Nutraceutical Food)</option>
              <option value="Proprietary ASU Medicine">Proprietary ASU Medicine</option>
              <option value="Classical Formulation">Classical Formulation</option>
              <option value="Phytopharmaceutical">Phytopharmaceutical</option>
              <option value="Ayurvedic Cosmetic">Ayurvedic Cosmetic</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A8B5AC]">{t("analyze.descriptionLabel", "Product Description & Processing Method")}</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="w-full bg-[#050806] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all font-sans"
              placeholder={t("analyze.descriptionPlaceholder", "Describe processing method, intended use, solvent extraction ratios...")}
            />
          </div>
        </div>

        {/* Section 3: Dynamic Ingredients Table */}
        <div className="space-y-4 pt-4 border-t border-[#D4AF37]/20">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
              {t("analyze.section2", "2. Formulation Ingredients")}
            </h3>
            <button
              type="button"
              onClick={handleAddIngredient}
              className="inline-flex items-center gap-1 text-xs font-bold text-[#D4AF37] bg-[#087F5B]/20 hover:bg-[#087F5B]/40 px-3 py-1.5 rounded-lg border border-[#D4AF37]/30 transition-colors"
            >
              <Plus className="w-3.5 h-3.5 text-[#087F5B]" />
              <span>{t("analyze.addIngredient", "Add Ingredient")}</span>
            </button>
          </div>

          <div className="overflow-x-auto rounded-xl border border-[#D4AF37]/20 bg-[#050806]">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#0F1813] text-[#D4AF37] uppercase tracking-wider font-mono text-[11px] border-b border-[#D4AF37]/20">
                <tr>
                  <th className="p-3">{t("analyze.table.ingredient", "Ingredient Name")}</th>
                  <th className="p-3 w-28">{t("analyze.table.quantity", "Quantity")}</th>
                  <th className="p-3 w-24">{t("analyze.table.unit", "Unit")}</th>
                  <th className="p-3 w-12 text-center">{t("analyze.table.action", "Action")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D4AF37]/10 text-[#F4F8F5]">
                {ingredients.map((ing, idx) => (
                  <tr key={idx} className="hover:bg-white/5">
                    <td className="p-2.5">
                      <input
                        type="text"
                        value={ing.name}
                        onChange={(e) => handleIngredientChange(idx, "name", e.target.value)}
                        placeholder={t("analyze.table.placeholderName", "Herbal name (botanical or classical)")}
                        required
                        className="w-full bg-transparent border-none text-xs text-[#F4F8F5] focus:outline-none placeholder-[#718078]"
                      />
                    </td>
                    <td className="p-2.5">
                      <input
                        type="text"
                        value={ing.quantity}
                        onChange={(e) => handleIngredientChange(idx, "quantity", e.target.value)}
                        placeholder="500"
                        required
                        className="w-full bg-transparent border-none text-xs text-[#F4F8F5] focus:outline-none placeholder-[#718078]"
                      />
                    </td>
                    <td className="p-2.5">
                      <select
                        value={ing.unit}
                        onChange={(e) => handleIngredientChange(idx, "unit", e.target.value)}
                        className="bg-[#0A100C] text-[#F4F8F5] border border-[#D4AF37]/20 rounded px-2 py-1 text-xs cursor-pointer"
                      >
                        <option value="mg">mg</option>
                        <option value="g">g</option>
                        <option value="ml">ml</option>
                        <option value="%">% w/w</option>
                      </select>
                    </td>
                    <td className="p-2.5 text-center">
                      {ingredients.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveIngredient(idx)}
                          className="p-1 text-[#718078] hover:text-[#D4AF37] transition-colors"
                          title="Remove ingredient"
                        >
                          <Trash2 className="w-4 h-4 text-[#D4AF37]" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legal Disclaimer */}
        <div className="p-4 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/30 flex items-start gap-3 text-xs text-[#D4AF37]">
          <ShieldAlert className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />
          <span>
            <strong>{t("analyze.disclaimerTitle", "Preliminary AI Notice:")}</strong> {t("analyze.disclaimerBody", "Classifications generated by AYUSHYA are preliminary decision-support assessments grounded in available statutory text and subject to verification against official Gazette notifications.")}
          </span>
        </div>

        {/* Submit Primary Button */}
        <button
          type="submit"
          className="w-full btn-primary-glow py-4 px-6 rounded-2xl text-white font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition-all cursor-pointer"
        >
          <CheckCircle2 className="w-5 h-5 text-[#D4AF37]" />
          <span>{t("analyze.submitBtn", "Analyze Product →")}</span>
        </button>
      </form>

      {/* RAG Processing Screen Modal */}
      {isProcessing && (
        <div className="fixed inset-0 z-50 bg-[#050806]/95 backdrop-blur-2xl flex items-center justify-center p-4 animate-fade-slide-in-1">
          <div className="w-full max-w-md p-8 rounded-3xl bg-[#0A100C] border border-[#D4AF37]/40 shadow-[0_0_80px_rgba(8,127,91,0.3)] space-y-6 text-center">
            {/* Animated AYUSHYA AI Node Spinner */}
            <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-2 border-[#D4AF37]/30 border-t-[#087F5B] animate-spin" />
              <div className="w-14 h-14 rounded-2xl bg-[#087F5B] border border-[#D4AF37] flex items-center justify-center text-[#D4AF37] shadow-[0_0_20px_rgba(8,127,91,0.5)]">
                <Cpu className="w-7 h-7 animate-pulse text-[#D4AF37]" />
              </div>
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-extrabold text-[#F4F8F5] font-sans">
                {t("analyze.processing.title", "AYUSHYA Demo Processing")}
              </h3>
              <p className="text-xs text-[#D4AF37] font-mono">
                {t("analyze.processing.preparing", "Preparing demo analysis for")} &ldquo;{productName}&rdquo;
              </p>
            </div>

            {/* Checklist Steps Animation */}
            <div className="space-y-2.5 text-left border-t border-[#D4AF37]/20 pt-4">
              {processingSteps.map((stepText, idx) => {
                const isDone = idx < stepIndex;
                const isCurrent = idx === stepIndex;

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-3 text-xs p-2.5 rounded-xl transition-all ${
                      isDone
                        ? "text-[#D4AF37] bg-[#0F1813]"
                        : isCurrent
                        ? "text-[#F4F8F5] font-bold bg-[#087F5B] border border-[#D4AF37]/40 shadow-md"
                        : "text-[#718078]"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-[#D4AF37] shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-[#D4AF37] animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-[#D4AF37]/30 shrink-0 flex items-center justify-center text-[9px] font-mono">
                        ○
                      </span>
                    )}
                    <span className="truncate">{stepText}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
