"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  Globe,
  ArrowRight,
  ShieldAlert,
  Plus,
  Trash2,
  Cpu,
  CheckCircle2,
  Loader2,
  Scale,
  AlertTriangle,
} from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";
import { submitProductAnalysis } from "@/services/analysisService";
import type { IngredientInput } from "@/features/rag/types/analysis_api";
import type { Jurisdiction } from "@/features/rag/types/retrieval_api";

export default function AnalyzeProductPage() {
  const router = useRouter();
  const { t } = useLanguage();

  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>("India");
  const [productName, setProductName] = useState("Ashwagandha Wellness Tablet");
  const [form, setForm] = useState("Tablet");
  const [category, setCategory] = useState("Ayurveda-Aahar");
  const [description, setDescription] = useState(
    "Standardized extract formulation targeted for stress reduction and immunity enhancement using traditional processing methods."
  );

  const [ingredients, setIngredients] = useState<IngredientInput[]>([
    { name: "Ashwagandha (Withania somnifera)", quantity: "500", unit: "mg" },
    { name: "Pipali (Piper longum)", quantity: "50", unit: "mg" },
    { name: "Black Pepper", quantity: "25", unit: "mg" },
  ]);

  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const realProcessingStages = [
    t("analyze.processing.step1", "Submitting product formulation..."),
    t("analyze.processing.step2", "Running targeted statutory retrieval..."),
    t("analyze.processing.step3", "Evaluating legal evidence & regulatory standards..."),
    t("analyze.processing.step4", "Generating grounded intelligence analysis..."),
  ];

  const handleAddIngredient = () => {
    setIngredients([...ingredients, { name: "", quantity: "", unit: "mg" }]);
  };

  const handleRemoveIngredient = (index: number) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleIngredientChange = (index: number, field: keyof IngredientInput, value: string) => {
    const updated = [...ingredients];
    updated[index][field] = value;
    setIngredients(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsProcessing(true);
    setProcessingStage(0);

    try {
      setProcessingStage(1);
      const result = await submitProductAnalysis({
        productName: productName.trim(),
        category,
        form,
        description: description.trim(),
        ingredients: ingredients.filter((i) => i.name.trim().length > 0),
        jurisdiction,
      });

      setProcessingStage(realProcessingStages.length - 1);
      router.push(`/analysis/${result.id}?jurisdiction=${encodeURIComponent(jurisdiction)}&category=${encodeURIComponent(category)}&name=${encodeURIComponent(productName)}`);
    } catch (err: unknown) {
      setIsProcessing(false);
      const msg = err instanceof Error ? err.message : "Failed to analyze formulation. Please try again.";
      setErrorMessage(msg);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-10 relative">
      {/* Background ambient light */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#087F5B]/15 blur-[120px] pointer-events-none -z-10" />

      {/* Page Title Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#080D0A] border border-[#D4AF37]/35 text-[#F3E5AB] text-xs font-mono font-semibold tracking-wide shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-[#10B981]" />
          <span>{t("analyze.tag", "Product Formulation Analysis")}</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-[#F4F8F5] tracking-tight font-display">
          {t("analyze.title", "Analyze Product Formulation")}
        </h1>
        <p className="text-sm text-[#A3B3A9] max-w-xl mx-auto leading-relaxed">
          {t(
            "analyze.subtitle",
            "Submit your product details for preliminary AI-assisted classification, traditional-knowledge checks, and regulatory compliance identification grounded in authoritative legal sources."
          )}
        </p>
      </div>

      {/* Error Message Display */}
      {errorMessage && (
        <div className="p-4 rounded-2xl bg-red-950/40 border border-red-500/50 flex items-start gap-3 text-xs text-red-200 animate-fade-slide-in-1">
          <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold font-mono uppercase">Analysis Error</p>
            <p className="font-sans">{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Main Enterprise Form Container */}
      <form
        onSubmit={handleSubmit}
        className="p-6 sm:p-10 rounded-3xl bg-[#090F0B]/90 border border-[rgba(212,175,55,0.2)] shadow-2xl space-y-8 backdrop-blur-2xl"
      >
        {/* Section 1: Jurisdiction Selector */}
        <div className="space-y-3">
          <label className="block text-xs font-bold text-[#F3E5AB] uppercase tracking-wider font-mono flex items-center gap-2">
            <Globe className="w-4 h-4 text-[#10B981]" />
            <span>{t("analyze.jurisdictionLabel", "Target Jurisdiction")}</span>
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg">
            {(["India", "International"] as Jurisdiction[]).map((j) => (
              <button
                type="button"
                key={j}
                onClick={() => setJurisdiction(j)}
                className={`px-4 py-3 rounded-xl text-xs font-bold border text-center transition-all cursor-pointer ${
                  jurisdiction === j
                    ? "bg-gradient-to-r from-[#087F5B] to-[#059669] border-[#D4AF37] text-white shadow-[0_0_20px_rgba(8,127,91,0.35)] scale-[1.02]"
                    : "bg-[#050806] border-[rgba(212,175,55,0.18)] text-[#A3B3A9] hover:text-[#F4F8F5] hover:border-[#D4AF37]/40"
                }`}
              >
                {j === "India" ? "🇮🇳 India (Acts & AYUSH Rules)" : "🌍 International (CBD/TRIPS/PCT)"}
              </button>
            ))}
          </div>
        </div>

        {/* Section 2: Product Information */}
        <div className="space-y-5 pt-6 border-t border-[rgba(212,175,55,0.18)]">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-lg bg-[#087F5B]/20 border border-[#D4AF37]/30 flex items-center justify-center text-[11px] font-bold text-[#F3E5AB] font-mono">
              01
            </span>
            <h3 className="text-sm font-bold text-[#F3E5AB] uppercase tracking-wider font-mono">
              {t("analyze.section1", "1. Product Information")}
            </h3>
          </div>

          <div className="grid sm:grid-cols-2 gap-5">
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A3B3A9]">
                {t("analyze.productNameLabel", "Product Name")}
              </label>
              <input
                type="text"
                value={productName}
                onChange={(e) => setProductName(e.target.value)}
                required
                className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all font-sans"
                placeholder={t("analyze.productNamePlaceholder", "e.g. Ashwagandha Wellness Tablet")}
              />
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-semibold text-[#A3B3A9]">
                {t("analyze.productFormLabel", "Product Form")}
              </label>
              <select
                value={form}
                onChange={(e) => setForm(e.target.value)}
                className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
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
            <label className="block text-xs font-semibold text-[#A3B3A9]">
              {t("analyze.categoryLabel", "Target Classification Category")}
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] focus:outline-none transition-all cursor-pointer font-sans"
            >
              <option value="Ayurveda-Aahar">Ayurveda-Aahar (FSSAI Regulations 2022)</option>
              <option value="Proprietary ASU Medicine">Proprietary ASU Medicine (Drugs & Cosmetics Act)</option>
              <option value="Classical Formulation">Classical Formulation (Authoritative Ayurvedic Texts)</option>
              <option value="Phytopharmaceutical">Phytopharmaceutical (Standardized Extracts)</option>
              <option value="Ayurvedic Cosmetic">Ayurvedic Cosmetic (Schedule S / Cosmetics Rules)</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-[#A3B3A9]">
              {t("analyze.descriptionLabel", "Product Description & Processing Method")}
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              className="w-full bg-[#050806] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-xl px-4 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all font-sans"
              placeholder={t("analyze.descriptionPlaceholder", "Describe processing method, intended use, solvent extraction ratios...")}
            />
          </div>
        </div>

        {/* Section 3: Dynamic Ingredients Table */}
        <div className="space-y-4 pt-6 border-t border-[rgba(212,175,55,0.18)]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-[#087F5B]/20 border border-[#D4AF37]/30 flex items-center justify-center text-[11px] font-bold text-[#F3E5AB] font-mono">
                02
              </span>
              <h3 className="text-sm font-bold text-[#F3E5AB] uppercase tracking-wider font-mono">
                {t("analyze.section2", "2. Formulation Ingredients")}
              </h3>
            </div>
            <button
              type="button"
              onClick={handleAddIngredient}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-[#F3E5AB] bg-[#087F5B]/20 hover:bg-[#087F5B]/35 px-3.5 py-1.5 rounded-xl border border-[#D4AF37]/35 transition-all cursor-pointer shadow-sm active:scale-95"
            >
              <Plus className="w-3.5 h-3.5 text-[#10B981]" />
              <span>{t("analyze.addIngredient", "Add Ingredient")}</span>
            </button>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-[rgba(212,175,55,0.2)] bg-[#050806]">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#090F0B] text-[#F3E5AB] uppercase tracking-wider font-mono text-[11px] border-b border-[rgba(212,175,55,0.18)]">
                <tr>
                  <th className="p-3.5">{t("analyze.table.ingredient", "Ingredient Name")}</th>
                  <th className="p-3.5 w-32">{t("analyze.table.quantity", "Quantity")}</th>
                  <th className="p-3.5 w-28">{t("analyze.table.unit", "Unit")}</th>
                  <th className="p-3.5 w-14 text-center">{t("analyze.table.action", "Action")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(212,175,55,0.1)] text-[#F4F8F5]">
                {ingredients.map((ing, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.03] transition-colors">
                    <td className="p-3">
                      <input
                        type="text"
                        value={ing.name}
                        onChange={(e) => handleIngredientChange(idx, "name", e.target.value)}
                        placeholder={t("analyze.table.placeholderName", "Herbal name (botanical or classical)")}
                        required
                        className="w-full bg-transparent border-none text-xs text-[#F4F8F5] focus:outline-none placeholder-[#6C7D73] font-medium"
                      />
                    </td>
                    <td className="p-3">
                      <input
                        type="text"
                        value={ing.quantity}
                        onChange={(e) => handleIngredientChange(idx, "quantity", e.target.value)}
                        placeholder="500"
                        required
                        className="w-full bg-transparent border-none text-xs text-[#F4F8F5] focus:outline-none placeholder-[#6C7D73] font-mono"
                      />
                    </td>
                    <td className="p-3">
                      <select
                        value={ing.unit}
                        onChange={(e) => handleIngredientChange(idx, "unit", e.target.value)}
                        className="bg-[#090F0B] text-[#F4F8F5] border border-[rgba(212,175,55,0.2)] rounded-lg px-2.5 py-1 text-xs cursor-pointer font-mono"
                      >
                        <option value="mg">mg</option>
                        <option value="g">g</option>
                        <option value="ml">ml</option>
                        <option value="%">% w/w</option>
                      </select>
                    </td>
                    <td className="p-3 text-center">
                      {ingredients.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveIngredient(idx)}
                          className="p-1.5 text-[#6C7D73] hover:text-[#EF4444] hover:bg-white/[0.05] rounded-lg transition-colors cursor-pointer"
                          title="Remove ingredient"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div className="p-4 rounded-2xl bg-[#090F0B] border border-[#D4AF37]/25 flex items-start gap-3 text-xs text-[#F3E5AB]">
          <ShieldAlert className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />
          <span className="leading-relaxed">
            <strong className="text-[#D4AF37] font-semibold">{t("analyze.disclaimerTitle", "Preliminary AI Notice:")}</strong>{" "}
            <span className="text-[#A3B3A9]">
              {t(
                "analyze.disclaimerBody",
                "Classifications generated by AYUSHYA are preliminary decision-support assessments grounded in retrieved statutory evidence and subject to verification against official Gazette notifications."
              )}
            </span>
          </span>
        </div>

        {/* Submit Primary Button */}
        <button
          type="submit"
          disabled={isProcessing}
          className="w-full btn-primary-glow py-4 px-6 rounded-2xl text-white font-bold text-sm shadow-2xl flex items-center justify-center gap-2.5 transition-all cursor-pointer group tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Scale className="w-5 h-5 text-[#F3E5AB]" />
          <span>{t("analyze.submitBtn", "Analyze Product →")}</span>
          <ArrowRight className="w-4 h-4 text-[#F3E5AB] group-hover:translate-x-1 transition-transform" />
        </button>
      </form>

      {/* RAG Processing Screen Modal */}
      {isProcessing && (
        <div className="fixed inset-0 z-50 bg-[#040705]/90 backdrop-blur-2xl flex items-center justify-center p-4 animate-fade-slide-in-1">
          <div className="w-full max-w-md p-8 sm:p-10 rounded-3xl bg-[#080D0A] border border-[#D4AF37]/40 shadow-[0_0_80px_rgba(8,127,91,0.35)] space-y-6 text-center">
            {/* Animated AYUSHYA AI Node Spinner */}
            <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full border-2 border-[#D4AF37]/30 border-t-[#10B981] animate-spin" />
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#087F5B] to-[#040705] border border-[#D4AF37] flex items-center justify-center text-[#D4AF37] shadow-[0_0_25px_rgba(8,127,91,0.6)]">
                <Cpu className="w-7 h-7 animate-pulse text-[#34D399]" />
              </div>
            </div>

            <div className="space-y-1.5">
              <h3 className="text-xl font-extrabold text-[#F4F8F5] font-display">
                {t("analyze.processing.title", "AYUSHYA Legal Intelligence")}
              </h3>
              <p className="text-xs text-[#D4AF37] font-mono">
                {t("analyze.processing.preparing", "Analyzing formulation for")} &ldquo;{productName}&rdquo;
              </p>
            </div>

            {/* Real Checklist Stages Animation */}
            <div className="space-y-2.5 text-left border-t border-[rgba(212,175,55,0.18)] pt-5">
              {realProcessingStages.map((stepText, idx) => {
                const isDone = idx < processingStage;
                const isCurrent = idx === processingStage;

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-3 text-xs p-3 rounded-xl transition-all ${
                      isDone
                        ? "text-[#34D399] bg-[#0D1611] border border-[#087F5B]/30"
                        : isCurrent
                        ? "text-[#F4F8F5] font-bold bg-gradient-to-r from-[#087F5B] to-[#059669] border border-[#D4AF37]/50 shadow-lg"
                        : "text-[#6C7D73]"
                    }`}
                  >
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-[#10B981] shrink-0" />
                    ) : isCurrent ? (
                      <Loader2 className="w-4 h-4 text-[#F3E5AB] animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-[rgba(212,175,55,0.3)] shrink-0 flex items-center justify-center text-[9px] font-mono">
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
