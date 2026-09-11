import json, os, sys, time, hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.features.product_analysis.domain.product_request import ProductAnalysisRequest, IngredientRecord
from src.features.product_analysis.domain.domain_router import DomainRouter
from src.features.product_analysis.domain.query_builder import QueryBuilder
from src.features.rag.application.hybrid_retrieval_use_case import HybridRetrievalUseCase
from src.features.rag.application.evidence_selection_use_case import EvidenceSelectionUseCase
from src.features.rag.domain.evidence_evaluator import EvidenceEvaluator
from src.features.rag.domain.evidence_selector import select_evidence
from src.features.rag.domain.chunk_quality import is_retrievable_chunk
from src.features.rag.infrastructure.openrouter_provider import (
    OpenRouterProvider, LLMProviderError, LLMResponseError, LLMRateLimitError,
    LLMTimeoutError, LLMAuthError, LLMUnavailableError,
)

def cit_id_for(cid):
    return "cit_" + hashlib.sha1(cid.encode()).hexdigest()[:12] if cid else ""

def track_a():
    print("\n" + "="*70)
    print("TRACK A -- PRODUCT ANALYSIS: PER-DIMENSION EVIDENCE TRACE")
    print("="*70)

    request = ProductAnalysisRequest(
        product_name="Ashwagandha Wellness Tablet",
        product_form="tablet",
        user_selected_classification="Ayurveda-Aahar",
        jurisdiction="India",
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

    print("Dimensions routed: %d" % len(dimensions))
    for d in dimensions:
        print("  [%s] domain=%s" % (d.dimension, d.legal_domain))

    retrieval_uc = HybridRetrievalUseCase(BASE_DIR)
    all_raw = []
    chunk_dim_map = {}

    for tq in targeted_queries:
        print("\n" + "-"*60)
        print("DIMENSION: %s  domain=%s  jur=%s" % (tq.dimension, tq.legal_domain, tq.jurisdiction))
        t0 = time.time()
        output = retrieval_uc.execute(query=tq.query_text, top_k=5,
                                      jurisdiction=tq.jurisdiction, domain=tq.legal_domain)
        elapsed = time.time() - t0
        results = output.get("results", [])
        assessment = output.get("evidence_assessment", {})

        print("  Retrieved: %d results in %.2fs" % (len(results), elapsed))
        print("  Eval: strength=%s  abstain=%s" % (assessment.get("strength"), assessment.get("abstention_recommended")))
        print("  Reasons: %s" % assessment.get("reasons", []))

        for i, r in enumerate(results, 1):
            cid = r.get("chunk_id", "")
            if cid and cid not in chunk_dim_map:
                chunk_dim_map[cid] = tq.dimension
            all_raw.append(r)
            meta = r.get("metadata", {})
            jur_val = (r.get("jurisdiction") or meta.get("jurisdiction") or "").lower()
            dom_val = (r.get("domain") or meta.get("domain") or "").lower()
            doc = (r.get("title") or r.get("document_id") or "")[:45]
            sec = (r.get("section") or meta.get("section") or "")[:30]
            lex = r.get("lexical_rank", 999)
            sem = r.get("semantic_rank", 999)
            rrf = float(r.get("relevance_score") or r.get("hybrid_score") or r.get("score") or 0.0)
            auth = bool(r.get("title") or r.get("document_id"))
            sub = is_retrievable_chunk(r)
            cit = cit_id_for(cid)
            jm = (not tq.jurisdiction) or jur_val == tq.jurisdiction.lower()
            dm = (not tq.legal_domain) or dom_val == tq.legal_domain.lower()
            flags = []
            if not auth: flags.append("NO-AUTH")
            if not sub:  flags.append("NOT-SUB")
            if not jm:   flags.append("JUR-MISMATCH(got=%s)" % jur_val)
            if not dm:   flags.append("DOM-MISMATCH(got=%s)" % dom_val)
            flag_str = "  !! " + " | ".join(flags) if flags else "  OK"
            print("    #%d: rrf=%.5f lex=%s sem=%s  doc=%r  sec=%r  jur=%r  dom=%r  cit=%s%s" % (
                i, rrf, lex, sem, doc, sec, jur_val, dom_val, cit, flag_str))

        sel = select_evidence(results=results, assessment=assessment,
                              jurisdiction=tq.jurisdiction, domain=tq.legal_domain, max_evidence=5)
        sel_count = sel.get("count", 0)
        print("  PER-DIM SELECTION: %d selected from %d retrieved" % (sel_count, len(results)))
        if sel_count == 0:
            print("  *** SELECTION BLOCKED: strength=%s abstain=%s" % (
                assessment.get("strength"), assessment.get("abstention_recommended")))

    print("\n" + "-"*60)
    print("COMBINED AGGREGATE (as run by ProductAnalysisUseCase)")
    seen = set()
    deduped = []
    for r in all_raw:
        cid = r.get("chunk_id") or ""
        if cid and cid in seen: continue
        deduped.append(r)
        if cid: seen.add(cid)

    print("  Total raw: %d  After dedup: %d" % (len(all_raw), len(deduped)))
    combined = EvidenceEvaluator.evaluate(
        results=deduped,
        query="product analysis Ashwagandha Wellness Tablet",
        jurisdiction="India",
        domain=None,
    )
    print("  Combined strength: %s" % combined.get("strength"))
    print("  Combined abstain: %s" % combined.get("abstention_recommended"))
    print("  Combined reasons: %s" % combined.get("reasons", []))

    top_scores = []
    for r in deduped[:5]:
        rrf = float(r.get("relevance_score") or r.get("hybrid_score") or r.get("score") or 0.0)
        jur_val = (r.get("jurisdiction") or r.get("metadata", {}).get("jurisdiction") or "").lower()
        top_scores.append("%.5f(jur=%s)" % (rrf, jur_val))
    print("  Top 5 scores+jur: %s" % ", ".join(top_scores))

    if combined.get("abstention_recommended") or combined.get("strength") == "insufficient":
        print("  *** ABSTENTION GATE TRIGGERS -- UI will show all 'Insufficient Evidence' ***")
    else:
        esc = EvidenceSelectionUseCase()
        full_sel = esc.execute({"results": deduped, "evidence_assessment": combined,
                                "jurisdiction_filter": "India", "domain_filter": None}, max_evidence=25)
        sel_items = full_sel.get("evidence", {}).get("selected", [])
        print("  Full selection (max=25): %d items" % len(sel_items))
        for ev in sel_items[:10]:
            cit = ev.get("citation", {})
            print("    %s  %r  dom=%s  sec=%r" % (
                cit.get("citation_id"), cit.get("title","")[:40],
                cit.get("domain"), cit.get("section","")[:25]))


def track_b():
    print("\n" + "="*70)
    print("TRACK B -- CHAT / OPENROUTER INVESTIGATION")
    print("="*70)

    retrieval_uc = HybridRetrievalUseCase(BASE_DIR)
    esc = EvidenceSelectionUseCase()

    queries = [
        ("TRIPS", "What does the TRIPS Agreement require regarding patent protection?", "India", None),
        ("Trademark", "Can I register a trademark for the brand name of my Ayurvedic medicine?", "India", "trademarks"),
    ]

    for label, q, jur, dom in queries:
        print("\n" + "-"*60)
        print("[%s] query=%r" % (label, q))
        t0 = time.time()
        out = retrieval_uc.execute(query=q, top_k=5, jurisdiction=jur, domain=dom)
        elapsed = time.time() - t0
        results = out.get("results", [])
        assessment = out.get("evidence_assessment", {})
        print("  Retrieved: %d in %.2fs  strength=%s  abstain=%s" % (
            len(results), elapsed, assessment.get("strength"), assessment.get("abstention_recommended")))
        print("  Reasons: %s" % assessment.get("reasons", []))

        for i, r in enumerate(results, 1):
            cid = r.get("chunk_id", "")
            meta = r.get("metadata", {})
            jur_val = (r.get("jurisdiction") or meta.get("jurisdiction") or "").lower()
            dom_val = (r.get("domain") or meta.get("domain") or "").lower()
            doc = (r.get("title") or r.get("document_id") or "")[:45]
            sec = (r.get("section") or meta.get("section") or "")[:30]
            lex = r.get("lexical_rank", 999)
            sem = r.get("semantic_rank", 999)
            rrf = float(r.get("relevance_score") or r.get("hybrid_score") or r.get("score") or 0.0)
            sub = is_retrievable_chunk(r)
            text_low = (r.get("text") or "")[:150].lower()
            cit = cit_id_for(cid)
            sub_flag = "" if sub else "  !!NOT-SUB"
            print("    #%d: rrf=%.5f lex=%s sem=%s  %r  sec=%r  jur=%r  dom=%r  cit=%s%s" % (
                i, rrf, lex, sem, doc, sec, jur_val, dom_val, cit, sub_flag))
            if label == "TRIPS":
                trips_found = "trips" in text_low or "agreement on trade" in text_low
                print("         TRIPS-in-text=%s  snippet=%r" % (trips_found, text_low[:80]))
            if label == "Trademark":
                has_reg = any(s in text_low for s in ["registr", "eligible", "applicat", "class 5", "class 30", "distinct"])
                has_ren = any(s in text_low for s in ["renewal", "removal", "rectif"])
                print("         has_reg=%s  has_renewal=%s  snippet=%r" % (has_reg, has_ren, text_low[:80]))

        sel_out = esc.execute(out)
        sel = sel_out.get("evidence", {}).get("selected", [])
        print("  SELECTION: %d items" % len(sel))
        for ev in sel:
            cit = ev.get("citation", {})
            print("    %s  %r  dom=%s  sec=%r" % (
                cit.get("citation_id"), cit.get("title","")[:40],
                cit.get("domain"), cit.get("section","")[:25]))
        if not sel:
            print("  *** CHAT WILL ABSTAIN")

    print("\n" + "-"*60)
    print("OPENROUTER PROBE")
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    llm_model = os.environ.get("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b")
    fallback_raw = os.environ.get("LLM_FALLBACK_MODELS", "")
    fallbacks = [m.strip() for m in fallback_raw.split(",") if m.strip()]
    print("  Primary: %s" % llm_model)
    print("  Fallbacks: %s" % (fallbacks or "(none)"))
    print("  API key set: %s" % bool(api_key))

    if not api_key:
        print("  SKIP: no API key")
        return

    provider = OpenRouterProvider()
    t0 = time.time()
    try:
        resp = provider.complete(
            system_prompt='Respond with only the JSON object: {"ok": true}',
            user_prompt='Return {"ok": true} and nothing else.',
            max_tokens=30,
            response_format={"type": "json_object"},
        )
        elapsed = time.time() - t0
        print("  Probe SUCCESS in %.2fs" % elapsed)
        try:
            parsed = json.loads(resp)
            print("  Valid JSON keys: %s" % list(parsed.keys()))
        except Exception:
            print("  Non-JSON resp (len=%d)" % len(resp))
    except LLMResponseError as e:
        elapsed = time.time() - t0
        print("  *** LLMResponseError in %.2fs: %s" % (elapsed, e))
        print("  Root cause: empty content or missing content field from model")
    except LLMUnavailableError as e:
        elapsed = time.time() - t0
        print("  LLMUnavailableError in %.2fs: %s" % (elapsed, e))
        print("  NOTE: If this contained 'model output must contain either output text or tool calls'")
        print("  then OpenRouter returned error-in-JSON-body for empty completion.")
    except LLMRateLimitError as e:
        print("  RATE_LIMIT: %s" % e)
    except LLMTimeoutError as e:
        print("  TIMEOUT: %s" % e)
    except LLMAuthError as e:
        print("  AUTH_FAIL: %s" % e)
    except LLMProviderError as e:
        print("  LLMProviderError (%s): %s" % (type(e).__name__, e))

    print("\nSTATIC ANALYSIS of OpenRouterProvider:")
    print("  [OK] choices/message/content missing -> LLMResponseError")
    print("  [OK] content empty/None -> LLMResponseError('OpenRouter returned an empty response.')")
    print("  [!!] error-in-JSON-body -> LLMUnavailableError (not LLMResponseError)")
    print("       'model output must contain either output text or tool calls' arrives as")
    print("       data['error']['message'] -> classified as LLMUnavailableError -> fallback triggered")
    print("       This is CORRECT behavior (fallback), but imprecise error class.")
    print("  [!!] If primary model always returns empty completion, fallback to model 2/3 required.")


def main():
    print("\n" + "#"*70)
    print("AYUSHYA DUAL-TRACK DIAGNOSTIC")
    print("#"*70)
    print("BASE_DIR:", BASE_DIR)
    print("Time:", time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        track_a()
    except Exception as e:
        import traceback
        print("[TRACK A EXCEPTION] %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

    try:
        track_b()
    except Exception as e:
        import traceback
        print("[TRACK B EXCEPTION] %s: %s" % (type(e).__name__, e))
        traceback.print_exc()

    print("\n" + "#"*70 + "\nDIAGNOSTIC COMPLETE\n" + "#"*70)

if __name__ == "__main__":
    main()
