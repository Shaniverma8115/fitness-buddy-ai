/**
 * Fitness Buddy — Local Proxy Server
 * Handles IAM token exchange + watsonx.ai API calls server-side (no CORS issues).
 * Run: node server.js
 * Then open: http://localhost:3000
 */

const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");
const url = require("url");

const PORT = 3000;
const API_KEY = "0WeqfqiHKVKp-CFVrBD2NKSL49yJ99OvFxp85sPf9IRB";
const PROJECT_ID = "76edf6b0-8919-446e-93dc-43e0b6a7e481";
const MODEL_ID = "ibm/granite-4-h-small";

let cachedToken = null;
let tokenExpiry = 0;

function getIAMToken(cb) {
  const now = Date.now();
  if (cachedToken && now < tokenExpiry) return cb(null, cachedToken);

  const postData = `grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${API_KEY}`;
  const options = {
    hostname: "iam.cloud.ibm.com",
    path: "/identity/token",
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      "Content-Length": Buffer.byteLength(postData),
    },
  };

  const req = https.request(options, (res) => {
    let data = "";
    res.on("data", (chunk) => (data += chunk));
    res.on("end", () => {
      try {
        const json = JSON.parse(data);
        cachedToken = json.access_token;
        tokenExpiry = now + (json.expires_in - 60) * 1000;
        cb(null, cachedToken);
      } catch (e) {
        cb(new Error("IAM parse error: " + data));
      }
    });
  });
  req.on("error", cb);
  req.write(postData);
  req.end();
}

function callWatsonx(token, messages, cb) {
  const payload = JSON.stringify({
    model_id: MODEL_ID,
    project_id: PROJECT_ID,
    messages: messages,
    parameters: { max_new_tokens: 900, temperature: 0.7, repetition_penalty: 1.1 },
  });

  const options = {
    hostname: "us-south.ml.cloud.ibm.com",
    path: "/ml/v1/text/chat?version=2023-05-29",
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json",
      "Content-Length": Buffer.byteLength(payload),
    },
  };

  const req = https.request(options, (res) => {
    let data = "";
    res.on("data", (chunk) => (data += chunk));
    res.on("end", () => cb(null, res.statusCode, data));
  });
  req.on("error", cb);
  req.write(payload);
  req.end();
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);

  // CORS headers for local dev
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  // ── Serve index.html ──────────────────────────────────────────────
  if (req.method === "GET" && (parsedUrl.pathname === "/" || parsedUrl.pathname === "/index.html")) {
    const filePath = path.join(__dirname, "index.html");
    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(500); return res.end("Cannot read index.html"); }
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(data);
    });
    return;
  }

  // ── /chat proxy endpoint ──────────────────────────────────────────
  if (req.method === "POST" && parsedUrl.pathname === "/chat") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      let messages;
      try {
        messages = JSON.parse(body).messages;
        if (!Array.isArray(messages)) throw new Error("messages must be array");
      } catch (e) {
        res.writeHead(400, { "Content-Type": "application/json" });
        return res.end(JSON.stringify({ error: "Bad request: " + e.message }));
      }

      getIAMToken((err, token) => {
        if (err) {
          res.writeHead(500, { "Content-Type": "application/json" });
          return res.end(JSON.stringify({ error: "IAM error: " + err.message }));
        }

        callWatsonx(token, messages, (err2, statusCode, data) => {
          if (err2) {
            res.writeHead(500, { "Content-Type": "application/json" });
            return res.end(JSON.stringify({ error: "watsonx error: " + err2.message }));
          }
          res.writeHead(statusCode, { "Content-Type": "application/json" });
          res.end(data);
        });
      });
    });
    return;
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, () => {
  console.log(`\n✅ Fitness Buddy server running!`);
  console.log(`👉 Open in browser: http://localhost:${PORT}\n`);
});
