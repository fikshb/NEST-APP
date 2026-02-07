"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { setToken } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || "Login failed");
      }

      const data = await res.json();
      setToken(data.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-softWhite">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-[28px] font-heading font-semibold text-teal-900">
            NestApp
          </h1>
          <p className="text-sm font-ui text-text-muted mt-1">
            Serviced Apartment Management
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-modal shadow-soft p-8 space-y-5"
        >
          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">
              Username
            </label>
            <input
              type="text"
              className="input-field w-full"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
            />
          </div>

          <div>
            <label className="text-sm font-ui text-text-secondary mb-1 block">
              Password
            </label>
            <input
              type="password"
              className="input-field w-full"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <p className="text-sm text-feedback-danger font-ui">{error}</p>
          )}

          <button
            type="submit"
            className="btn-primary w-full"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="text-center text-[11px] font-ui text-text-muted mt-6">
          PRD v8.1
        </p>
      </div>
    </div>
  );
}
