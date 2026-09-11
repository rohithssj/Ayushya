import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar/Navbar";
import { Footer } from "@/components/Footer/Footer";
import { SupportBox } from "@/components/SupportBox/SupportBox";
import ParticlesComponent from "@/components/ui/particles-bg";
import { LanguageProvider } from "@/i18n/LanguageContext";

export const metadata: Metadata = {
  title: "AYUSHYA — AI-Powered IP & Regulatory Intelligence for Ayurveda",
  description:
    "Multilingual, source-cited AI legal intelligence for Ayurvedic intellectual property, traditional knowledge exclusions (Section 3p), FSSAI regulations, and NBA clearances.",
  icons: {
    icon: "/ayushya-icon.svg",
    shortcut: "/ayushya-icon.svg",
    apple: "/ayushya-icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className="antialiased bg-black text-[#F4F8F5] min-h-screen flex flex-col font-sans selection:bg-[#059669]/30 selection:text-[#34D399] relative overflow-x-hidden">
        <LanguageProvider>
          {/* Particles Background Layer with Black Base */}
          <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden bg-black" aria-hidden="true">
            <ParticlesComponent className="w-full h-full absolute top-0 left-0 bg-black pointer-events-none opacity-60" />
          </div>

          <div className="relative z-20 flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-1 relative z-10">{children}</main>
            <Footer />
            <SupportBox />
          </div>
        </LanguageProvider>
      </body>
    </html>
  );
}
