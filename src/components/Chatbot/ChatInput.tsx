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
    <div className="p-3.5 border-t border-[rgba(212,175,55,0.18)] bg-[#050806]/95 backdrop-blur-2xl">
      <div className="flex items-center gap-2.5">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || defaultPlaceholder}
          disabled={isLoading}
          className="flex-1 bg-[#090F0B] border border-[rgba(212,175,55,0.2)] focus:border-[#10B981] focus:ring-2 focus:ring-[#10B981]/25 rounded-2xl px-4.5 py-3 text-sm text-[#F4F8F5] placeholder-[#6C7D73] focus:outline-none transition-all disabled:opacity-50 font-sans shadow-inner"
        />
        <button
          onClick={handleSend}
          disabled={!text.trim() || isLoading}
          aria-label="Send message"
          className="btn-primary-glow inline-flex items-center justify-center w-11 h-11 rounded-2xl disabled:opacity-40 disabled:pointer-events-none transition-all shrink-0 cursor-pointer shadow-md active:scale-95"
        >
          {isLoading ? (
            <Loader2 className="w-4.5 h-4.5 animate-spin text-[#F3E5AB]" />
          ) : (
            <Send className="w-4.5 h-4.5 text-[#F3E5AB]" />
          )}
        </button>
      </div>
    </div>
  );
};
