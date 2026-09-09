"use client";

import { BackgroundPixelStars } from "@/components/ui/background-pixel-stars";

const Default = () => {
  return (
    <div className="h-dvh w-dvw bg-[#07110B] relative">
      <BackgroundPixelStars />
      <div className="flex flex-col items-center justify-center h-full text-center p-6 relative z-10 space-y-2">
        <h2 className="text-3xl font-extrabold text-[#F4F8F5]">Background Pixel Stars Demo</h2>
        <p className="text-sm text-[#66D98A]">16-bit twinkling pixelated stars and shooting stars on #07110B canvas</p>
      </div>
    </div>
  );
};

export default Default;
