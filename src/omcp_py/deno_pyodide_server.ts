import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import initPyodide, { PyodideInterface } from "npm:pyodide@0.23.4";

let pyodide: PyodideInterface | null = null;

async function ensurePyodide() {
  if (!pyodide) {
    pyodide = await initPyodide();
  }
  return pyodide;
}

console.log("Starting Deno Pyodide server on :8000");

serve(async (req) => {
  if (req.method === "POST" && new URL(req.url).pathname === "/run") {
    const { code } = await req.json();
    try {
      const py = await ensurePyodide();
      const result = py.runPython(code);
      return new Response(JSON.stringify({ result }), { status: 200 });
    } catch (e) {
      return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
    }
  }
  return new Response("Send POST to /run with { code }", { status: 404 });
}, { port: 8000 });
