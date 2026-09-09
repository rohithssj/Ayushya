"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { sendChatMessage, ChatMessageData } from "@/services/chatService";
import { Bot, X, Sparkles, RefreshCw, Globe, AlertCircle, HelpCircle } from "lucide-react";
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
      className={`flex flex-col bg-[#050806]/95 border border-[#D4AF37]/30 backdrop-blur-xl shadow-[0_0_50px_rgba(0,0,0,0.9)] overflow-hidden ${
        isFullPage
          ? "w-full min-h-[700px] h-[calc(100vh-140px)] rounded-2xl"
          : "w-full sm:w-[430px] h-[590px] max-h-[85vh] rounded-2xl"
      }`}
    >
      {/* Chatbot Header */}
      <div className="flex items-center justify-between px-4 py-3.5 border-b border-[#D4AF37]/20 bg-[#0A100C]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[#087F5B]/20 border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] shadow-[0_0_15px_rgba(8,127,91,0.3)]">
            <Bot className="w-5 h-5 text-[#087F5B]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-sm text-[#F4F8F5] font-sans tracking-tight">
                {t("chat.title", "Ask AYUSHYA")}
              </h3>
              <span className="flex items-center gap-1 text-[10px] bg-[#0F1813] text-[#D4AF37] border border-[#D4AF37]/30 px-2 py-0.5 rounded-full font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-[#087F5B] animate-pulse" />
                {t("chat.ragActive", "RAG Active")}
              </span>
            </div>
            <p className="text-[11px] text-[#A8B5AC] flex items-center gap-1.5 mt-0.5 font-sans">
              <Globe className="w-3 h-3 text-[#D4AF37]" />
              <span>{t("chat.jurisdiction", "Jurisdiction:")} <strong className="text-[#F4F8F5]">{jurisdiction}</strong></span>
              {productName && <span className="truncate max-w-[120px]">| {productName}</span>}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="p-1.5 text-[#A8B5AC] hover:text-[#D4AF37] hover:bg-white/5 rounded-lg transition-colors cursor-pointer"
              title={t("chat.clearHistory", "Clear chat history")}
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}

          {!isFullPage && onClose && (
            <button
              onClick={onClose}
              className="p-1.5 text-[#A8B5AC] hover:text-[#D4AF37] hover:bg-white/5 rounded-lg transition-colors cursor-pointer"
              title={t("chat.closePanel", "Close panel")}
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-[#0F1813]">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-5 my-auto">
            <div className="w-14 h-14 rounded-2xl bg-[#0A100C] border border-[#D4AF37]/40 flex items-center justify-center text-[#D4AF37] shadow-[0_0_30px_rgba(8,127,91,0.25)]">
              <Sparkles className="w-7 h-7 text-[#087F5B]" />
            </div>
            <div>
              <h4 className="text-base font-bold text-[#F4F8F5] font-sans">
                {t("chat.welcomeHeader", "Evidence-Backed Ayurvedic Legal Intelligence")}
              </h4>
              <p className="text-xs text-[#A8B5AC] max-w-sm mt-1">
                {t("chat.welcomeSub", "Ask about Section 3(p) TK exclusions, formulation patents, FSSAI Ayurveda-Aahar rules, or NBA biodiversity clearance.")}
              </p>
            </div>

            {/* Suggested Questions */}
            <div className="w-full max-w-md pt-2 space-y-2">
              <p className="text-[11px] font-bold text-[#D4AF37] uppercase tracking-wider text-left font-mono">
                {t("chat.suggestedPromptTitle", "Suggested Inquiry Prompts:")}
              </p>
              <div className="grid gap-2 text-left">
                {SUGGESTED_QUESTIONS.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(question)}
                    className="w-full text-left text-xs p-3 rounded-xl bg-[#0A100C] hover:bg-[#0F1813] border border-[#D4AF37]/20 hover:border-[#087F5B] text-[#F4F8F5] hover:text-[#D4AF37] transition-all flex items-center justify-between group shadow-sm cursor-pointer"
                  >
                    <span>{question}</span>
                    <span className="text-[#D4AF37] group-hover:text-[#087F5B] font-mono text-xs">→</span>
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
          <div className="flex justify-start mb-4 animate-pulse">
            <div className="rounded-2xl rounded-tl-sm bg-[#0A100C] border border-[#D4AF37]/20 p-4 space-y-2 max-w-[80%]">
              <div className="flex items-center gap-2 text-xs text-[#D4AF37] font-semibold">
                <span className="w-2 h-2 rounded-full bg-[#087F5B] animate-ping" />
                <span>{t("chat.loading", "AYUSHYA RAG is querying statutory databases...")}</span>
              </div>
              <div className="h-2 bg-[#0F1813] rounded w-3/4 animate-pulse" />
              <div className="h-2 bg-[#0F1813] rounded w-1/2 animate-pulse" />
            </div>
          </div>
        )}

        {/* Error State Display */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-[#0A100C] border border-[#D4AF37]/40 text-xs text-[#D4AF37] space-y-2">
            <div className="flex items-center gap-2 font-bold">
              <AlertCircle className="w-4 h-4 text-[#D4AF37]" />
              <span>{t("chat.errorNotice", "Retrieval Notice")}</span>
            </div>
            <p>{errorMessage}</p>
            <div className="flex items-center gap-2 pt-1">
              <Link
                href="/help"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#087F5B] text-white font-bold transition-colors"
              >
                <HelpCircle className="w-3.5 h-3.5 text-[#D4AF37]" />
                {t("chat.requestAdvisory", "Request Human Advisory")}
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
