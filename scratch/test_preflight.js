async function testCorsPreflight() {
  console.log("=== TESTING CORS PREFLIGHT OPTIONS REQUEST ===");
  const optionsRes = await fetch("http://127.0.0.1:8000/api/auth/login", {
    method: "OPTIONS",
    headers: {
      "Origin": "http://localhost:3000",
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "content-type"
    }
  });

  console.log(`Preflight Status: ${optionsRes.status}`);
  console.log("Preflight Headers:");
  for (const [key, value] of optionsRes.headers.entries()) {
    console.log(`  ${key}: ${value}`);
  }

  console.log("\n=== TESTING ACTUAL LOGIN POST REQUEST ===");
  const postRes = await fetch("http://127.0.0.1:8000/api/auth/login", {
    method: "POST",
    headers: {
      "Origin": "http://localhost:3000",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: "annuysfavv@gmail.com",
      password: "Annu@199500"
    })
  });

  console.log(`Post Login Status: ${postRes.status}`);
  const data = await postRes.json();
  console.log("Post Login Response Data:", data);
}

testCorsPreflight().catch(console.error);
