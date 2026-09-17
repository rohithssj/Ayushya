from unittest.mock import MagicMock
from src.features.product_analysis.application.product_analysis_use_case import ProductAnalysisUseCase
from src.features.product_analysis.domain.product_request import validate_product_request

mock_llm = MagicMock()
mock_llm.complete.return_value = """{
  "grounded_summary": "AYUSHYA analyzed the formulation under International framework evidence. The Convention on Biological Diversity (CBD) provides broad principles on sovereign rights and access, while the Nagoya Protocol specifies access and benefit-sharing (ABS) mechanisms including prior informed consent (PIC) and mutually agreed terms (MAT). Applicability to this product cannot be determined without provider-country information.",
  "classification": {
    "user_selected": "Ayurveda-Aahar",
    "preliminary_assessment": "AYUSHYA could not independently verify the user-selected Ayurveda-Aahar classification from the available evidence.",
    "evidence_strength": "insufficient",
    "requires_verification": true,
    "supporting_citation_ids": []
  },
  "ip_assessment": [
    {
      "ip_type": "Patent",
      "relevance": "insufficient_evidence",
      "preliminary_assessment": "No product-specific patent protection was established from the retrieved evidence.",
      "reasoning": "The retrieved evidence discusses PCT and TRIPS frameworks but does not contain product-specific patent claims.",
      "evidence_strength": "insufficient",
      "requires_verification": true,
      "supporting_citation_ids": []
    }
  ],
  "regulatory_assessment": [
    {
      "framework": "Convention on Biological Diversity (CBD)",
      "why_applicable": "CBD provides broader international framework principles for biological resources.",
      "relevant_provisions": ["Article 1 Objectives"],
      "evidence_strength": "moderate",
      "requires_verification": true,
      "supporting_citation_ids": ["cit_1"]
    },
    {
      "framework": "Nagoya Protocol on Access and Benefit Sharing",
      "why_applicable": "Nagoya Protocol provides specific ABS framework mechanisms for genetic resource utilization.",
      "relevant_provisions": ["Article 6 Access to Genetic Resources"],
      "evidence_strength": "moderate",
      "requires_verification": true,
      "supporting_citation_ids": ["cit_2"]
    }
  ],
  "tk_biodiversity": {
    "tk_considerations": "International traditional knowledge principles apply under CBD and WIPO frameworks.",
    "biodiversity_considerations": "International ABS and Traditional Knowledge Considerations: Nagoya Protocol mechanisms may apply if biological resources are accessed from a provider country with active domestic ABS measures.",
    "abs_note": "Potentially relevant — applicability not established. Missing facts: country of origin/provider, source location, TK access history.",
    "evidence_strength": "moderate",
    "requires_verification": true,
    "supporting_citation_ids": ["cit_1", "cit_2"],
    "insufficient": false
  },
  "compliance_checklist": [
    {
      "action": "Determine whether prior informed consent requirements apply based on the relevant provider country's applicable ABS framework and the circumstances of access/use.",
      "reason": "Nagoya Protocol Article 6 requires access to be subject to prior informed consent of the provider country where applicable under domestic law.",
      "legal_area": "International ABS Framework",
      "priority": "high",
      "requires_verification": true,
      "supporting_citation_id": "cit_2"
    },
    {
      "action": "Determine whether mutually agreed terms are required and verify whether they have been established.",
      "reason": "Nagoya Protocol Article 5 requires benefit-sharing to be based on mutually agreed terms.",
      "legal_area": "International ABS Framework",
      "priority": "high",
      "requires_verification": true,
      "supporting_citation_id": "cit_2"
    }
  ]
}"""

use_case = ProductAnalysisUseCase('d:/Ayushya', llm_provider=mock_llm)

raw_req_intl = {
    'productName': 'Ashwagandha Wellness Tablet',
    'category': 'Ayurveda-Aahar',
    'form': 'Tablet',
    'description': 'Standardized extract formulation targeted for stress reduction and immunity enhancement using traditional processing methods.',
    'ingredients': [
        {'name': 'Ashwagandha', 'quantity': '500', 'unit': 'mg'},
        {'name': 'Pippali', 'quantity': '50', 'unit': 'mg'},
        {'name': 'Black Pepper', 'quantity': '20', 'unit': 'mg'}
    ],
    'jurisdiction': 'International'
}

req_intl = validate_product_request(raw_req_intl)
res_intl = use_case.execute(req_intl)

print('================================================================================')
print('FINAL VERIFIED ASHWAGANDHA INTERNATIONAL PRODUCT ANALYSIS OUTPUT')
print('================================================================================')
print('Product Name:', res_intl['product_name'])
print('Target Jurisdiction:', res_intl['jurisdiction'])
print('Overall Evidence Strength:', res_intl['evidence_strength'])
print('Abstained:', res_intl['abstained'])

print('\n--- CLASSIFICATION ASSESSMENT ---')
cls = res_intl.get('classification', {})
print('User-Selected:', cls.get('user_selected'))
print('Assessment:', cls.get('preliminary_assessment'))
print('Evidence Strength:', cls.get('evidence_strength'))

print('\n--- IP ASSESSMENT ---')
for ip in res_intl.get('ip_assessment', []):
    print('IP Type:', ip.get('ip_type'), '| Relevance:', ip.get('relevance'), '| Strength:', ip.get('evidence_strength'))
    print('  Assessment:', ip.get('preliminary_assessment'))

print('\n--- REGULATORY ASSESSMENT ---')
for reg in res_intl.get('regulatory_assessment', []):
    print('Framework:', reg.get('framework'), '| Strength:', reg.get('evidence_strength'))
    print('  Why Applicable:', reg.get('why_applicable'))

print('\n--- INTERNATIONAL ABS & TRADITIONAL KNOWLEDGE CONSIDERATIONS ---')
tk = res_intl.get('tk_biodiversity') or {}
print('Biodiversity Considerations:', tk.get('biodiversity_considerations'))
print('ABS Note:', tk.get('abs_note'))
print('Evidence Strength:', tk.get('evidence_strength'))

print('\n--- COMPLIANCE CHECKLIST ---')
for item in res_intl.get('compliance_checklist', []):
    print('- Action:', item.get('action'))
    print('  Reason:', item.get('reason'))
