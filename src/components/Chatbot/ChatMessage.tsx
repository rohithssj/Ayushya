"use client";

import React from "react";
import Link from "next/link";
import { ChatMessageData } from "@/services/chatService";
import { FileText, AlertTriangle, HelpCircle, ExternalLink } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageData;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 animate-fade-slide-in-1">
        <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-[#087F5B] text-white px-4 py-3 shadow-[0_0_20px_rgba(8,127,91,0.3)] border border-[#D4AF37]/30">
          <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans">{message.text}</p>
          <span className="block text-[10px] text-white/70 text-right mt-1 font-mono">
            {message.timestamp}
          </span>
        </div>
      </div>
    );
  }

  // AYUSHYA Assistant message styling using strict 3-color palette
  const confidenceColor =
    message.confidence === "High"
      ? "bg-[#087F5B]/20 text-[#087F5B] border-[#087F5B]/40"
      : message.confidence === "Medium"
      ? "bg-[#D4AF37]/15 text-[#D4AF37] border-[#D4AF37]/40"
      : "bg-[#050806] text-[#D4AF37] border-[#D4AF37]/30";

  return (
    <div className="flex justify-start mb-5 animate-fade-slide-in-1">
      <div className="max-w-[90%] sm:max-w-[85%] rounded-2xl rounded-tl-sm bg-[#0A100C] text-[#F4F8F5] p-4 border border-[#D4AF37]/20 shadow-2xl space-y-3 backdrop-blur-sm">
        {/* AYUSHYA Header badge inside message */}
        <div className="flex items-center justify-between border-b border-[#D4AF37]/20 pb-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#087F5B]/20 border border-[#D4AF37]/50 flex items-center justify-center text-xs font-bold text-[#D4AF37]">
              🌿
            </div>
            <span className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider font-mono">
              AYUSHYA AI Evidence
            </span>
          </div>

          {message.confidence && (
            <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${confidenceColor}`}>
              Confidence: {message.confidence}
            </span>
          )}
        </div>

        {/* Answer Content */}
        <div className="text-sm leading-relaxed text-[#F4F8F5] whitespace-pre-wrap font-sans">
          {message.text}
        </div>

        {/* Evidence / Sources Section */}
        {message.sources && message.sources.length > 0 && (
          <div className="pt-2 border-t border-[#D4AF37]/20 space-y-1.5">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#D4AF37]">
              <FileText className="w-3.5 h-3.5 text-[#087F5B]" />
              <span>Cited Legal Evidence & Sources:</span>
            </div>
            <div className="grid gap-1.5 pl-1">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-xs p-2.5 rounded-xl bg-[#050806] border border-[#D4AF37]/20 hover:border-[#087F5B] transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[#D4AF37] font-mono text-[10px]">📄</span>
                    <div>
                      <p className="font-semibold text-[#F4F8F5] text-xs">{source.title}</p>
                      <p className="text-[11px] text-[#D4AF37] font-mono">{source.section}</p>
                    </div>
                  </div>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#A8B5AC] hover:text-[#D4AF37] p-1"
                      title="View Official Source"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legal Safety Disclaimer */}
        <div className="flex items-center gap-2 text-[11px] text-[#D4AF37] bg-[#D4AF37]/10 p-2.5 rounded-xl border border-[#D4AF37]/30">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 text-[#D4AF37]" />
          <span>{message.disclaimer || "⚠️ Informational guidance based on available evidence, not legal advice."}</span>
        </div>

        {/* Human Assistance Request Trigger on Low Confidence */}
        {(message.requiresHumanAssistance || message.confidence === "Low") && (
          <div className="pt-2 border-t border-[#D4AF37]/20 text-center space-y-2">
            <p className="text-xs text-[#D4AF37]">
              AYUSHYA could not confidently determine this aspect from available statutory context.
            </p>
            <Link
              href="/help"
              className="inline-flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-full bg-[#087F5B] text-white border border-[#D4AF37]/40 transition-all hover:scale-105"
            >
              <HelpCircle className="w-3.5 h-3.5 text-[#D4AF37]" />
              Request Human Assistance
            </Link>
          </div>
        )}

        <span className="block text-[10px] text-[#718078] text-right mt-1 font-mono">
          {message.timestamp}
        </span>
      </div>
    </div>
  );
};
