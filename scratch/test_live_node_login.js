const email = "node_browser_test@example.com";
const password = "Password123!";
const API_BASE = "http://127.0.0.1:8000";

async function runRealLoginTrace() {
  console.log("=== STEP 1: REGISTER USER VIA REAL FETCH ===");
  const regRes = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: "Node Browser User",
      email: email,
      password: password,
      confirm_password: password
    })
  });

  console.log(`Register Status: ${regRes.status}`);
  const regBody = await regRes.json();
  console.log(`Register Response Body:`, regBody);

  console.log("\n=== STEP 2: FIRST LOGIN VIA REAL FETCH ===");
  const login1Res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  console.log(`Login 1 Status: ${login1Res.status}`);
  const login1Body = await login1Res.json();
  console.log(`Login 1 Response Body:`, login1Body);

  console.log("\n=== STEP 3: LOGOUT VIA REAL FETCH ===");
  const logoutRes = await fetch(`${API_BASE}/api/auth/logout`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${login1Body.access_token}`
    },
    body: JSON.stringify({ refresh_token: login1Body.refresh_token })
  });

  console.log(`Logout Status: ${logoutRes.status}`);
  const logoutBody = await logoutRes.json();
  console.log(`Logout Response Body:`, logoutBody);

  console.log("\n=== STEP 4: SECOND LOGIN VIA REAL FETCH (SAME CREDENTIALS) ===");
  const login2Res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  console.log(`Login 2 Status: ${login2Res.status}`);
  const login2Body = await login2Res.json();
  console.log(`Login 2 Response Body:`, login2Body);
}

runRealLoginTrace().catch(console.error);
