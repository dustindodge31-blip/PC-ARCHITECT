// Proxies AI Architect requests to Gemini so the API key never ships inside
// the app bundle. Requires a valid Supabase auth session (enforced both by
// Supabase's own JWT verification on this function and by needing a user id
// to key the per-user daily rate limit below).
//
// Deploy: supabase functions deploy gemini-proxy
// Secret: supabase secrets set GEMINI_API_KEY=<key>
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const DAILY_LIMIT = 15;
const GEMINI_MODEL = "gemini-2.5-flash";
const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY");
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type",
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: CORS_HEADERS });
  }

  if (!GEMINI_API_KEY) {
    return jsonResponse({ error: "Server misconfigured: GEMINI_API_KEY not set." }, 500);
  }

  // Identify the caller from their own auth token (not the service role) --
  // this is what actually verifies the JWT belongs to a real user.
  const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    global: { headers: { Authorization: req.headers.get("Authorization") ?? "" } },
  });
  const { data: userData, error: userError } = await userClient.auth.getUser();
  if (userError || !userData?.user) {
    return jsonResponse({ error: "Sign in required to use AI Architect." }, 401);
  }
  const userId = userData.user.id;

  // Service-role client bypasses RLS -- needed to read/write another user's
  // row is never the point here, just to manage the shared usage-counter table.
  const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const today = new Date().toISOString().slice(0, 10);

  const { data: usageRow, error: usageError } = await adminClient
    .from("ai_usage")
    .select("count")
    .eq("user_id", userId)
    .eq("usage_date", today)
    .maybeSingle();

  // Fail closed, not open: if the usage table can't be read (missing table,
  // RLS misconfiguration, transient DB error), block the request rather than
  // silently letting the rate limit -- the whole point of this function --
  // be bypassed without anyone noticing.
  if (usageError) {
    return jsonResponse({ error: `Usage check failed: ${usageError.message}` }, 500);
  }

  const currentCount = usageRow?.count ?? 0;
  if (currentCount >= DAILY_LIMIT) {
    return jsonResponse(
      { error: `You've hit today's limit of ${DAILY_LIMIT} AI Architect requests. Try again tomorrow.` },
      429,
    );
  }

  let payload: unknown;
  try {
    payload = await req.json();
  } catch {
    return jsonResponse({ error: "Invalid request body." }, 400);
  }

  const geminiUrl =
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`;

  let geminiResponse: Response;
  try {
    geminiResponse = await fetch(geminiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (e) {
    return jsonResponse({ error: `Couldn't reach Gemini: ${e}` }, 502);
  }

  // Count it whether or not Gemini's response parses cleanly downstream --
  // Gemini bills on receipt, same reasoning as the client-side cap it replaces.
  const { error: incrementError } = await adminClient
    .from("ai_usage")
    .upsert(
      { user_id: userId, usage_date: today, count: currentCount + 1 },
      { onConflict: "user_id,usage_date" },
    );
  if (incrementError) {
    console.error("Failed to record ai_usage count:", incrementError.message);
  }

  const geminiBody = await geminiResponse.text();
  return new Response(geminiBody, {
    status: geminiResponse.status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
  });
});
