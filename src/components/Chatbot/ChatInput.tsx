"use client";

import React, { useState, KeyboardEvent } from "react";
import { Send, Loader2 } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading = false,
  placeholder,
}) => {
  const { t } = useLanguage();
  const [text, setText] = useState("");

  const defaultPlaceholder = t("chat.inputPlaceholder", "Ask a legal or regulatory question...");

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      onSendMessage(text.trim());
      setText("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-3 border-t border-[#D4AF37]/20 bg-[#050806]/95 backdrop-blur-xl">
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || defaultPlaceholder}
          disabled={isLoading}
          className="flex-1 bg-[#0A100C] border border-[#D4AF37]/20 focus:border-[#087F5B] focus:ring-2 focus:ring-[#087F5B]/30 rounded-xl px-4 py-2.5 text-sm text-[#F4F8F5] placeholder-[#718078] focus:outline-none transition-all disabled:opacity-50 font-sans"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || isLoading}
          aria-label="Send message"
          className="btn-primary-glow inline-flex items-center justify-center w-10 h-10 rounded-xl disabled:bg-[#0A100C] disabled:text-[#718078] disabled:shadow-none disabled:border border-[#D4AF37]/10 transition-all shrink-0 cursor-pointer"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-[#D4AF37]" />
          ) : (
            <Send className="w-4 h-4 text-[#D4AF37]" />
          )}
        </button>
      </div>
    </div>
  );
};
