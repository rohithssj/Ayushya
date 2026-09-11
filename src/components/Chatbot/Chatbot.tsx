"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { sendChatMessage, ChatMessageData } from "@/services/chatService";
import { Bot, X, Sparkles, RefreshCw, Globe, AlertCircle, HelpCircle, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useLanguage } from "@/i18n/LanguageContext";

export interface ChatbotProps {
  mode?: "floating" | "fullPage";
  analysisId?: string;
  productName?: string;
  jurisdiction?: string;
  onClose?: () => void;
}

export const Chatbot: React.FC<ChatbotProps> = ({
  mode = "floating",
  analysisId,
  productName,
  jurisdiction = "India",
  onClose,
}) => {
  const { language, t } = useLanguage();
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const SUGGESTED_QUESTIONS = [
    t("chat.suggested.q1", "Can I patent this formulation?"),
    t("chat.suggested.q2", "What regulations apply to my product?"),
    t("chat.suggested.q3", "What IP protection options are available?"),
    t("chat.suggested.q4", "Are there biodiversity requirements?"),
    t("chat.suggested.q5", "Does traditional knowledge affect this product?"),
    t("chat.suggested.q6", "What should I do next?"),
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    setErrorMessage(null);
    const userMsg: ChatMessageData = {
      id: Date.now().toString(),
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: text,
        analysisId,
        productName,
        jurisdiction,
        language,
        history: messages,
      });

      const aiMsg: ChatMessageData = {
        id: (Date.now() + 1).toString(),
        sender: "ayushya",
        text: response.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        sources: response.sources,
        confidence: response.confidence,
        disclaimer: response.disclaimer,
        requiresHumanAssistance: response.requiresHumanAssistance,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      setErrorMessage(
        t("chat.errorMessage", "AYUSHYA couldn't retrieve sufficient evidence for this question. Please try again or request human assistance.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    setErrorMessage(null);
  };

  const isFullPage = mode === "fullPage";

  return (
    <div
      className={`flex flex-col bg-[#080D0A]/95 border border-[rgba(212,175,55,0.25)] backdrop-blur-2xl shadow-[0_25px_60px_rgba(0,0,0,0.9),0_0_30px_rgba(8,127,91,0.15)] overflow-hidden ${
        isFullPage
          ? "w-full min-h-[680px] h-[calc(100vh-160px)] rounded-3xl"
          : "w-full sm:w-[440px] h-[600px] max-h-[85vh] rounded-3xl"
      }`}
    >
      {/* Chatbot Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[rgba(212,175,55,0.18)] bg-[#050806]/90 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#087F5B]/30 to-[#040705] border border-[#D4AF37]/35 flex items-center justify-center text-[#10B981] shadow-[0_0_15px_rgba(8,127,91,0.25)]">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-sm text-[#F4F8F5] font-display tracking-wide">
                {t("chat.title", "Ask AYUSHYA")}
              </h3>
              <span className="flex items-center gap-1.5 text-[10px] bg-[#0D1611] text-[#34D399] border border-[#087F5B]/40 px-2 py-0.5 rounded-full font-mono font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                {t("chat.ragActive", "RAG Active")}
              </span>
            </div>
            <p className="text-[11px] text-[#A3B3A9] flex items-center gap-1.5 mt-0.5 font-sans">
              <Globe className="w-3 h-3 text-[#D4AF37]" />
              <span>{t("chat.jurisdiction", "Jurisdiction:")} <strong className="text-white">{jurisdiction}</strong></span>
              {productName && <span className="truncate max-w-[130px] font-medium text-[#F3E5AB]">| {productName}</span>}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="p-2 text-[#A3B3A9] hover:text-[#F3E5AB] hover:bg-white/[0.06] rounded-xl transition-colors cursor-pointer"
              title={t("chat.clearHistory", "Clear chat history")}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}

          {!isFullPage && onClose && (
            <button
              onClick={onClose}
              className="p-2 text-[#A3B3A9] hover:text-[#F3E5AB] hover:bg-white/[0.06] rounded-xl transition-colors cursor-pointer"
              title={t("chat.closePanel", "Close panel")}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-6 my-auto">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-br from-[#087F5B]/25 to-[#040705] border border-[#D4AF37]/35 flex items-center justify-center text-[#10B981] shadow-[0_0_35px_rgba(8,127,91,0.25)]">
              <Sparkles className="w-8 h-8 text-[#34D399]" />
            </div>
            <div className="space-y-1.5">
              <h4 className="text-base font-extrabold text-[#F4F8F5] font-display tracking-tight">
                {t("chat.welcomeHeader", "Evidence-Backed Ayurvedic Legal Intelligence")}
              </h4>
              <p className="text-xs text-[#A3B3A9] max-w-sm mx-auto leading-relaxed">
                {t("chat.welcomeSub", "Ask about Section 3(p) TK exclusions, formulation patents, FSSAI Ayurveda-Aahar rules, or NBA biodiversity clearance.")}
              </p>
            </div>

            {/* Suggested Questions */}
            <div className="w-full max-w-md pt-2 space-y-2.5">
              <p className="text-[11px] font-bold text-[#F3E5AB] uppercase tracking-wider text-left font-mono flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                {t("chat.suggestedPromptTitle", "Suggested Inquiry Prompts:")}
              </p>
              <div className="grid gap-2 text-left">
                {SUGGESTED_QUESTIONS.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(question)}
                    className="w-full text-left text-xs p-3.5 rounded-2xl bg-[#050806] hover:bg-[#0D1611] border border-[rgba(212,175,55,0.18)] hover:border-[#10B981] text-[#F4F8F5] hover:text-[#F3E5AB] transition-all flex items-center justify-between group shadow-sm cursor-pointer"
                  >
                    <span className="font-medium pr-2">{question}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#D4AF37] group-hover:text-[#10B981] group-hover:translate-x-0.5 transition-transform shrink-0" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
          </>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start mb-4 animate-fade-slide-in-1">
            <div className="rounded-2xl rounded-tl-sm bg-[#050806] border border-[#D4AF37]/25 p-4 space-y-2.5 max-w-[85%] shadow-md">
              <div className="flex items-center gap-2 text-xs text-[#F3E5AB] font-semibold font-mono">
                <span className="w-2 h-2 rounded-full bg-[#10B981] animate-ping" />
                <span>{t("chat.loading", "AYUSHYA RAG is querying statutory databases...")}</span>
              </div>
              <div className="h-1.5 bg-[#0D1611] rounded-full overflow-hidden border border-[#D4AF37]/10">
                <div className="bg-gradient-to-r from-[#087F5B] to-[#D4AF37] h-full rounded-full w-full animate-pulse" />
              </div>
            </div>
          </div>
        )}

        {/* Error State Display */}
        {errorMessage && (
          <div className="p-4 rounded-2xl bg-[#050806] border border-[#EF4444]/40 text-xs text-[#F87171] space-y-2.5 shadow-md">
            <div className="flex items-center gap-2 font-bold">
              <AlertCircle className="w-4 h-4 text-[#EF4444]" />
              <span>{t("chat.errorNotice", "Retrieval Notice")}</span>
            </div>
            <p className="text-[#A3B3A9] leading-relaxed">{errorMessage}</p>
            <div className="flex items-center gap-2 pt-1">
              <Link
                href="/help"
                className="btn-primary-glow inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-white font-bold transition-colors"
              >
                <HelpCircle className="w-3.5 h-3.5 text-[#F3E5AB]" />
                <span>{t("chat.requestAdvisory", "Request Human Advisory")}</span>
              </Link>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Field */}
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};
