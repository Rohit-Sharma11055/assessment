import { useState } from "react";
import { Landmark, LockKeyhole, UserRound } from "lucide-react";
import api from "../api/client";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post("auth/token/", {
        username,
        password,
      });

      sessionStorage.setItem("access_token", response.data.access);
      sessionStorage.setItem("refresh_token", response.data.refresh);

      // Fetch the authenticated user's actual profile and role.
      const profile = await api.get("auth/me/");
      const user = profile.data;

      sessionStorage.setItem("username", user.username);
      sessionStorage.setItem("user_role", user.role);
      sessionStorage.setItem(
        "home_branch_id",
        user.home_branch_id == null ? "" : String(user.home_branch_id)
      );
      sessionStorage.setItem(
        "home_branch_name",
        user.home_branch_name || ""
      );

      onLogin();
    } catch (err) {
      sessionStorage.removeItem("access_token");
      sessionStorage.removeItem("refresh_token");
      sessionStorage.removeItem("username");
      sessionStorage.removeItem("user_role");

      setError(
        err.response?.data?.detail ||
          err.response?.data?.error ||
          "Login failed. Check your credentials and user profile endpoint."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-5">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
        <div className="mb-8 flex items-center gap-3">
          <div className="rounded-xl bg-blue-700 p-3 text-white">
            <Landmark size={26} />
          </div>
          <div>
            <h1 className="text-2xl font-bold">CMRS</h1>
            <p className="text-sm text-slate-500">
              Cash management portal
            </p>
          </div>
        </div>

        <h2 className="text-xl font-bold">Welcome back</h2>
        <p className="mt-2 text-sm text-slate-500">
          Sign in to access your workspace.
        </p>

        <form onSubmit={handleSubmit} className="mt-7 space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium">
              Username
            </label>
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 px-3 focus-within:border-blue-600">
              <UserRound size={18} className="text-slate-400" />
              <input
                required
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full py-3 text-sm outline-none"
                placeholder="Your username"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Password
            </label>
            <div className="flex items-center gap-3 rounded-xl border border-slate-200 px-3 focus-within:border-blue-600">
              <LockKeyhole size={18} className="text-slate-400" />
              <input
                required
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full py-3 text-sm outline-none"
                placeholder="Your password"
              />
            </div>
          </div>

          {error && (
            <p
              role="alert"
              className="rounded-lg bg-red-50 p-3 text-sm text-red-700"
            >
              {error}
            </p>
          )}

          <button
            disabled={loading}
            className="w-full rounded-xl bg-blue-700 py-3 font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          Authorized users only
        </p>
      </div>
    </main>
  );
}
