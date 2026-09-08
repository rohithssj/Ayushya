export interface LegalSource {
  title: string;
  act: string;
  section: string;
  url?: string;
  jurisdiction: string;
  relevanceScore?: number;
}

export interface ChatMessageData {
  id: string;
  sender: "user" | "ayushya";
  text: string;
  timestamp: string;
  sources?: LegalSource[];
  confidence?: "High" | "Medium" | "Low";
  disclaimer?: string;
  requiresHumanAssistance?: boolean;
}

export interface ChatRequest {
  message: string;
  analysisId?: string;
  productName?: string;
  jurisdiction?: string;
  language?: string;
  history?: ChatMessageData[];
}

export interface ChatResponse {
  answer: string;
  sources: LegalSource[];
  confidence: "High" | "Medium" | "Low";
  disclaimer: string;
  requiresHumanAssistance: boolean;
}

/**
 * Multilingual Service abstraction for RAG legal intelligence API.
 * Connects frontend to AYUSHYA backend retrieval system.
 * Respects requested language while maintaining official statutory names.
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  // Simulate network delay for realistic RAG retrieval & LLM reasoning
  await new Promise((resolve) => setTimeout(resolve, 1000));

  const query = request.message.toLowerCase();
  const jurisdiction = request.jurisdiction || "India";
  const lang = request.language || "en";
  const product = request.productName ? `for "${request.productName}"` : "";

  // Helper translations for RAG responses preserving official law titles
  const getMultilingualText = (key: string): string => {
    if (lang === "te") {
      if (key === "biodiversity") {
        return `భారత చట్టం ప్రకారం ${product}, ఆయుర్వేద మిశ్రమాలలో జీవ వనరులు లేదా సాంప్రదాయ జ్ఞానాన్ని ఉపయోగించినప్పుడు అక్సెస్ అండ్ బెనిఫిట్ షేరింగ్ (ABS) నిబంధనలను పాటించాలి. నాచురల్ బయోడైవర్సిటీ అథారిటీ (NBA) అనుమతి మరియు వివరాల దాఖలు తప్పనిసరి. (Biological Diversity Act, 2002 & Section 3(p)).`;
      }
      if (key === "patent") {
        return `పేటెంట్ రక్షణ ${product} ఆవిష్కరణ నవీనత మరియు పారిశ్రామిక ఉపయోగంపై ఆధారపడి ఉంటుంది. భారతదేశ పేటెంట్ల చట్టం Section 3(p) ప్రకారం సాంప్రదాయ గ్రంథాలలో నమోదైన ఆయుర్వేద మిశ్రమాలకు నేరుగా పేటెంట్ లభించదు. అయితే, కొత్త ఉత్ప్రేరక సమ్మేళనాలు లేదా ప్రత్యేక ప్రక్రియలకు పేటెంట్ పొందే అవకాశం ఉంది (The Patents Act 1970).`;
      }
      if (key === "regulatory") {
        return `నియంత్రణ నిబంధనలు ${product} ఉత్పత్తి వర్గీకరణపై ఆధారపడి ఉంటాయి. "Ayurveda Aahar" ఉత్పత్తులు FSSAI (Ayurveda Aahar) Regulations 2022 నిబంధనలను పాటించాలి. ప్రామాణిక ఔషధాలకు Drugs and Cosmetics Rules 1945 Rule 158B కింద లైసెన్స్ పొంది ఉండాలి.`;
      }
      return `ఆయుష్య లభ్యమయ్యే చట్టపరమైన ఆధారాలను విశ్లేషించింది ${product}, అయితే సంబంధిత స్పష్టమైన చట్టబద్ధమైన సెక్షన్‌ను కచ్చితంగా గుర్తించలేకపోయింది. నిపుణుల సలహా కొరకు దరఖాస్తు చేసుకోండి.`;
    }

    if (lang === "hi") {
      if (key === "biodiversity") {
        return `भारतीय कानून के तहत ${product}, आयुर्वेदिक संरचनाओं में जैविक संसाधनों या पारंपरिक ज्ञान के उपयोग पर Access and Benefit Sharing (ABS) नियमों का पालन करना अनिवार्य है। नेशनल बायोडायवर्सिटी अथॉरिटी (NBA) से स्वीकृति लेना आवश्यक है। (Biological Diversity Act, 2002 & Section 3(p)).`;
      }
      if (key === "patent") {
        return `पेटेंट सुरक्षा ${product} नवीनता और औद्योगिक उपयोगिता पर निर्भर करती है। भारत के पेटेंट अधिनियम की Section 3(p) के तहत पारंपरिक ग्रंथों में वर्णित आयुर्वेदिक योग गैर-पेटेंट योग्य हैं। हालांकि, नवीन प्रक्रियाओं या विशेष निष्कर्षों के लिए पेटेंट आवेदन किया जा सकता है (The Patents Act 1970).`;
      }
      if (key === "regulatory") {
        return `नियामक आवश्यकताएं ${product} आपके उत्पाद के वर्गीकरण पर निर्भर करती हैं। "Ayurveda Aahar" के तहत आने वाले उत्पादों को FSSAI (Ayurveda Aahar) Regulations 2022 का पालन करना होगा। शास्त्रीय या एएसयू दवाओं को Drugs and Cosmetics Rules 1945 Rule 158B के तहत निर्माण लाइसेंस की आवश्यकता होती है।`;
      }
      return `आयुष्या ने उपलब्ध कानूनी स्रोतों का विश्लेषण किया ${product}, लेकिन किसी विशिष्ट वैधानिक धारा को निश्चित रूप से निर्धारित नहीं कर सका। कृपया विशेषज्ञ परामर्श का अनुरोध करें।`;
    }

    // Default English RAG Responses
    if (key === "biodiversity") {
      return `Under ${jurisdiction} law ${product}, Ayurvedic formulations using biological resources or traditional knowledge require compliance with Access and Benefit Sharing (ABS) mechanisms. Patent applications involving Indian biological entities must disclose source of origin and obtain approval from the National Biodiversity Authority (NBA).`;
    }
    if (key === "patent") {
      return `Patent protection ${product} depends on novelty, inventive step, industrial applicability, and whether statutory exclusions apply. In India, classical Ayurvedic formulations described in traditional texts are non-patentable under Section 3(p) as traditional knowledge. However, novel synergistic combinations or specific non-obvious extracts may be eligible for process or formulation patents.`;
    }
    if (key === "regulatory") {
      return `Regulatory requirements ${product} depend on your product's classification. Products categorized under "Ayurveda Aahar" must comply with FSSAI (Ayurveda Aahar) Regulations, 2022. Classical or ASU (Ayurveda, Siddha, Unani) medicines require manufacturing licenses under Rule 158B of the Drugs & Cosmetics Rules, 1945.`;
    }
    return `AYUSHYA analyzed available legal sources ${product} for your query, but could not confidently determine a specific statutory section. Complex formulation claims, specific herb-herb interactions, or international export considerations may require expert verification.`;
  };

  // 1. Biodiversity queries
  if (query.includes("biodiversity") || query.includes("traditional knowledge") || query.includes("tk") || query.includes("abs")) {
    return {
      answer: getMultilingualText("biodiversity"),
      sources: [
        {
          title: "Biological Diversity Act, 2002",
          act: "Biological Diversity Act",
          section: "Section 3 & Section 6",
          jurisdiction: "India",
          url: "https://nbaindia.org/act",
        },
        {
          title: "TKDL (Traditional Knowledge Digital Library) Guidelines",
          act: "Traditional Knowledge Safeguards",
          section: "Prior Art Defense Guidelines",
          jurisdiction: "India",
          url: "https://www.tkdl.res.in",
        },
      ],
      confidence: "High",
      disclaimer: "⚠️ Informational guidance, not legal advice.",
      requiresHumanAssistance: false,
    };
  }

  // 2. Patent queries
  if (query.includes("patent") || query.includes("formulation") || query.includes("novelty") || query.includes("invent")) {
    return {
      answer: getMultilingualText("patent"),
      sources: [
        {
          title: "The Patents Act, 1970",
          act: "Patents Act, 1970",
          section: "Section 3(p) — Traditional Knowledge Exclusion",
          jurisdiction: "India",
          url: "https://ipindia.gov.in",
        },
        {
          title: "The Patents Act, 1970",
          act: "Patents Act, 1970",
          section: "Section 3(e) — Mere Admixture Exclusion",
          jurisdiction: "India",
          url: "https://ipindia.gov.in",
        },
      ],
      confidence: "Medium",
      disclaimer: "⚠️ Informational guidance, not legal advice.",
      requiresHumanAssistance: false,
    };
  }

  // 3. Regulatory queries
  if (query.includes("regulat") || query.includes("fssai") || query.includes("ayush") || query.includes("license") || query.includes("aahar")) {
    return {
      answer: getMultilingualText("regulatory"),
      sources: [
        {
          title: "Food Safety and Standards (Ayurveda Aahar) Regulations, 2022",
          act: "FSSAI Regulations",
          section: "Regulation 4 & Schedule I",
          jurisdiction: "India",
          url: "https://www.fssai.gov.in",
        },
        {
          title: "Drugs and Cosmetics Rules, 1945",
          act: "Drugs & Cosmetics Act, 1940",
          section: "Rule 158B — Licensing of ASU Drugs",
          jurisdiction: "India",
          url: "https://ayush.gov.in",
        },
      ],
      confidence: "High",
      disclaimer: "⚠️ Informational guidance, not legal advice.",
      requiresHumanAssistance: false,
    };
  }

  // 4. Default response
  return {
    answer: getMultilingualText("default"),
    sources: [
      {
        title: "Ayurvedic Pharmacopoeia of India (API)",
        act: "Pharmacopoeial Standards",
        section: "General Monograph Standards",
        jurisdiction: jurisdiction,
      },
    ],
    confidence: "Low",
    disclaimer: "⚠️ Informational guidance, not legal advice.",
    requiresHumanAssistance: true,
  };
}
