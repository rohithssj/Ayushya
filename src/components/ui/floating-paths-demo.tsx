"use client";

import { FloatingPathsBackground } from "@/components/ui/floating-paths";
import React from "react";

export default function FloatingPathsBackgroundExample() {
  return (
    <FloatingPathsBackground
      className="aspect-16/9 flex items-center justify-center min-h-[300px] rounded-3xl bg-[#101C14] border border-white/10"
      position={-1}
    >
      <div className="text-center space-y-2 z-10 p-6">
        <h3 className="text-2xl font-bold text-[#F4F8F5]">Floating Animated Vector Paths</h3>
        <p className="text-xs text-[#A8B5AC]">Integrated smoothly into the AYUSHYA #07110B legal AI theme.</p>
      </div>
    </FloatingPathsBackground>
  );
}
