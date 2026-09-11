import json, os, sys, time, hashlib, re

BASE_DIR = "D:/Ayushya"
sys.path.insert(0, BASE_DIR)

env_path = "D:/Ayushya/.env.local"
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k not in os.environ:
                    os.environ[k] = v
    print("Loaded .env.local  API key set:", bool(os.environ.get("OPENROUTER_API_KEY","").strip()))
    print("  Model:", os.environ.get("LLM_MODEL","not set"))
    print("  Fallbacks:", os.environ.get("LLM_FALLBACK_MODELS","none"))

from src.features.rag.infrastructure.lexical_retriever import LexicalRetriever
from src.features.rag.infrastructure.embedding_retriever import EmbeddingRetriever
from src.features.rag.infrastructure.hybrid_retriever import HybridRetriever
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase
from src.features.rag.application.evidence_selection_use_case import EvidenceSelectionUseCase
from src.features.rag.domain.chunk_quality import is_retrievable_chunk

processed_dir = os.path.join(BASE_DIR, "data", "processed")
store_dir = os.path.join(BASE_DIR, "data", "embeddings", "legal_chunks")
lexical = LexicalRetriever(processed_dir)
embedding = EmbeddingRetriever(store_dir)
hybrid = HybridRetriever(lexical, embedding)

print("\n" + "="*70)
print("TRIPS RETRIEVAL TRACE")
print("="*70)

trips_q = "What does the TRIPS Agreement require regarding patent protection?"
print("Query:", repr(trips_q))

print("\n[LEX no-filter top-15]")
lex_all = lexical.search(query=trips_q, top_k=15, jurisdiction=None, domain=None)
trips_lex = [r for r in lex_all if "trips" in str(r.chunk.get("domain","")).lower() or "trips" in str(r.chunk.get("document_id","")).lower()]
print("Results: %d  TRIPS in top-15: %d" % (len(lex_all), len(trips_lex)))
for i, r in enumerate(lex_all[:15], 1):
    c = r.chunk
    is_t = "trips" in str(c.get("domain","")).lower()
    print("  lex#%d score=%.4f  doc=%r  sec=%r  jur=%r  dom=%r%s" % (
        i, r.score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], c.get("jurisdiction",""), c.get("domain",""),
        " <<TRIPS>>" if is_t else ""))

print("\n[SEM no-filter top-15]")
emb_all = embedding.search(query=trips_q, top_k=15, jurisdiction=None, domain=None)
trips_emb = [r for r in emb_all if "trips" in str(r.chunk.get("domain","")).lower()]
print("Results: %d  TRIPS in top-15: %d" % (len(emb_all), len(trips_emb)))
for i, r in enumerate(emb_all[:15], 1):
    c = r.chunk
    is_t = "trips" in str(c.get("domain","")).lower()
    print("  sem#%d score=%.4f  doc=%r  sec=%r  jur=%r  dom=%r%s" % (
        i, r.score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], c.get("jurisdiction",""), c.get("domain",""),
        " <<TRIPS>>" if is_t else ""))

print("\n[RRF no-filter top-10]")
rrf_nf = hybrid.search(query=trips_q, top_k=10, jurisdiction=None, domain=None)
for i, r in enumerate(rrf_nf, 1):
    c = r.chunk
    is_t = "trips" in str(c.get("domain","")).lower()
    print("  rrf#%d hybrid=%.5f lex=%d sem=%d  doc=%r  sec=%r  jur=%r  dom=%r%s" % (
        i, r.hybrid_score, r.lexical_rank, r.semantic_rank,
        (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], c.get("jurisdiction",""), c.get("domain",""),
        " <<TRIPS>>" if is_t else ""))

print("\n[RRF jur=India (current behavior)]")
rrf_india = hybrid.search(query=trips_q, top_k=5, jurisdiction="India", domain=None)
for i, r in enumerate(rrf_india, 1):
    c = r.chunk
    print("  rrf#%d hybrid=%.5f  doc=%r  sec=%r  jur=%r  dom=%r" % (
        i, r.hybrid_score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], c.get("jurisdiction",""), c.get("domain","")))
print("  CONCLUSION: jur=India filter removes International TRIPS chunks -> 0 TRIPS in results")

print("\n[RRF jur=International dom=trips]")
rrf_intl = hybrid.search(query=trips_q, top_k=5, jurisdiction="International", domain="trips")
for i, r in enumerate(rrf_intl, 1):
    c = r.chunk
    print("  rrf#%d hybrid=%.5f  doc=%r  sec=%r  jur=%r  dom=%r" % (
        i, r.hybrid_score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], c.get("jurisdiction",""), c.get("domain","")))
    snip = str(c.get("text","")).lower()[:120]
    print("    text: %r" % snip)

print("\n" + "="*70)
print("TRADEMARK RETRIEVAL TRACE")
print("="*70)

tm_q = "Can I register a trademark for the brand name of my Ayurvedic medicine?"

def tm_classify(text):
    t = text.lower()
    flags = []
    if any(s in t for s in ["registrable","absolute ground","relative ground","not registrable","distinctive","class 5","class 30","eligib","section 9","section 11","section 18","application for registration"]): flags.append("REG/ELIG")
    if any(s in t for s in ["renewal","section 58","notice before removal"]): flags.append("REMOVAL/RENEWAL")
    if any(s in t for s in ["rectif","section 97"]): flags.append("RECTIFY")
    return "|".join(flags) if flags else "other"

print("\n[LEX jur=India dom=trademarks top-15]")
lex_tm = lexical.search(query=tm_q, top_k=15, jurisdiction="India", domain="trademarks")
for i, r in enumerate(lex_tm[:15], 1):
    c = r.chunk
    print("  lex#%d score=%.4f  doc=%r  sec=%r  [%s]" % (
        i, r.score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], tm_classify(c.get("text",""))))

print("\n[SEM jur=India dom=trademarks top-15]")
emb_tm = embedding.search(query=tm_q, top_k=15, jurisdiction="India", domain="trademarks")
for i, r in enumerate(emb_tm[:15], 1):
    c = r.chunk
    print("  sem#%d score=%.4f  doc=%r  sec=%r  [%s]" % (
        i, r.score, (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], tm_classify(c.get("text",""))))

print("\n[RRF jur=India dom=trademarks top-10]")
rrf_tm = hybrid.search(query=tm_q, top_k=10, jurisdiction="India", domain="trademarks")
for i, r in enumerate(rrf_tm, 1):
    c = r.chunk
    print("  rrf#%d hybrid=%.5f lex=%d sem=%d  doc=%r  sec=%r  [%s]" % (
        i, r.hybrid_score, r.lexical_rank, r.semantic_rank,
        (c.get("title") or c.get("document_id") or "")[:40],
        str(c.get("section",""))[:25], tm_classify(c.get("text",""))))

print("\n[Trade Marks Act registration sections in corpus]")
with open(os.path.join(processed_dir, "india_trademark_act_1999_chunks.json"), encoding="utf-8") as f:
    tm_act = json.load(f)
reg_chunks = [(str(c.get("section","")), (c.get("title") or c.get("document_id") or "")[:35])
              for c in tm_act if isinstance(c,dict) and any(s in str(c.get("text","")).lower()
              for s in ["registrable","absolute ground","relative ground","not registrable","distinctive"])]
print("Registration-related chunks in Act:", len(reg_chunks))
for sec, title in reg_chunks[:8]:
    print("  sec=%r  %r" % (sec, title))

print("\n" + "="*70)
print("PRODUCT ANALYSIS -- REAL LLM PROBE")
print("="*70)

api_key = os.environ.get("OPENROUTER_API_KEY","").strip()
if not api_key:
    print("SKIP: no API key")
else:
    from src.features.product_analysis.domain.product_request import ProductAnalysisRequest, IngredientRecord
    from src.features.product_analysis.domain.domain_router import DomainRouter
    from src.features.product_analysis.domain.query_builder import QueryBuilder
    from src.features.product_analysis.domain.analysis_prompt import build_product_evidence_block, build_product_analysis_prompt
    from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
    from src.features.product_analysis.application.structured_response_parser import parse_structured_analysis_response
    from src.features.rag.infrastructure.openrouter_provider import (
        OpenRouterProvider, LLMProviderError, LLMResponseError,
        LLMRateLimitError, LLMTimeoutError, LLMAuthError, LLMUnavailableError,
    )

    request = ProductAnalysisRequest(
        product_name="Ashwagandha Wellness Tablet", product_form="tablet",
        user_selected_classification="Ayurveda-Aahar", jurisdiction="India",
        ingredients=[
            IngredientRecord(name="Ashwagandha (Withania somnifera)", quantity="500", unit="mg"),
            IngredientRecord(name="Pippali (Piper longum)", quantity="50", unit="mg"),
            IngredientRecord(name="Black Pepper", quantity="25", unit="mg"),
        ],
        description="Standardized herbal tablet formulation intended for general wellness, using traditional processing methods.",
    )

    router = DomainRouter()
    builder = QueryBuilder()
    dimensions = router.route(request)
    targeted_queries = builder.build_queries(request, dimensions)

    retrieval_uc = HybridRetrievalUseCase(BASE_DIR)
    esc = EvidenceSelectionUseCase()

    all_raw = []
    chunk_dim_map = {}
    for tq in targeted_queries:
        out = retrieval_uc.execute(query=tq.query_text, top_k=5, jurisdiction=tq.jurisdiction, domain=tq.legal_domain)
        for r in out.get("results", []):
            cid = r.get("chunk_id") or ""
            if cid not in chunk_dim_map: chunk_dim_map[cid] = tq.dimension
            all_raw.append(r)

    seen = set()
    deduped = []
    for r in all_raw:
        cid = r.get("chunk_id") or ""
        if cid and cid in seen: continue
        deduped.append(r)
        if cid: seen.add(cid)

    combined = EvidenceEvaluator.evaluate(results=deduped, query="product analysis Ashwagandha Wellness Tablet",
                                          jurisdiction=request.jurisdiction, domain=None)
    retrieval_combined = {"results": deduped, "evidence_assessment": combined,
                          "jurisdiction_filter": request.jurisdiction, "domain_filter": None}
    full_sel = esc.execute(retrieval_combined, max_evidence=25)
    all_selected = full_sel.get("evidence",{}).get("selected",[])

    # Diversity-aware cap
    from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
    llm_evidence = ProductAnalysisUseCase._select_llm_evidence(all_selected, chunk_dim_map, cap=10)

    valid_cit_ids = {ev.get("citation",{}).get("citation_id","") for ev in llm_evidence if ev.get("citation",{}).get("citation_id")}
    print("Evidence to LLM: %d items" % len(llm_evidence))
    print("Valid citation IDs: %d  IDs: %s" % (len(valid_cit_ids), sorted(valid_cit_ids)))

    evidence_block = build_product_evidence_block(llm_evidence)
    system_prompt, user_prompt = build_product_analysis_prompt(request, evidence_block, [d.legal_domain for d in dimensions])
    print("Total prompt chars: %d" % (len(system_prompt)+len(user_prompt)))

    provider = OpenRouterProvider()
    print("\nCalling LLM...")
    t0 = time.time()
    raw_answer = None
    llm_error_type = None

    try:
        raw_answer = provider.complete(system_prompt=system_prompt, user_prompt=user_prompt,
                                       max_tokens=4000, response_format={"type": "json_object"})
        elapsed = time.time()-t0
        print("LLM SUCCESS in %.2fs" % elapsed)
        print("Response length: %d chars" % len(raw_answer))
        print("Response start: %r" % raw_answer[:100])
        print("Response end:   %r" % raw_answer[-60:])
        stripped = raw_answer.strip()
        print("Starts {: %s  Ends }: %s" % (stripped.startswith("{"), stripped.endswith("}")))

    except LLMResponseError as e:
        elapsed = time.time()-t0
        llm_error_type = "LLMResponseError"
        print("LLMResponseError (%.2fs): %s" % (elapsed, e))
    except LLMUnavailableError as e:
        elapsed = time.time()-t0
        llm_error_type = "LLMUnavailableError"
        print("LLMUnavailableError (%.2fs): %s" % (elapsed, e))
    except LLMRateLimitError as e:
        elapsed = time.time()-t0
        llm_error_type = "LLMRateLimitError"
        print("LLMRateLimitError (%.2fs): %s" % (elapsed, e))
    except LLMTimeoutError as e:
        elapsed = time.time()-t0
        llm_error_type = "LLMTimeoutError"
        print("LLMTimeoutError (%.2fs): %s" % (elapsed, e))
    except LLMAuthError as e:
        elapsed = time.time()-t0
        llm_error_type = "LLMAuthError"
        print("LLMAuthError (%.2fs): %s" % (elapsed, e))
    except LLMProviderError as e:
        elapsed = time.time()-t0
        llm_error_type = type(e).__name__
        print("LLMProviderError[%s] (%.2fs): %s" % (type(e).__name__, elapsed, e))

    if raw_answer is not None:
        parsed = parse_structured_analysis_response(raw_answer, valid_cit_ids)
        print("\nPARSER OUTPUT:")
        print("  _parse_fallback:", parsed.get("_parse_fallback"))
        print("  _fallback_reason:", parsed.get("_fallback_reason",""))
        print("  grounded_summary:", "PRESENT (len=%d)" % len(parsed.get("grounded_summary","") or "") if parsed.get("grounded_summary") else "NULL")
        cls = parsed.get("classification")
        print("  classification:", list(cls.keys()) if isinstance(cls,dict) else repr(cls))
        print("  ip_assessment items:", len(parsed.get("ip_assessment",[])))
        print("  regulatory_assessment items:", len(parsed.get("regulatory_assessment",[])))
        print("  tk_biodiversity:", "dict" if isinstance(parsed.get("tk_biodiversity"),dict) else repr(parsed.get("tk_biodiversity")))
        print("  compliance_checklist items:", len(parsed.get("compliance_checklist",[])))
        # Citation diagnostics
        all_cit_in_resp = set(re.findall(r"cit_[a-f0-9]{12}", raw_answer))
        valid_matched = all_cit_in_resp & valid_cit_ids
        invalid_halluci = all_cit_in_resp - valid_cit_ids
        print("\n  Citation ID diagnostics:")
        print("    Supplied to LLM:", len(valid_cit_ids))
        print("    Found in response:", len(all_cit_in_resp))
        print("    Matched valid:", len(valid_matched))
        print("    Not in supplied set:", len(invalid_halluci))
        if invalid_halluci: print("    Invalid IDs:", sorted(invalid_halluci))
        if parsed.get("_parse_fallback"):
            print("\n  *** PARSE FALLBACK = TRUE -> all dimensions show Insufficient Evidence ***")
            s = raw_answer.strip()
            if s.startswith("```"): print("  CAUSE: Markdown code fence wrapping")
            elif s.startswith("{"): 
                try:
                    test = json.loads(s)
                    print("  json.loads OK - issue is in _strip_markdown or extraction. Keys:", list(test.keys())[:10])
                except json.JSONDecodeError as je:
                    print("  JSON error at pos %d: %s" % (je.pos, je.msg))
                    print("  Context: %r" % s[max(0,je.pos-40):je.pos+60])
            else: print("  CAUSE: Response not JSON. First 200: %r" % s[:200])
        else:
            print("\n  Parse succeeded.")
            cls = parsed.get("classification") or {}
            if isinstance(cls, dict):
                print("  classification.evidence_strength:", cls.get("evidence_strength","?"))
                print("  classification.preliminary_assessment:", repr(str(cls.get("preliminary_assessment",""))[:80]))
            ip = parsed.get("ip_assessment",[])
            for item in ip[:2]:
                print("  ip_item: relevance=%s strength=%s cits=%s" % (item.get("relevance"), item.get("evidence_strength"), item.get("supporting_citation_ids",[])))
            cc = parsed.get("compliance_checklist",[])
            print("  compliance items with valid citation:", sum(1 for c in cc if c.get("supporting_citation_id")))

print("\n" + "#"*70 + "\nTRACE COMPLETE\n" + "#"*70)
