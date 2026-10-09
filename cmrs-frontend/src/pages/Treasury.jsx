import { useEffect, useState } from "react";
import api from "../api/client";
import { RefreshCw, Landmark, CheckCircle, AlertCircle } from "lucide-react";

export default function Treasury() {
  const [deposits, setDeposits] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [form, setForm] = useState({
    branch: "",
    bank_name: "",
    bank_account_reference: "",
    deposited_amount: "",
    deposit_date: new Date().toISOString().slice(0, 10),
    notes: "",
  });

  const [settlement, setSettlement] = useState({
    deposit_id: "",
    credited_amount: "",
    bank_reference_number: "",
    settlement_date: new Date().toISOString().slice(0, 10),
    notes: "",
  });

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      const [depositResponse, branchResponse] = await Promise.all([
        api.get("treasury/"),
        api.get("branches/"),
      ]);
      setDeposits(depositResponse.data.results || depositResponse.data);
      setBranches(branchResponse.data.results || branchResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        "Could not load treasury data. Check the branches API and your role."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const updateForm = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const updateSettlement = (e) =>
    setSettlement({ ...settlement, [e.target.name]: e.target.value });

  const createDeposit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const { data } = await api.post("treasury/", form);
      setSuccess(`Deposit ${data.deposit_reference} created.`);
      setForm({
        branch: "",
        bank_name: "",
        bank_account_reference: "",
        deposited_amount: "",
        deposit_date: new Date().toISOString().slice(0, 10),
        notes: "",
      });
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        "Could not create deposit."
      );
    } finally {
      setBusy(false);
    }
  };

  const recordSettlement = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      const { deposit_id, ...payload } = settlement;
      const { data } = await api.post(
        `treasury/${deposit_id}/settlements/`,
        payload
      );
      setSuccess(
        `Settlement recorded. Outstanding: ₹${Number(data.outstanding_amount).toLocaleString("en-IN")}`
      );
      setSettlement({
        ...settlement,
        credited_amount: "",
        bank_reference_number: "",
        notes: "",
      });
      await loadData();
    } catch (err) {
      setError(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        "Could not record settlement."
      );
    } finally {
      setBusy(false);
    }
  };

  const money = (value) =>
    `₹${Number(value || 0).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Treasury & Settlement</h1>
          <p className="mt-1 text-sm text-slate-500">
            Track branch deposits and bank settlement credits.
          </p>
        </div>
        <button onClick={loadData} className="flex items-center gap-2 rounded-xl border px-4 py-2 text-sm">
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {error && (
        <div className="flex gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle size={18} /> {error}
        </div>
      )}
      {success && (
        <div className="flex gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          <CheckCircle size={18} /> {success}
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-3">
        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">Total Deposits</p>
          <p className="mt-2 text-2xl font-bold">{deposits.length}</p>
        </div>
        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">Deposited Amount</p>
          <p className="mt-2 text-2xl font-bold">
            {money(deposits.reduce((sum, d) => sum + Number(d.deposited_amount), 0))}
          </p>
        </div>
        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">Outstanding Settlement</p>
          <p className="mt-2 text-2xl font-bold text-amber-600">
            {money(deposits.reduce((sum, d) => sum + Number(d.outstanding_amount ?? d.deposited_amount), 0))}
          </p>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <form onSubmit={createDeposit} className="space-y-4 rounded-2xl border bg-white p-5">
          <div className="flex items-center gap-2">
            <Landmark size={20} className="text-indigo-600" />
            <h2 className="text-lg font-semibold">Create Bank Deposit</h2>
          </div>

          <label className="block text-sm">
            Branch
            <select name="branch" value={form.branch} onChange={updateForm} required className="mt-1 w-full rounded-xl border p-3">
              <option value="">Select branch</option>
              {branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            Bank Name
            <input name="bank_name" value={form.bank_name} onChange={updateForm} required className="mt-1 w-full rounded-xl border p-3" placeholder="e.g. State Bank of India" />
          </label>

          <label className="block text-sm">
            Bank Account Reference
            <input name="bank_account_reference" value={form.bank_account_reference} onChange={updateForm} required className="mt-1 w-full rounded-xl border p-3" placeholder="Account reference (avoid full account number)" />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm">
              Amount (₹)
              <input type="number" name="deposited_amount" min="0.01" step="0.01" value={form.deposited_amount} onChange={updateForm} required className="mt-1 w-full rounded-xl border p-3" />
            </label>
            <label className="block text-sm">
              Deposit Date
              <input type="date" name="deposit_date" value={form.deposit_date} onChange={updateForm} required className="mt-1 w-full rounded-xl border p-3" />
            </label>
          </div>

          <label className="block text-sm">
            Notes
            <input name="notes" value={form.notes} onChange={updateForm} className="mt-1 w-full rounded-xl border p-3" />
          </label>

          <button disabled={busy || loading || !branches.length} className="w-full rounded-xl bg-indigo-600 p-3 font-semibold text-white disabled:opacity-50">
            {busy ? "Processing..." : "Create Deposit"}
          </button>
        </form>

        <form onSubmit={recordSettlement} className="space-y-4 rounded-2xl border bg-white p-5">
          <h2 className="text-lg font-semibold">Record Settlement Credit</h2>

          <label className="block text-sm">
            Deposit
            <select name="deposit_id" value={settlement.deposit_id} onChange={updateSettlement} required className="mt-1 w-full rounded-xl border p-3">
              <option value="">Select pending deposit</option>
              {deposits.filter((d) => Number(d.outstanding_amount ?? d.deposited_amount) > 0).map((d) => (
                <option key={d.id} value={d.id}>
                  {d.deposit_reference} — outstanding {money(d.outstanding_amount ?? d.deposited_amount)}
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            Credit Amount (₹)
            <input type="number" name="credited_amount" min="0.01" step="0.01" value={settlement.credited_amount} onChange={updateSettlement} required className="mt-1 w-full rounded-xl border p-3" />
          </label>

          <label className="block text-sm">
            Bank Reference Number
            <input name="bank_reference_number" value={settlement.bank_reference_number} onChange={updateSettlement} required className="mt-1 w-full rounded-xl border p-3" />
          </label>

          <label className="block text-sm">
            Settlement Date
            <input type="date" name="settlement_date" value={settlement.settlement_date} onChange={updateSettlement} required className="mt-1 w-full rounded-xl border p-3" />
          </label>

          <label className="block text-sm">
            Notes
            <input name="notes" value={settlement.notes} onChange={updateSettlement} className="mt-1 w-full rounded-xl border p-3" />
          </label>

          <button disabled={busy || loading || !deposits.some((d) => Number(d.outstanding_amount ?? d.deposited_amount) > 0)} className="w-full rounded-xl bg-emerald-600 p-3 font-semibold text-white disabled:opacity-50">
            {busy ? "Processing..." : "Record Settlement"}
          </button>
        </form>
      </div>

      <section className="overflow-x-auto rounded-2xl border bg-white p-5">
        <h2 className="text-lg font-semibold">Deposit Register</h2>
        {loading ? <p className="py-6 text-sm text-slate-500">Loading deposits...</p> : (
          <table className="mt-4 w-full min-w-[800px] text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                {["Reference", "Branch", "Bank", "Deposited", "Credited", "Outstanding", "Status"].map((heading) => (
                  <th key={heading} className="px-3 py-3 font-medium">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {deposits.map((d) => (
                <tr key={d.id} className="border-t">
                  <td className="px-3 py-3 font-medium">{d.deposit_reference}</td>
                  <td className="px-3 py-3">{d.branch_name || d.branch}</td>
                  <td className="px-3 py-3">{d.bank_name}</td>
                  <td className="px-3 py-3">{money(d.deposited_amount)}</td>
                  <td className="px-3 py-3">{money(d.total_credited)}</td>
                  <td className="px-3 py-3">{money(d.outstanding_amount)}</td>
                  <td className="px-3 py-3">{d.status}</td>
                </tr>
              ))}
              {deposits.length === 0 && (
                <tr><td colSpan="7" className="px-3 py-6 text-center text-slate-500">No deposits recorded yet.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
