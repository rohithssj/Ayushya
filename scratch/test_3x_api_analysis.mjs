const payload = {
  productName: "Ashwagandha Wellness Tablet",
  category: "Ayurveda-Aahar",
  form: "Tablet",
  description: "Standardized extract formulation targeted for stress reduction and immunity enhancement using traditional processing methods.",
  ingredients: [
    { name: "Ashwagandha (Withania somnifera)", quantity: "500", unit: "mg" },
    { name: "Pipali (Piper longum)", quantity: "50", unit: "mg" },
    { name: "Black Pepper", quantity: "25", unit: "mg" }
  ],
  jurisdiction: "India"
};

async function testRun(runNum) {
  console.log(`\n--- Starting Product Analysis HTTP Run #${runNum} ---`);
  const startTime = Date.now();
  const res = await fetch("http://localhost:3000/api/analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  console.log(`Run #${runNum} Response Status: ${res.status} (took ${duration}s)`);

  if (!res.ok) {
    const errText = await res.text();
    console.error(`Run #${runNum} FAILED:`, errText);
    return false;
  }

  const data = await res.json();
  console.log(`Run #${runNum} SUCCESS: ID=${data.id}`);
  console.log(`  - evidence_strength: ${data.evidence_strength}`);
  console.log(`  - abstained: ${data.abstained}`);
  console.log(`  - citations count: ${data.citations?.length}`);
  console.log(`  - classification present: ${Boolean(data.classification)}`);
  console.log(`  - ip_assessment count: ${data.ip_assessment?.length}`);
  console.log(`  - regulatory_assessment count: ${data.regulatory_assessment?.length}`);
  console.log(`  - tk_biodiversity present: ${Boolean(data.tk_biodiversity)}`);
  console.log(`  - compliance_checklist count: ${data.compliance_checklist?.length}`);
  return true;
}

async function main() {
  for (let i = 1; i <= 3; i++) {
    const ok = await testRun(i);
    if (!ok) {
      console.error(`Stopped due to failure on run #${i}`);
      process.exit(1);
    }
  }
  console.log("\nALL 3 CONSECUTIVE HTTP RUNS RETURNED HTTP 200 SUCCESS!");
}

main().catch(err => {
  console.error("Fatal test error:", err);
  process.exit(1);
});
