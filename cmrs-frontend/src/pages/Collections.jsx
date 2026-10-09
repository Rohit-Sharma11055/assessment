import { useEffect, useState } from "react";
import api from "../api/client";
import { RefreshCw, IndianRupee, CheckCircle, AlertCircle } from "lucide-react";

export default function Collections() {
  const [loans, setLoans] = useState([]);
  const [loanId, setLoanId] = useState("");
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [message, setMessage] = useState(null);

  const loadLoans = async () => {
    setFetching(true);
    try {
      const response = await api.get("loans/");
      setLoans(response.data.results || response.data);
    } catch {
      setMessage({ type: "error", text: "Could not load loans." });
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    loadLoans();
  }, []);

  const submitRepayment = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await api.post("repayments/", {
        loan_id: Number(loanId),
        amount: amount,
      });

      setMessage({
        type: "success",
        text: `Payment recorded! Receipt: ${response.data.receipt_number}`,
      });
      setAmount("");
    } catch (error) {
      const data = error.response?.data;
      const detail =
        data?.detail ||
        data?.amount?.[0] ||
        data?.loan_id?.[0] ||
        data?.error ||
        "Payment failed. Check loan assignment and amount.";
      setMessage({ type: "error", text: detail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Cash Collections</h1>
        <p className="mt-1 text-sm text-slate-500">
          Record customer repayments and generate unique receipts.
        </p>
      </div>

      {message && (
        <div className={`flex items-start gap-2 rounded-xl border p-4 text-sm ${
          message.type === "success"
            ? "border-emerald-200 bg-emerald-50 text-emerald-700"
            : "border-red-200 bg-red-50 text-red-700"
        }`}>
          {message.type === "success"
            ? <CheckCircle size={18} />
            : <AlertCircle size={18} />}
          <span>{message.text}</span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <form
          onSubmit={submitRepayment}
          className="space-y-5 rounded-2xl border border-slate-200 bg-white p-6 lg:col-span-2"
        >
          <h2 className="text-lg font-semibold text-slate-900">
            Record Repayment
          </h2>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Loan
            </label>
            <select
              value={loanId}
              onChange={(e) => setLoanId(e.target.value)}
              required
              className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-indigo-500"
            >
              <option value="">
                {fetching ? "Loading loans..." : "Select a loan"}
              </option>
              {loans.map((loan) => (
                <option key={loan.id} value={loan.id}>
                  {loan.loan_number} — {loan.customer_name} — ₹
                  {Number(loan.principal_amount).toLocaleString("en-IN")}
                </option>
              ))}
            </select>
            {!fetching && loans.length === 0 && (
              <p className="mt-2 text-xs text-amber-600">
                No accessible loans found. Ensure this agent is assigned to a customer with an active loan.
              </p>
            )}
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Collection Amount (₹)
            </label>
            <div className="flex items-center rounded-xl border border-slate-300 px-3 focus-within:border-indigo-500">
              <IndianRupee size={17} className="text-slate-400" />
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
                placeholder="Enter amount collected"
                className="w-full border-0 px-3 py-3 text-sm outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || fetching || !loans.length}
            className="w-full rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Recording..." : "Record Payment"}
          </button>

          <p className="text-xs text-slate-500">
            The server calculates repayment allocations and generates the receipt number.
          </p>
        </form>

        <div className="rounded-2xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Collection Workflow</h2>
          <div className="mt-5 space-y-5">
            {[
              ["01", "Select loan", "Choose an accessible customer's loan."],
              ["02", "Record payment", "Enter the amount actually received."],
              ["03", "Save receipt", "The backend records the payment and allocations."],
              ["04", "Submit cash", "Next, we'll connect branch reconciliation."],
            ].map(([number, title, description]) => (
              <div key={number} className="flex gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-xs font-bold text-indigo-600">
                  {number}
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-800">{title}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={loadLoans}
            type="button"
            className="mt-6 flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-800"
          >
            <RefreshCw size={15} /> Refresh loans
          </button>
        </div>
      </div>
    </div>
  );
}
