"use client";

console.log("[TEST PAGE] File loaded at:", new Date().toISOString());
console.log("[TEST PAGE] This should appear in browser console");

export default function TestPage() {
  console.log("[TEST PAGE] Component rendering");
  
  return (
    <div style={{ padding: "2rem", background: "#0f172a", color: "#f1f5f9", minHeight: "100vh" }}>
      <h1>TEST PAGE WORKS!</h1>
      <p>If you see this, routing is working.</p>
      <p>Check browser console (F12) for logs.</p>
      <a href="/login" style={{ color: "#818cf8" }}>Go to Login</a>
    </div>
  );
}
