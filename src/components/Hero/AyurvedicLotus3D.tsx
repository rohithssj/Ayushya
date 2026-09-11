"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface AyurvedicLotus3DProps {
  className?: string;
  heroRef?: React.RefObject<HTMLElement | null>;
}

export default function AyurvedicLotus3D({ className = "" }: AyurvedicLotus3DProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isWebGLSupported, setIsWebGLSupported] = useState(true);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    // Check WebGL availability
    try {
      const canvasTest = document.createElement("canvas");
      const gl =
        canvasTest.getContext("webgl2") ||
        canvasTest.getContext("webgl") ||
        canvasTest.getContext("experimental-webgl");
      if (!gl) {
        setIsWebGLSupported(false);
        return;
      }
    } catch {
      setIsWebGLSupported(false);
      return;
    }

    // Check reduced motion preference
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // Scene setup
    const scene = new THREE.Scene();

    const width = container.clientWidth || 420;
    const height = container.clientHeight || 420;

    const camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 100);
    // Elevated top-down 3/4 camera view to showcase the sacred golden center and concentric petals
    camera.position.set(0, 3.2, 5.0);
    camera.lookAt(0, -0.05, 0);

    let renderer: THREE.WebGLRenderer | null = null;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
    } catch (e) {
      console.warn("Failed to initialize WebGLRenderer for Lotus:", e);
      setIsWebGLSupported(false);
      return;
    }

    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    // ─── PROCEDURAL TEXTURE GENERATION ───
    // 1. Authentic broad botanical petal texture with deep emerald jade and delicate gold border
    const petalCanvas = document.createElement("canvas");
    petalCanvas.width = 512;
    petalCanvas.height = 1024;
    const ctx = petalCanvas.getContext("2d");
    if (ctx) {
      // Base deep emerald gradient
      const grad = ctx.createLinearGradient(0, 1024, 0, 0);
      grad.addColorStop(0.0, "#031c13"); // Deep Vedic root
      grad.addColorStop(0.2, "#063324");
      grad.addColorStop(0.5, "#0b543c"); // Radiant herbal jade
      grad.addColorStop(0.8, "#127555");
      grad.addColorStop(0.95, "#1c966f");
      grad.addColorStop(1.0, "#d8b248"); // Sacred gold apex
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 512, 1024);

      // Fine golden botanical venation
      ctx.strokeStyle = "rgba(220, 185, 75, 0.28)";
      ctx.lineWidth = 2.0;
      ctx.beginPath();
      // Primary median spine
      ctx.moveTo(256, 1020);
      ctx.quadraticCurveTo(256, 450, 256, 35);
      ctx.stroke();

      // Secondary curving pinnate veins
      ctx.lineWidth = 1.0;
      ctx.strokeStyle = "rgba(220, 185, 75, 0.16)";
      for (let y = 880; y > 120; y -= 42) {
        const span = Math.sin((y / 1024) * Math.PI) * 210;
        // Left
        ctx.beginPath();
        ctx.moveTo(256, y);
        ctx.quadraticCurveTo(256 - span * 0.45, y - 40, 256 - span, y - 75);
        ctx.stroke();
        // Right
        ctx.beginPath();
        ctx.moveTo(256, y);
        ctx.quadraticCurveTo(256 + span * 0.45, y - 40, 256 + span, y - 75);
        ctx.stroke();
      }

      // Golden rim border glow along the upper half of the petal
      const rimPath = new Path2D();
      rimPath.moveTo(40, 550);
      rimPath.quadraticCurveTo(70, 120, 256, 30);
      rimPath.quadraticCurveTo(442, 120, 472, 550);
      ctx.strokeStyle = "rgba(235, 195, 75, 0.45)";
      ctx.lineWidth = 6.0;
      ctx.stroke(rimPath);

      // Soft tip radial highlight
      const tipGrad = ctx.createRadialGradient(256, 60, 5, 256, 60, 240);
      tipGrad.addColorStop(0.0, "rgba(255, 235, 160, 0.55)");
      tipGrad.addColorStop(0.35, "rgba(218, 175, 55, 0.3)");
      tipGrad.addColorStop(1.0, "rgba(218, 175, 55, 0)");
      ctx.fillStyle = tipGrad;
      ctx.fillRect(0, 0, 512, 260);
    }

    const petalTexture = new THREE.CanvasTexture(petalCanvas);
    petalTexture.colorSpace = THREE.SRGBColorSpace;
    petalTexture.wrapS = THREE.ClampToEdgeWrapping;
    petalTexture.wrapT = THREE.ClampToEdgeWrapping;

    // 2. Soft sacred volumetric back-glow texture
    const glowCanvas = document.createElement("canvas");
    glowCanvas.width = 512;
    glowCanvas.height = 512;
    const gCtx = glowCanvas.getContext("2d");
    if (gCtx) {
      const radGrad = gCtx.createRadialGradient(256, 256, 10, 256, 256, 256);
      radGrad.addColorStop(0.0, "rgba(16, 185, 129, 0.6)"); // Jade core
      radGrad.addColorStop(0.22, "rgba(212, 175, 55, 0.38)"); // Golden aura ring
      radGrad.addColorStop(0.5, "rgba(8, 127, 91, 0.18)"); // Ambient emerald
      radGrad.addColorStop(0.8, "rgba(4, 30, 20, 0.05)");
      radGrad.addColorStop(1.0, "rgba(0, 0, 0, 0)");
      gCtx.fillStyle = radGrad;
      gCtx.fillRect(0, 0, 512, 512);
    }
    const glowTexture = new THREE.CanvasTexture(glowCanvas);

    // ─── MATERIALS ───
    // Primary translucent emerald petal material with gold undertones
    const petalMaterial = new THREE.MeshPhysicalMaterial({
      map: petalTexture,
      color: new THREE.Color(0x0c523c),
      emissive: new THREE.Color(0x041810),
      emissiveIntensity: 0.35,
      roughness: 0.42,
      metalness: 0.1,
      clearcoat: 0.35,
      clearcoatRoughness: 0.25,
      transmission: 0.3, // Translucent botanical light transmission
      thickness: 0.5,
      ior: 1.48, // Plant cuticle index
      attenuationColor: new THREE.Color(0x10b981),
      attenuationDistance: 1.4,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.98,
    });

    // Outer calyx sepal material (darker forest emerald)
    const sepalMaterial = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(0x042117),
      emissive: new THREE.Color(0x020f0a),
      roughness: 0.48,
      metalness: 0.15,
      clearcoat: 0.25,
      side: THREE.DoubleSide,
    });

    // Sacred Ayurvedic Gold for Seed Pod & Stamens
    const goldMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color(0xdfb43a),
      metalness: 0.9,
      roughness: 0.22,
      emissive: new THREE.Color(0x524110),
      emissiveIntensity: 0.3,
    });

    // Glowing Stamen Anther Tip Material
    const antherMaterial = new THREE.MeshStandardMaterial({
      color: new THREE.Color(0xffe27a),
      metalness: 0.92,
      roughness: 0.15,
      emissive: new THREE.Color(0xdfb43a),
      emissiveIntensity: 0.7,
    });

    // ─── BROAD BOTANICAL PETAL GEOMETRY GENERATOR ───
    function createPetalGeometry(
      length: number,
      width: number,
      cupDepth: number,
      recurve: number
    ): THREE.BufferGeometry {
      const uSegments = 28;
      const vSegments = 20;
      const positions: number[] = [];
      const normals: number[] = [];
      const uvs: number[] = [];
      const indices: number[] = [];

      for (let i = 0; i <= uSegments; i++) {
        const u = i / uSegments; // 0 at base, 1 at tip
        // Real broad lotus paddle shape: swells gracefully to full width between u=0.35 and 0.7
        const widthTaper = Math.sin(Math.pow(u, 0.55) * Math.PI) * (0.3 + 0.7 * Math.sin(u * Math.PI));
        const currentHalfWidth = (width * 0.5) * Math.max(0.01, widthTaper);

        // Longitudinal curvature: cups smoothly inward, tip softly recurves back
        const longitudinal =
          -Math.sin(Math.pow(u, 0.82) * Math.PI) * cupDepth + Math.pow(u, 2.5) * recurve;

        for (let j = 0; j <= vSegments; j++) {
          const vNorm = (j / vSegments) * 2 - 1; // -1 to +1
          const x = vNorm * currentHalfWidth;
          const y = u * length;

          // Transverse hollow arch (spoon/cup hollow)
          const transverse = -(1 - vNorm * vNorm) * Math.sin(u * Math.PI) * (cupDepth * 0.45);
          // Soft organic margin wave
          const ruffle = Math.sin(u * 12.0) * (vNorm * vNorm) * (width * 0.018);

          const z = longitudinal + transverse + ruffle;

          positions.push(x, y, z);
          normals.push(0, 1, 0); // Recomputed later
          uvs.push((vNorm + 1) * 0.5, u);
        }
      }

      for (let i = 0; i < uSegments; i++) {
        for (let j = 0; j < vSegments; j++) {
          const a = i * (vSegments + 1) + j;
          const b = (i + 1) * (vSegments + 1) + j;
          const c = (i + 1) * (vSegments + 1) + (j + 1);
          const d = i * (vSegments + 1) + (j + 1);
          indices.push(a, b, d);
          indices.push(b, c, d);
        }
      }

      const geom = new THREE.BufferGeometry();
      geom.setIndex(indices);
      geom.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
      geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
      geom.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
      geom.computeVertexNormals();
      return geom;
    }

    // ─── ASSEMBLE LOTUS FLOWER ───
    const lotusRoot = new THREE.Group();
    lotusRoot.position.set(0, -0.15, 0);
    // Harmonious scale fitting beautifully within the canvas
    lotusRoot.scale.set(0.44, 0.44, 0.44);
    // Forward tilt so camera peers directly down into the sacred golden heart
    lotusRoot.rotation.x = THREE.MathUtils.degToRad(32);
    scene.add(lotusRoot);

    // Track petal whorls for dynamic organic breathing animation
    interface WhorlLayer {
      group: THREE.Group;
      basePitch: number;
      breathAmp: number;
      breathSpeed: number;
      breathPhase: number;
      petals: THREE.Mesh[];
    }
    const whorlLayers: WhorlLayer[] = [];

    // Layer 1: Inner Cupping Whorl (6 broad petals, upright, cradling the golden seed pod)
    const innerGeom = createPetalGeometry(1.0, 0.75, 0.28, 0.06);
    const innerGroup = new THREE.Group();
    const innerPetals: THREE.Mesh[] = [];
    const innerCount = 6;
    for (let i = 0; i < innerCount; i++) {
      const petalMesh = new THREE.Mesh(innerGeom, petalMaterial);
      const angle = (i / innerCount) * Math.PI * 2;
      const petalHolder = new THREE.Group();
      petalHolder.rotation.y = angle;

      petalMesh.position.set(0, 0.1, 0.22);
      petalMesh.rotation.x = THREE.MathUtils.degToRad(28); // Cupped near pod
      petalHolder.add(petalMesh);
      innerGroup.add(petalHolder);
      innerPetals.push(petalMesh);
    }
    lotusRoot.add(innerGroup);
    whorlLayers.push({
      group: innerGroup,
      basePitch: THREE.MathUtils.degToRad(28),
      breathAmp: 0.035,
      breathSpeed: 1.05,
      breathPhase: 0,
      petals: innerPetals,
    });

    // Layer 2: Mid Blooming Whorl (8 broad petals, gracefully opening)
    const midGeom = createPetalGeometry(1.35, 0.92, 0.34, 0.12);
    const midGroup = new THREE.Group();
    const midPetals: THREE.Mesh[] = [];
    const midCount = 8;
    for (let i = 0; i < midCount; i++) {
      const petalMesh = new THREE.Mesh(midGeom, petalMaterial);
      const angle = (i / midCount) * Math.PI * 2 + Math.PI / 8; // Staggered
      const petalHolder = new THREE.Group();
      petalHolder.rotation.y = angle;

      petalMesh.position.set(0, 0.06, 0.32);
      petalMesh.rotation.x = THREE.MathUtils.degToRad(48);
      petalHolder.add(petalMesh);
      midGroup.add(petalHolder);
      midPetals.push(petalMesh);
    }
    lotusRoot.add(midGroup);
    whorlLayers.push({
      group: midGroup,
      basePitch: THREE.MathUtils.degToRad(48),
      breathAmp: 0.05,
      breathSpeed: 0.92,
      breathPhase: 1.1,
      petals: midPetals,
    });

    // Layer 3: Outer Expansive Whorl (10 wide petals, catching warm rim lights)
    const outerGeom = createPetalGeometry(1.7, 1.1, 0.38, 0.2);
    const outerGroup = new THREE.Group();
    const outerPetals: THREE.Mesh[] = [];
    const outerCount = 10;
    for (let i = 0; i < outerCount; i++) {
      const petalMesh = new THREE.Mesh(outerGeom, petalMaterial);
      const angle = (i / outerCount) * Math.PI * 2 + Math.PI / 10;
      const petalHolder = new THREE.Group();
      petalHolder.rotation.y = angle;

      petalMesh.position.set(0, 0.02, 0.42);
      petalMesh.rotation.x = THREE.MathUtils.degToRad(68);
      petalHolder.add(petalMesh);
      outerGroup.add(petalHolder);
      outerPetals.push(petalMesh);
    }
    lotusRoot.add(outerGroup);
    whorlLayers.push({
      group: outerGroup,
      basePitch: THREE.MathUtils.degToRad(68),
      breathAmp: 0.065,
      breathSpeed: 0.82,
      breathPhase: 2.0,
      petals: outerPetals,
    });

    // Layer 4: Calyx Sepals (5 dark green sepals resting underneath)
    const sepalGeom = createPetalGeometry(1.25, 0.65, 0.28, 0.12);
    const sepalGroup = new THREE.Group();
    const sepalCount = 5;
    for (let i = 0; i < sepalCount; i++) {
      const sepalMesh = new THREE.Mesh(sepalGeom, sepalMaterial);
      const angle = (i / sepalCount) * Math.PI * 2 + 0.2;
      const sepalHolder = new THREE.Group();
      sepalHolder.rotation.y = angle;
      sepalMesh.position.set(0, -0.04, 0.38);
      sepalMesh.rotation.x = THREE.MathUtils.degToRad(88);
      sepalHolder.add(sepalMesh);
      sepalGroup.add(sepalHolder);
    }
    lotusRoot.add(sepalGroup);

    // ─── SACRED SEED POD (KARNIKA / TORUS) ───
    const podGroup = new THREE.Group();
    podGroup.position.set(0, 0.14, 0);

    // Inverted golden cone receptacle
    const podGeom = new THREE.CylinderGeometry(0.42, 0.24, 0.28, 36);
    const podMesh = new THREE.Mesh(podGeom, goldMaterial);
    podGroup.add(podMesh);

    // Golden seed carpels on top disc (sacred geometric concentric pattern: 1 center, 6 inner, 12 outer)
    const carpelGeom = new THREE.SphereGeometry(0.036, 12, 12);
    const centerCarpel = new THREE.Mesh(carpelGeom, antherMaterial);
    centerCarpel.position.set(0, 0.145, 0);
    podGroup.add(centerCarpel);

    for (let i = 0; i < 6; i++) {
      const ang = (i / 6) * Math.PI * 2;
      const c = new THREE.Mesh(carpelGeom, antherMaterial);
      c.position.set(Math.cos(ang) * 0.14, 0.145, Math.sin(ang) * 0.14);
      podGroup.add(c);
    }
    for (let i = 0; i < 12; i++) {
      const ang = (i / 12) * Math.PI * 2 + 0.25;
      const c = new THREE.Mesh(carpelGeom, antherMaterial);
      c.position.set(Math.cos(ang) * 0.28, 0.145, Math.sin(ang) * 0.28);
      podGroup.add(c);
    }
    lotusRoot.add(podGroup);

    // ─── GOLDEN STAMEN FILAMENTS RING (KESARA) ───
    const stamenGroup = new THREE.Group();
    stamenGroup.position.set(0, 0.12, 0);
    const stamenCount = 40;
    const filamentGeom = new THREE.CylinderGeometry(0.007, 0.009, 0.18, 8);
    const antherGeom = new THREE.SphereGeometry(0.018, 8, 8);

    for (let i = 0; i < stamenCount; i++) {
      const ang = (i / stamenCount) * Math.PI * 2;
      const r = 0.43;
      const stamenHolder = new THREE.Group();
      stamenHolder.position.set(Math.cos(ang) * r, 0, Math.sin(ang) * r);
      stamenHolder.rotation.y = ang;
      stamenHolder.rotation.z = -0.18; // Flared slightly outward

      const filament = new THREE.Mesh(filamentGeom, goldMaterial);
      filament.position.set(0, 0.09, 0);
      stamenHolder.add(filament);

      const anther = new THREE.Mesh(antherGeom, antherMaterial);
      anther.position.set(0, 0.18, 0);
      stamenHolder.add(anther);

      stamenGroup.add(stamenHolder);
    }
    lotusRoot.add(stamenGroup);

    // ─── SOFT VOLUMETRIC AURA GLOW BILLBOARD ───
    const glowPlaneGeom = new THREE.PlaneGeometry(2.6, 2.6);
    const glowMaterial = new THREE.MeshBasicMaterial({
      map: glowTexture,
      transparent: true,
      opacity: 0.55,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
    });
    const glowMesh = new THREE.Mesh(glowPlaneGeom, glowMaterial);
    glowMesh.position.set(0, -0.05, -0.2);
    glowMesh.rotation.x = THREE.MathUtils.degToRad(20);
    scene.add(glowMesh);

    // ─── FLOATING BOTANICAL PARTICLES & GOLDEN SPORES ───
    const particleCount = 36;
    const particlePositions = new Float32Array(particleCount * 3);
    const particleVelocities: { x: number; y: number; z: number; phase: number; radius: number; baseAngle: number }[] = [];

    for (let i = 0; i < particleCount; i++) {
      const radius = 0.5 + Math.random() * 0.9;
      const baseAngle = Math.random() * Math.PI * 2;
      const y = -0.2 + Math.random() * 1.4;
      const x = Math.cos(baseAngle) * radius;
      const z = Math.sin(baseAngle) * radius;

      particlePositions[i * 3] = x;
      particlePositions[i * 3 + 1] = y;
      particlePositions[i * 3 + 2] = z;

      particleVelocities.push({
        x: (Math.random() - 0.5) * 0.003,
        y: 0.002 + Math.random() * 0.0035,
        z: (Math.random() - 0.5) * 0.003,
        phase: Math.random() * Math.PI * 2,
        radius,
        baseAngle,
      });
    }

    const particleGeom = new THREE.BufferGeometry();
    particleGeom.setAttribute("position", new THREE.BufferAttribute(particlePositions, 3));

    // Particle texture
    const particleCanvas = document.createElement("canvas");
    particleCanvas.width = 64;
    particleCanvas.height = 64;
    const pCtx = particleCanvas.getContext("2d");
    if (pCtx) {
      const pGrad = pCtx.createRadialGradient(32, 32, 2, 32, 32, 30);
      pGrad.addColorStop(0.0, "rgba(255, 235, 160, 1.0)"); // Warm gold core
      pGrad.addColorStop(0.35, "rgba(52, 211, 153, 0.75)"); // Jade aura
      pGrad.addColorStop(1.0, "rgba(16, 185, 129, 0)");
      pCtx.fillStyle = pGrad;
      pCtx.fillRect(0, 0, 64, 64);
    }
    const particleTexture = new THREE.CanvasTexture(particleCanvas);

    const particleMaterial = new THREE.PointsMaterial({
      size: 0.09,
      map: particleTexture,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });

    const particleSystem = new THREE.Points(particleGeom, particleMaterial);
    scene.add(particleSystem);

    // ─── CINEMATIC STUDIO LIGHTING ───
    // 1. Ambient herbal light
    const ambientLight = new THREE.AmbientLight(0x0a2f22, 1.6);
    scene.add(ambientLight);

    // 2. Primary Warm Golden Directional Key Light (from upper right)
    const keyLight = new THREE.DirectionalLight(0xfffae0, 2.5);
    keyLight.position.set(3.0, 5.0, 3.8);
    scene.add(keyLight);

    // 3. Sacred Gold Rim Light (behind & above)
    const rimLight = new THREE.DirectionalLight(0xdfb43a, 3.4);
    rimLight.position.set(-2.4, 4.2, -3.2);
    scene.add(rimLight);

    // 4. Cool Emerald Fill Light (from lower left)
    const fillLight = new THREE.DirectionalLight(0x10b981, 1.4);
    fillLight.position.set(-3.2, 1.8, 2.2);
    scene.add(fillLight);

    // 5. Pulsing Heart Point Light (inside the flower receptacle)
    const heartLight = new THREE.PointLight(0x34d399, 1.9, 3.5, 1.8);
    heartLight.position.set(0, 0.35, 0);
    scene.add(heartLight);

    // ─── INTERACTIVITY & PARALLAX STATE ───
    let targetRotX = THREE.MathUtils.degToRad(32);
    let targetRotY = 0;
    let targetPosX = 0;
    let targetPosY = -0.15;

    let currentRotX = targetRotX;
    let currentRotY = targetRotY;
    let currentPosX = targetPosX;
    let currentPosY = targetPosY;

    const handleMouseMove = (e: MouseEvent) => {
      // Calculate normalized mouse position (-1 to 1) relative to window
      const xNorm = (e.clientX / window.innerWidth) * 2 - 1;
      const yNorm = (e.clientY / window.innerHeight) * 2 - 1;

      // Gentle, subtle 3D response without extreme tilts
      targetRotY = xNorm * 0.18; // Subtle yaw
      targetRotX = THREE.MathUtils.degToRad(32) + yNorm * 0.12; // Subtle pitch
      targetPosX = xNorm * 0.1;
      targetPosY = -0.15 - yNorm * 0.08;
    };

    const handleMouseLeave = () => {
      // Return gently to resting posture
      targetRotX = THREE.MathUtils.degToRad(32);
      targetRotY = 0;
      targetPosX = 0;
      targetPosY = -0.15;
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.addEventListener("mouseleave", handleMouseLeave);

    // ─── INTERSECTION OBSERVER FOR GPU CONSERVATION ───
    let isVisible = true;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          isVisible = entry.isIntersecting;
        });
      },
      { threshold: 0.05 }
    );
    observer.observe(container);

    // Handle container resize
    const handleResize = () => {
      if (!container || !renderer) return;
      const newW = container.clientWidth || 420;
      const newH = container.clientHeight || 420;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    };
    window.addEventListener("resize", handleResize);

    // ─── MAIN ANIMATION LOOP ───
    let animationFrameId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      if (!isVisible || !renderer) return;

      const elapsedTime = clock.getElapsedTime();

      // Organic smooth damping for cursor parallax (smooth lerp)
      const lerpSpeed = 0.045;
      currentRotX += (targetRotX - currentRotX) * lerpSpeed;
      currentRotY += (targetRotY - currentRotY) * lerpSpeed;
      currentPosX += (targetPosX - currentPosX) * lerpSpeed;
      currentPosY += (targetPosY - currentPosY) * lerpSpeed;

      lotusRoot.rotation.x = currentRotX;
      lotusRoot.rotation.y = currentRotY;
      lotusRoot.position.x = currentPosX;
      lotusRoot.position.y = currentPosY;

      if (!prefersReducedMotion) {
        // Continuous slow Ayurvedic floating & gentle breathing
        const floatOffset = Math.sin(elapsedTime * 0.7) * 0.035;
        lotusRoot.position.y = currentPosY + floatOffset;

        // Subtle sacred auto-yaw drift
        lotusRoot.rotation.y = currentRotY + Math.sin(elapsedTime * 0.2) * 0.05;

        // Whorl breathing (organic blossoming & folding pulse)
        whorlLayers.forEach((whorl) => {
          const breath =
            Math.sin(elapsedTime * whorl.breathSpeed + whorl.breathPhase) * whorl.breathAmp;
          whorl.petals.forEach((petal) => {
            petal.rotation.x = whorl.basePitch + breath;
          });
        });

        // Heart light breathing pulse
        const heartIntensity = 1.6 + Math.sin(elapsedTime * 1.5) * 0.4;
        heartLight.intensity = heartIntensity;

        // Volumetric glow breathing pulse & gentle tracking
        glowMesh.position.x = currentPosX * 0.7;
        glowMesh.position.y = currentPosY * 0.7 + floatOffset * 0.5;
        glowMaterial.opacity = 0.48 + Math.sin(elapsedTime * 1.1) * 0.1;

        // Floating particles drift
        const positions = particleGeom.attributes.position.array as Float32Array;
        for (let i = 0; i < particleCount; i++) {
          const v = particleVelocities[i];
          // Gentle orbital swirl + upward drift
          const currentY = positions[i * 3 + 1] + v.y;
          const currentAng = v.baseAngle + elapsedTime * 0.1;
          const r = v.radius + Math.sin(elapsedTime * 0.5 + v.phase) * 0.1;

          positions[i * 3] = Math.cos(currentAng) * r + currentPosX * 0.2;
          positions[i * 3 + 2] = Math.sin(currentAng) * r;

          if (currentY > 1.4) {
            // Reset at bottom
            positions[i * 3 + 1] = -0.3;
          } else {
            positions[i * 3 + 1] = currentY;
          }
        }
        particleGeom.attributes.position.needsUpdate = true;
      }

      renderer.render(scene, camera);
    };

    animate();

    // ─── CLEANUP ON UNMOUNT ───
    return () => {
      cancelAnimationFrame(animationFrameId);
      observer.disconnect();
      window.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", handleResize);

      if (renderer) {
        if (renderer.domElement && container.contains(renderer.domElement)) {
          container.removeChild(renderer.domElement);
        }
        renderer.dispose();
      }

      // Dispose textures & geometries
      petalTexture.dispose();
      glowTexture.dispose();
      particleTexture.dispose();
      innerGeom.dispose();
      midGeom.dispose();
      outerGeom.dispose();
      sepalGeom.dispose();
      podGeom.dispose();
      carpelGeom.dispose();
      filamentGeom.dispose();
      antherGeom.dispose();
      glowPlaneGeom.dispose();
      particleGeom.dispose();

      // Dispose materials
      petalMaterial.dispose();
      sepalMaterial.dispose();
      goldMaterial.dispose();
      antherMaterial.dispose();
      glowMaterial.dispose();
      particleMaterial.dispose();
    };
  }, []);

  if (!isWebGLSupported) {
    // Graceful fallback: return null so standard artwork displays cleanly without errors
    return null;
  }

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-full pointer-events-none select-none overflow-visible ${className}`}
      aria-hidden="true"
    />
  );
}
