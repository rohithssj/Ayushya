import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar/Navbar";
import { Footer } from "@/components/Footer/Footer";
import { SupportBox } from "@/components/SupportBox/SupportBox";
import { BackgroundPixelStars } from "@/components/ui/background-pixel-stars";
import { LanguageProvider } from "@/i18n/LanguageContext";

export const metadata: Metadata = {
  title: "AYUSHYA — AI-Powered IP & Regulatory Intelligence for Ayurveda",
  description: "Multilingual, source-cited AI assistant for Ayurvedic intellectual property, traditional knowledge exclusions, FSSAI regulations, and NBA clearances.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#07110B] text-[#F4F8F5] min-h-screen flex flex-col font-sans selection:bg-[#3FAE62]/30 selection:text-[#66D98A] relative">
        <LanguageProvider>
          <BackgroundPixelStars />
          <Navbar />
          <div className="flex-1 relative z-10">{children}</div>
          <Footer />
          <SupportBox />
        </LanguageProvider>
      </body>
    </html>
  );
}
