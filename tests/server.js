#!/usr/bin/env node
/* Minimal static file server for local preview/testing.
 * Serves the neta_story site root (parent of this tests/ dir). */
const http = require("http");
const fs   = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const PORT = process.env.PORT || 4178;

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css":  "text/css; charset=utf-8",
  ".js":   "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png":  "image/png",
  ".jpg":  "image/jpeg",
  ".jpeg": "image/jpeg",
  ".avif": "image/avif",
  ".svg":  "image/svg+xml",
  ".ico":  "image/x-icon"
};

http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath === "/") urlPath = "/index.html";
  const filePath = path.join(ROOT, urlPath);

  // prevent path traversal
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end("forbidden"); return; }

  fs.readFile(filePath, (err, buf) => {
    if (err) { res.writeHead(404); res.end("not found: " + urlPath); return; }
    res.writeHead(200, { "Content-Type": TYPES[path.extname(filePath)] || "application/octet-stream" });
    res.end(buf);
  });
}).listen(PORT, () => console.log(`neta-story preview on http://localhost:${PORT}`));
