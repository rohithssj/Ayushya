"use client";

import React from "react";
import Link from "next/link";
import { ChatMessageData } from "@/services/chatService";
import { FileText, AlertTriangle, HelpCircle, ExternalLink, ShieldCheck } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageData;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 animate-fade-slide-in-1">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-[#087F5B] to-[#059669] text-white px-5 py-3.5 shadow-[0_4px_20px_rgba(8,127,91,0.35)] border border-[#D4AF37]/30 space-y-1">
          <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans font-medium">{message.text}</p>
          <span className="block text-[10px] text-white/70 text-right font-mono">
            {message.timestamp}
          </span>
        </div>
      </div>
    );
  }

  // AYUSHYA Assistant message styling
  const confidenceColor =
    message.confidence === "High"
      ? "bg-[#087F5B]/20 text-[#34D399] border-[#10B981]/40"
      : message.confidence === "Medium"
      ? "bg-[#D4AF37]/15 text-[#F3E5AB] border-[#D4AF37]/40"
      : "bg-[#EF4444]/15 text-[#FCA5A5] border-[#EF4444]/30";

  return (
    <div className="flex justify-start mb-5 animate-fade-slide-in-1">
      <div className="max-w-[92%] sm:max-w-[85%] rounded-2xl rounded-tl-sm bg-[#050806] text-[#F4F8F5] p-5 border border-[rgba(212,175,55,0.22)] shadow-xl space-y-3.5 backdrop-blur-md">
        {/* AYUSHYA Header badge inside message */}
        <div className="flex items-center justify-between border-b border-[rgba(212,175,55,0.15)] pb-2.5">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-[#087F5B]/20 border border-[#D4AF37]/40 flex items-center justify-center text-xs font-bold text-[#D4AF37]">
              🌿
            </div>
            <span className="text-xs font-bold text-[#F3E5AB] uppercase tracking-wider font-mono">
              AYUSHYA AI Evidence
            </span>
          </div>

          {message.confidence && (
            <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border font-mono ${confidenceColor}`}>
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
          <div className="pt-2 border-t border-[rgba(212,175,55,0.15)] space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#F3E5AB] font-mono">
              <FileText className="w-3.5 h-3.5 text-[#10B981]" />
              <span>Cited Legal Evidence & Sources:</span>
            </div>
            <div className="grid gap-2">
              {message.sources.map((source, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between text-xs p-3 rounded-xl bg-[#090F0B] border border-[rgba(212,175,55,0.18)] hover:border-[#10B981] transition-all group shadow-sm"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-[#D4AF37] font-mono text-xs">§</span>
                    <div>
                      <p className="font-semibold text-[#F4F8F5] text-xs font-sans group-hover:text-[#F3E5AB] transition-colors">{source.title}</p>
                      <p className="text-[11px] text-[#D4AF37] font-mono">{source.section}</p>
                    </div>
                  </div>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#6C7D73] hover:text-[#10B981] p-1 transition-colors"
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
        <div className="flex items-center gap-2.5 text-[11px] text-[#F3E5AB] bg-[#D4AF37]/10 p-3 rounded-xl border border-[#D4AF37]/25">
          <AlertTriangle className="w-4 h-4 shrink-0 text-[#D4AF37]" />
          <span className="leading-relaxed font-sans">{message.disclaimer || "⚠️ Informational guidance based on available evidence, not legal advice."}</span>
        </div>

        {/* Human Assistance Request Trigger on Low Confidence */}
        {(message.requiresHumanAssistance || message.confidence === "Low") && (
          <div className="pt-2.5 border-t border-[rgba(212,175,55,0.18)] text-center space-y-2">
            <p className="text-xs text-[#D4AF37]">
              AYUSHYA could not confidently determine this aspect from available statutory context.
            </p>
            <Link
              href="/help"
              className="btn-primary-glow inline-flex items-center gap-2 text-xs font-bold px-4 py-2 rounded-full text-white shadow-md cursor-pointer"
            >
              <HelpCircle className="w-3.5 h-3.5 text-[#F3E5AB]" />
              <span>Request Human Assistance</span>
            </Link>
          </div>
        )}

        <span className="block text-[10px] text-[#6C7D73] text-right font-mono">
          {message.timestamp}
        </span>
      </div>
    </div>
  );
};
