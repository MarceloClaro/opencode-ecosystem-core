// Worker que serve o site estático + áudios do podcast a partir do R2.
// URL final: https://molambudos-podcast.<SEU-SUBDOMINIO>.workers.dev
// Suporta Range (seek em players de áudio/vídeo), HEAD e GET.

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".xml": "application/rss+xml; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".mmd": "text/plain; charset=utf-8",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".pdf": "application/pdf",
  ".mp4": "video/mp4",
  ".m4a": "audio/mp4",
  ".mp3": "audio/mpeg",
  ".zip": "application/zip",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let path = decodeURIComponent(url.pathname).replace(/^\/+/, "");
    if (path === "" || path.endsWith("/")) path = path + "index_podcast.html";

    const range = request.headers.get("Range");
    const obj = await env.BUCKET.get(path, range ? { range } : undefined);

    if (obj === null) {
      return new Response("404 Not Found", { status: 404 });
    }

    const dot = path.lastIndexOf(".");
    const ext = dot >= 0 ? path.substring(dot).toLowerCase() : "";
    const headers = new Headers();
    headers.set("Content-Type", MIME[ext] || "application/octet-stream");
    headers.set("Cache-Control", "public, max-age=3600");
    headers.set("Accept-Ranges", "bytes");

    // HEAD: só cabeçalhos
    if (request.method === "HEAD") {
      headers.set("Content-Length", obj.range ? String(obj.range.end - obj.range.offset + 1) : String(obj.size));
      return new Response(null, { status: 200, headers });
    }

    // GET com Range (seek no player)
    if (obj.range) {
      headers.set("Content-Range", `bytes ${obj.range.offset}-${obj.range.end}/${obj.range.total}`);
      headers.set("Content-Length", String(obj.range.end - obj.range.offset + 1));
      return new Response(obj.body, { status: 206, headers });
    }

    headers.set("Content-Length", String(obj.size));
    return new Response(obj.body, { status: 200, headers });
  },
};