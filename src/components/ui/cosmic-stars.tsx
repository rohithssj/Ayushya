"use client";

import React, { useEffect, useRef } from "react";

interface Star {
  x: number;
  y: number;
  originX: number;
  originY: number;
  radius: number;
  color: string;
  glowColor: string;
  baseAlpha: number;
  currentAlpha: number;
  twinkleSpeed: number;
  twinklePhase: number;
  depth: number; // 0.2 to 1.0 (parallax depth multiplier)
  driftX: number;
  driftY: number;
}

interface ShootingStar {
  x: number;
  y: number;
  length: number;
  speed: number;
  angle: number;
  opacity: number;
  life: number;
  maxLife: number;
  color: string;
}

export const CosmicStars: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    // Respect reduced motion
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    let animationFrameId: number;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    // High DPI crispness
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    // Mouse & scroll tracking with smooth easing
    let targetMouseX = 0;
    let targetMouseY = 0;
    let currentMouseX = 0;
    let currentMouseY = 0;
    let scrollY = window.scrollY;

    const handleMouseMove = (e: MouseEvent) => {
      // Offset from viewport center (-1 to +1 normalized)
      targetMouseX = (e.clientX - width / 2) / (width / 2);
      targetMouseY = (e.clientY - height / 2) / (height / 2);
    };

    const handleScroll = () => {
      scrollY = window.scrollY;
    };

    const handleResize = () => {
      if (!canvas) return;
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      initStars();
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", handleResize);

    // Luxury palette matching AYUSHYA: Gold, Emerald, Diamond White
    const STAR_PALETTE = [
      { color: "#FFFFFF", glow: "rgba(255, 255, 255, 0.6)" },
      { color: "#F3E5AB", glow: "rgba(212, 175, 55, 0.5)" }, // Champagne Gold
      { color: "#D4AF37", glow: "rgba(212, 175, 55, 0.7)" }, // Radiant Gold
      { color: "#A7F3D0", glow: "rgba(16, 185, 129, 0.5)" }, // Mint Emerald
      { color: "#34D399", glow: "rgba(52, 211, 153, 0.6)" }, // Vivid Emerald
      { color: "#E0E7FF", glow: "rgba(199, 210, 254, 0.5)" }, // Cosmic Starlight
    ];

    let stars: Star[] = [];
    let shootingStars: ShootingStar[] = [];

    const initStars = () => {
      stars = [];
      // Moderate star count: 90 - 150 stars depending on screen size for performance & elegance
      const starCount = Math.floor(Math.min(140, Math.max(70, (width * height) / 12000)));

      for (let i = 0; i < starCount; i++) {
        const palette = STAR_PALETTE[Math.floor(Math.random() * STAR_PALETTE.length)];
        const depth = 0.25 + Math.random() * 0.75; // 0.25 (deep background) to 1.0 (foreground)
        const radius = (0.7 + Math.random() * 1.5) * (0.6 + depth * 0.5);

        const x = Math.random() * width;
        const y = Math.random() * height;

        stars.push({
          x,
          y,
          originX: x,
          originY: y,
          radius,
          color: palette.color,
          glowColor: palette.glow,
          baseAlpha: 0.25 + Math.random() * 0.6,
          currentAlpha: 0.5,
          twinkleSpeed: 0.015 + Math.random() * 0.035,
          twinklePhase: Math.random() * Math.PI * 2,
          depth,
          driftX: (Math.random() - 0.5) * 0.12 * depth,
          driftY: (Math.random() - 0.5) * 0.12 * depth,
        });
      }
    };

    const spawnShootingStar = () => {
      if (prefersReducedMotion || shootingStars.length >= 2) return;
      // Start from upper quarter
      const startX = Math.random() * width * 1.2;
      const startY = Math.random() * (height * 0.4);
      const isGold = Math.random() > 0.4;

      shootingStars.push({
        x: startX,
        y: startY,
        length: 60 + Math.random() * 70,
        speed: 7 + Math.random() * 6,
        angle: (Math.PI / 4) + (Math.random() - 0.5) * 0.2, // ~45 degree glide
        opacity: 0.8,
        life: 0,
        maxLife: 55 + Math.random() * 30,
        color: isGold ? "#F3E5AB" : "#34D399",
      });
    };

    let lastShootingStarTime = Date.now();
    initStars();

    let isVisible = true;
    const handleVisibilityChange = () => {
      isVisible = !document.hidden;
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Animation Loop
    const render = () => {
      if (!isVisible) {
        animationFrameId = requestAnimationFrame(render);
        return;
      }

      ctx.clearRect(0, 0, width, height);

      // Smooth mouse follow easing
      if (!prefersReducedMotion) {
        currentMouseX += (targetMouseX - currentMouseX) * 0.04;
        currentMouseY += (targetMouseY - currentMouseY) * 0.04;
      }

      // Draw background ambient nebula tint for depth
      const gradient = ctx.createRadialGradient(
        width * 0.5 + currentMouseX * 40,
        height * 0.4 + currentMouseY * 40,
        40,
        width * 0.5,
        height * 0.5,
        width * 0.7
      );
      gradient.addColorStop(0, "rgba(8, 127, 91, 0.04)");
      gradient.addColorStop(0.5, "rgba(212, 175, 55, 0.02)");
      gradient.addColorStop(1, "rgba(4, 7, 5, 0)");
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // Render Stars
      const scrollOffset = scrollY * 0.15;

      for (let i = 0; i < stars.length; i++) {
        const star = stars[i];

        // Twinkle calculation
        star.twinklePhase += star.twinkleSpeed;
        const twinkleSine = (Math.sin(star.twinklePhase) + 1) / 2; // 0 to 1
        star.currentAlpha = star.baseAlpha * (0.4 + twinkleSine * 0.6);

        // Gentle floating drift
        if (!prefersReducedMotion) {
          star.originX += star.driftX;
          star.originY += star.driftY;

          // Wrap edges smoothly
          if (star.originX < -20) star.originX = width + 20;
          if (star.originX > width + 20) star.originX = -20;
          if (star.originY < -20) star.originY = height + 20;
          if (star.originY > height + 20) star.originY = -20;
        }

        // Parallax cursor and scroll displacement
        const mouseDisplacementX = currentMouseX * 35 * star.depth;
        const mouseDisplacementY = currentMouseY * 35 * star.depth;
        const scrollDisplacementY = (scrollOffset * star.depth) % height;

        let renderX = star.originX + mouseDisplacementX;
        let renderY = star.originY + mouseDisplacementY - scrollDisplacementY;

        // Wrap around viewport height for scroll parallax
        if (renderY < 0) renderY += height;
        if (renderY > height) renderY -= height;

        // Draw star with soft cosmic glow
        ctx.save();
        ctx.globalAlpha = Math.max(0.05, Math.min(1, star.currentAlpha));

        if (star.radius > 1.2) {
          ctx.shadowBlur = 8 * star.depth;
          ctx.shadowColor = star.glowColor;
        }

        ctx.fillStyle = star.color;
        ctx.beginPath();
        ctx.arc(renderX, renderY, star.radius, 0, Math.PI * 2);
        ctx.fill();

        // Cross sparkle on prominent stars
        if (star.radius > 1.6 && twinkleSine > 0.75) {
          ctx.strokeStyle = star.glowColor;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          const sparkleSize = star.radius * 2.2;
          ctx.moveTo(renderX - sparkleSize, renderY);
          ctx.lineTo(renderX + sparkleSize, renderY);
          ctx.moveTo(renderX, renderY - sparkleSize);
          ctx.lineTo(renderX, renderY + sparkleSize);
          ctx.stroke();
        }

        ctx.restore();
      }

      // Check for shooting star spawn (every 4 - 8 seconds)
      const now = Date.now();
      if (now - lastShootingStarTime > 5000 + Math.random() * 4000) {
        spawnShootingStar();
        lastShootingStarTime = now;
      }

      // Render Shooting Stars
      for (let i = shootingStars.length - 1; i >= 0; i--) {
        const s = shootingStars[i];
        s.life++;
        s.x += Math.cos(s.angle) * s.speed;
        s.y += Math.sin(s.angle) * s.speed;

        const lifeRatio = s.life / s.maxLife;
        const currentAlpha = Math.sin(lifeRatio * Math.PI) * s.opacity;

        if (lifeRatio >= 1 || s.x > width + 100 || s.y > height + 100) {
          shootingStars.splice(i, 1);
          continue;
        }

        ctx.save();
        ctx.globalAlpha = currentAlpha;
        const tailX = s.x - Math.cos(s.angle) * s.length;
        const tailY = s.y - Math.sin(s.angle) * s.length;

        const starGrad = ctx.createLinearGradient(tailX, tailY, s.x, s.y);
        starGrad.addColorStop(0, "rgba(255, 255, 255, 0)");
        starGrad.addColorStop(0.7, s.color);
        starGrad.addColorStop(1, "#FFFFFF");

        ctx.strokeStyle = starGrad;
        ctx.lineWidth = 1.6;
        ctx.shadowBlur = 10;
        ctx.shadowColor = s.color;

        ctx.beginPath();
        ctx.moveTo(tailX, tailY);
        ctx.lineTo(s.x, s.y);
        ctx.stroke();
        ctx.restore();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="fixed inset-0 pointer-events-none -z-10 w-full h-full"
      style={{
        background: "transparent",
      }}
    />
  );
};
