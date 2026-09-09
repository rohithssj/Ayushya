"use client";

import React, { useState } from 'react';

interface NavLink {
    label: string;
    href: string;
    isActive?: boolean;
}

interface Partner {
    logoUrl: string;
    href: string;
}

interface ResponsiveHeroBannerProps {
    logoUrl?: string;
    backgroundImageUrl?: string;
    navLinks?: NavLink[];
    ctaButtonText?: string;
    ctaButtonHref?: string;
    badgeText?: string;
    badgeLabel?: string;
    title?: string;
    titleLine2?: string;
    description?: string;
    primaryButtonText?: string;
    primaryButtonHref?: string;
    secondaryButtonText?: string;
    secondaryButtonHref?: string;
    partnersTitle?: string;
    partners?: Partner[];
}

const ResponsiveHeroBanner: React.FC<ResponsiveHeroBannerProps> = ({
    logoUrl = "",
    backgroundImageUrl = "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?q=80&w=2000&auto=format&fit=crop",
    navLinks = [
        { label: "Home", href: "/", isActive: true },
        { label: "Analyze Formulation", href: "/analyze" },
        { label: "Ask AYUSHYA", href: "/assistant" },
        { label: "Human Advisory", href: "/help" }
    ],
    ctaButtonText = "Ask AYUSHYA",
    ctaButtonHref = "/assistant",
    badgeLabel = "AYUSHYA",
    badgeText = "AI-Powered IP & Regulatory Intelligence for Ayurveda",
    title = "AYUSHYA Intelligence",
    titleLine2 = "Source-Cited Legal RAG for Ayurveda",
    description = "Navigate Indian and International patent eligibility, traditional knowledge exclusions (Section 3p), FSSAI Ayurveda-Aahar compliance, and NBA biodiversity clearances with authoritative statutory evidence.",
    primaryButtonText = "Analyze Formulation",
    primaryButtonHref = "/analyze",
    secondaryButtonText = "Ask AI Assistant",
    secondaryButtonHref = "/assistant",
    partnersTitle = "Grounded in Authoritative Statutory Frameworks & Government Databases",
    partners = []
}) => {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <section className="w-full isolate min-h-[85vh] overflow-hidden relative bg-neutral-950 flex flex-col justify-between">
            {/* Background Image with Dark Backdrop Overlay */}
            <img
                src={backgroundImageUrl}
                alt="AYUSHYA Background"
                className="w-full h-full object-cover absolute top-0 right-0 bottom-0 left-0 opacity-25 filter contrast-125"
            />
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-neutral-950/90 via-neutral-950/70 to-neutral-950" />

            {/* Header / Navbar */}
            <header className="z-10 xl:top-4 relative">
                <div className="mx-6">
                    <div className="flex items-center justify-between pt-4">
                        <a
                            href="/"
                            className="inline-flex items-center gap-2 text-white font-bold text-lg tracking-wider"
                        >
                            <span className="w-8 h-8 rounded-lg bg-emerald-600/30 border border-emerald-500/50 flex items-center justify-center text-emerald-400 text-sm">
                                🌿
                            </span>
                            <span>AYUSHYA</span>
                        </a>

                        <nav className="hidden md:flex items-center gap-2">
                            <div className="flex items-center gap-1 rounded-full bg-white/5 px-2 py-1 ring-1 ring-white/10 backdrop-blur">
                                {navLinks.map((link, index) => (
                                    <a
                                        key={index}
                                        href={link.href}
                                        className={`px-3.5 py-1.5 text-xs font-semibold hover:text-emerald-300 transition-colors ${
                                            link.isActive ? 'text-emerald-400 bg-emerald-950/60 rounded-full border border-emerald-500/30' : 'text-neutral-300'
                                        }`}
                                    >
                                        {link.label}
                                    </a>
                                ))}
                                <a
                                    href={ctaButtonHref}
                                    className="ml-2 inline-flex items-center gap-1.5 rounded-full bg-emerald-600 hover:bg-emerald-500 px-4 py-1.5 text-xs font-semibold text-white transition-all shadow-lg"
                                >
                                    {ctaButtonText}
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-3.5 w-3.5">
                                        <path d="M7 7h10v10" />
                                        <path d="M7 17 17 7" />
                                    </svg>
                                </a>
                            </div>
                        </nav>

                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden inline-flex h-10 w-10 items-center justify-center rounded-full bg-white/10 ring-1 ring-white/15 backdrop-blur text-white"
                            aria-expanded={mobileMenuOpen}
                            aria-label="Toggle menu"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                                <path d="M4 5h16" />
                                <path d="M4 12h16" />
                                <path d="M4 19h16" />
                            </svg>
                        </button>
                    </div>

                    {mobileMenuOpen && (
                        <div className="md:hidden mt-3 rounded-2xl bg-neutral-900/95 ring-1 ring-white/10 backdrop-blur p-4 space-y-2 relative z-20">
                            {navLinks.map((link, index) => (
                                <a
                                    key={index}
                                    href={link.href}
                                    className="block px-3 py-2 text-sm font-medium text-neutral-200 hover:text-emerald-400 transition-colors"
                                >
                                    {link.label}
                                </a>
                            ))}
                            <a
                                href={ctaButtonHref}
                                className="block text-center mt-2 rounded-full bg-emerald-600 px-3.5 py-2 text-sm font-semibold text-white hover:bg-emerald-500 transition-colors"
                            >
                                {ctaButtonText}
                            </a>
                        </div>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <div className="z-10 relative my-auto py-12">
                <div className="max-w-5xl mx-auto px-6 text-center">
                    <div className="mb-6 inline-flex items-center gap-2.5 rounded-full bg-emerald-950/80 px-3.5 py-1.5 ring-1 ring-emerald-500/40 backdrop-blur animate-fade-slide-in-1">
                        <span className="inline-flex items-center text-xs font-bold text-emerald-950 bg-emerald-400 rounded-full py-0.5 px-2 font-mono">
                            {badgeLabel}
                        </span>
                        <span className="text-xs font-medium text-emerald-200 font-sans">
                            {badgeText}
                        </span>
                    </div>

                    <h1 className="sm:text-5xl md:text-6xl leading-tight text-4xl text-white tracking-tight font-bold font-sans animate-fade-slide-in-2">
                        {title}
                        <br />
                        <span className="text-emerald-400 font-serif italic font-normal">{titleLine2}</span>
                    </h1>

                    <p className="sm:text-lg animate-fade-slide-in-3 text-base text-neutral-300 max-w-2xl mt-6 mx-auto leading-relaxed">
                        {description}
                    </p>

                    <div className="flex flex-col sm:flex-row sm:gap-4 mt-10 gap-3 items-center justify-center animate-fade-slide-in-4">
                        <a
                            href={primaryButtonHref}
                            className="inline-flex items-center gap-2 hover:bg-emerald-500 text-sm font-semibold text-white bg-emerald-600 shadow-xl rounded-full py-3.5 px-6 transition-all hover:scale-105"
                        >
                            {primaryButtonText}
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
                                <path d="M5 12h14" />
                                <path d="m12 5 7 7-7 7" />
                            </svg>
                        </a>
                        <a
                            href={secondaryButtonHref}
                            className="inline-flex items-center gap-2 rounded-full bg-neutral-900/80 hover:bg-neutral-800 px-6 py-3.5 text-sm font-semibold text-neutral-200 hover:text-white border border-neutral-800 transition-all"
                        >
                            {secondaryButtonText}
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-emerald-400">
                                <path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z" />
                            </svg>
                        </a>
                    </div>
                </div>
            </div>

            {/* Statutory Footer Badge */}
            <div className="z-10 relative pb-6 px-6">
                <div className="max-w-5xl mx-auto border-t border-neutral-800/80 pt-4 text-center">
                    <p className="animate-fade-slide-in-1 text-xs text-neutral-400 uppercase tracking-widest font-mono">
                        {partnersTitle}
                    </p>
                    <div className="flex flex-wrap items-center justify-center gap-6 mt-3 text-xs text-neutral-400 font-semibold">
                        <span className="flex items-center gap-1.5 text-emerald-400">📜 Patents Act 1970 §3(p)</span>
                        <span className="flex items-center gap-1.5 text-emerald-400">🌿 Biological Diversity Act 2002</span>
                        <span className="flex items-center gap-1.5 text-emerald-400">🥗 FSSAI Ayurveda-Aahar 2022</span>
                        <span className="flex items-center gap-1.5 text-emerald-400">🏥 Drugs & Cosmetics Rules 1945</span>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default ResponsiveHeroBanner;
