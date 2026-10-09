import { useEffect, useState } from "react";
import api from "../api/client";
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from "lucide-react";

export default function Reconciliation() {
  const role = sessionStorage.getItem("user_role") || "";
  const canSubmit = role === "Branch Manager" || role === "Administrator";
  const canVerify = role === "Branch Manager" || role === "Administrator";

  const [submissions, setSubmissions] = useState([]);
  const [receipts, setReceipts] = useState([]);
  const [selected, setSelected] = useState([]);
  const [actualAmounts, setActualAmounts] = useState({});
  const [notes, setNotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const requests = [api.get("reconciliation/")];
      if (canSubmit) requests.push(api.get("reconciliation/?type=receipts"));
      const responses = await Promise.all(requests);
      setSubmissions(responses[0].data.results || responses[0].data);
      setReceipts(canSubmit ? (responses[1].data.results || responses[1].data) : []);
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || "Could not load reconciliation data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const submitCash = async () => {
    if (!selected.length) {
      setError("Select at least one collected receipt.");
      return;
    }
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api.post("reconciliation/", { receipt_ids: selected });
      setSelected([]);
      setSuccess("Reconciliation confirmation submitted successfully.");
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || "Could not submit reconciliation.");
    } finally {
      setBusy(false);
    }
  };

  const verify = async (submission, action) => {
    const actual = actualAmounts[submission.id];
    if (action === "approve" && (actual === undefined || actual === "")) {
      setError("Enter the actual deposited amount to confirm it.");
      return;
    }
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await api.post(`reconciliation/${submission.id}/verify/`, {
        action,
        ...(action === "approve" ? { actual_amount: actual } : {}),
        notes: notes[submission.id] || "",
      });
      setSuccess(`Reconciliation ${submission.submission_reference || submission.reference} ${action === "approve" ? "confirmed" : "rejected"}.`);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || "Unable to update reconciliation.");
    } finally {
      setBusy(false);
    }
  };

  const money = (value) => `₹${Number(value || 0).toLocaleString("en-IN", {
    minimumFractionDigits: 2, maximumFractionDigits: 2,
  })}`;

  const eligibleReceipts = receipts.filter((r) => r.status === "COLLECTED");

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Bank Reconciliation Confirmation</h1>
          <p className="mt-1 text-sm text-slate-500">
            Select collected receipts and confirm the total cash deposited.
          </p>
        </div>
        <button onClick={loadData} disabled={loading || busy} className="flex items-center gap-2 rounded-xl border px-4 py-2 text-sm disabled:opacity-50">
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {error && <div className="flex gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"><AlertCircle size={18} />{error}</div>}
      {success && <div className="flex gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"><CheckCircle size={18} />{success}</div>}

      {canSubmit && (
        <section className="rounded-2xl border bg-white p-5">
          <h2 className="text-lg font-semibold">Confirm Cash Deposited</h2>
          <p className="mt-1 text-sm text-slate-500">Select collected receipts included in this deposit. The expected total is calculated by the backend.</p>
          {loading ? <p className="py-6 text-sm text-slate-500">Loading receipts...</p> : (
            <div className="mt-4 space-y-3">
              {eligibleReceipts.map((receipt) => (
                <label key={receipt.id} className="flex flex-wrap items-center gap-3 rounded-xl border p-3">
                  <input type="checkbox" checked={selected.includes(receipt.id)} onChange={(e) => setSelected((old) => e.target.checked ? [...old, receipt.id] : old.filter((id) => id !== receipt.id))} />
                  <span className="flex-1 text-sm font-medium">{receipt.receipt_number || `Receipt #${receipt.id}`} · {receipt.customer_name || "Customer"}</span>
                  <span className="text-sm font-semibold">{money(receipt.amount)}</span>
                </label>
              ))}
              {!eligibleReceipts.length && <p className="text-sm text-slate-500">No collected receipts available for reconciliation.</p>}
              <div className="flex flex-wrap items-center justify-between gap-3 border-t pt-3">
                <p className="text-sm text-slate-600">Selected total: <strong>{money(eligibleReceipts.filter((r) => selected.includes(r.id)).reduce((sum, r) => sum + Number(r.amount || 0), 0))}</strong></p>
                <button onClick={submitCash} disabled={busy || !selected.length} className="rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">
                  {busy ? "Processing..." : "Confirm Deposit"}
                </button>
              </div>
            </div>
          )}
        </section>
      )}

      <section className="rounded-2xl border bg-white p-5">
        <h2 className="text-lg font-semibold">Reconciliation Register</h2>
        {loading ? <p className="py-6 text-sm text-slate-500">Loading records...</p> : (
          <div className="mt-4 space-y-4">
            {submissions.map((s) => (
              <div key={s.id} className="space-y-3 rounded-xl border p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-semibold">{s.submission_reference || s.reference}</p>
                    <p className="text-xs text-slate-500">Submitted by: {s.agent_username || s.agent} · Branch: {s.branch_name || s.branch}</p>
                  </div>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium">{s.status}</span>
                </div>
                <div className="grid gap-3 text-sm sm:grid-cols-3">
                  <p>Expected: <strong>{money(s.expected_amount)}</strong></p>
                  <p>Confirmed deposited: <strong>{s.actual_amount == null ? "—" : money(s.actual_amount)}</strong></p>
                  <p>Difference: <strong>{s.discrepancy_amount == null ? "—" : money(s.discrepancy_amount)}</strong></p>
                </div>
                {canVerify && s.status === "PENDING" && (
                  <>
                    <input type="number" min="0" step="0.01" placeholder="Confirm deposited amount (₹)" value={actualAmounts[s.id] || ""} onChange={(e) => setActualAmounts((old) => ({ ...old, [s.id]: e.target.value }))} className="w-full rounded-xl border px-3 py-2 text-sm" />
                    <input placeholder="Notes (optional)" value={notes[s.id] || ""} onChange={(e) => setNotes((old) => ({ ...old, [s.id]: e.target.value }))} className="w-full rounded-xl border px-3 py-2 text-sm" />
                    <div className="flex flex-wrap gap-2">
                      <button disabled={busy} onClick={() => verify(s, "approve")} className="flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white disabled:opacity-50"><CheckCircle size={15} /> Confirm Amount</button>
                      <button disabled={busy} onClick={() => verify(s, "reject")} className="flex items-center gap-2 rounded-lg bg-red-600 px-3 py-2 text-sm text-white disabled:opacity-50"><XCircle size={15} /> Reject</button>
                    </div>
                  </>
                )}
              </div>
            ))}
            {!submissions.length && <p className="text-sm text-slate-500">No reconciliation records yet.</p>}
          </div>
        )}
      </section>
    </div>
  );
}
