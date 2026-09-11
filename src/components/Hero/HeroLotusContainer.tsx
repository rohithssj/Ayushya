"use client";

import React from "react";
import dynamic from "next/dynamic";

// Dynamically import the 3D canvas with SSR disabled for optimal performance
const AyurvedicLotus3D = dynamic(() => import("./AyurvedicLotus3D"), {
  ssr: false,
  loading: () => (
    <div
      className="w-full h-full flex items-center justify-center opacity-0 pointer-events-none"
      aria-hidden="true"
    />
  ),
});

interface HeroLotusContainerProps {
  className?: string;
}

export default function HeroLotusContainer({ className = "" }: HeroLotusContainerProps) {
  return (
    <div className={`relative w-full h-full pointer-events-none ${className}`}>
      <AyurvedicLotus3D />
    </div>
  );
}
