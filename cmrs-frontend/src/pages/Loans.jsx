
import { useEffect, useState } from "react";
import { Wallet, RefreshCw, Search } from "lucide-react";
import api from "../api/client";

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadLoans() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("loans/");
      setLoans(
        Array.isArray(response.data)
          ? response.data
          : response.data.results || []
      );
    } catch (err) {
      setError(
        err.response?.data?.detail || "Unable to load loans."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLoans();
  }, []);

  const filtered = loans.filter((loan) =>
    `${loan.loan_number} ${loan.customer_name}`
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const totalPrincipal = loans.reduce(
    (sum, loan) => sum + Number(loan.principal_amount),
    0
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Loans</h2>
        <p className="mt-1 text-sm text-slate-500">
          Loan portfolio retrieved from your database.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-blue-50 p-3 text-blue-700">
              <Wallet size={21} />
            </div>
            <div>
              <p className="text-sm text-slate-500">Total loans</p>
              <p className="text-2xl font-bold">{loans.length}</p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5">
          <p className="text-sm text-slate-500">Original principal</p>
          <p className="mt-2 text-2xl font-bold">
            ₹{totalPrincipal.toLocaleString("en-IN", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-4">
          <div className="flex min-w-48 flex-1 items-center gap-2 rounded-xl border border-slate-200 px-3">
            <Search size={17} className="text-slate-400" />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search loan or customer..."
              className="w-full py-3 text-sm outline-none"
            />
          </div>
          <button
            onClick={loadLoans}
            className="flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm hover:bg-slate-50"
          >
            <RefreshCw size={16} /> Refresh
          </button>
        </div>

        {loading ? (
          <p className="p-8 text-center text-sm text-slate-500">
            Loading loans...
          </p>
        ) : error ? (
          <div className="p-8 text-center text-sm text-red-600">
            {error}
            <button
              onClick={loadLoans}
              className="ml-2 font-semibold text-blue-700"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-4">Loan number</th>
                  <th className="px-5 py-4">Customer</th>
                  <th className="px-5 py-4">Principal</th>
                  <th className="px-5 py-4">Rate</th>
                  <th className="px-5 py-4">Tenure</th>
                  <th className="px-5 py-4">Scheduled total</th>
                  <th className="px-5 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((loan) => (
                  <tr key={loan.id} className="hover:bg-slate-50">
                    <td className="px-5 py-4 font-semibold text-blue-700">
                      {loan.loan_number}
                    </td>
                    <td className="px-5 py-4">{loan.customer_name}</td>
                    <td className="px-5 py-4">
                      ₹{Number(loan.principal_amount).toLocaleString("en-IN")}
                    </td>
                    <td className="px-5 py-4">
                      {loan.annual_interest_rate}%
                    </td>
                    <td className="px-5 py-4">
                      {loan.tenure_months} months
                    </td>
                    <td className="px-5 py-4 font-medium">
                      ₹{Number(loan.total_scheduled).toLocaleString("en-IN")}
                    </td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                        {loan.status}
                      </span>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-5 py-10 text-center text-slate-500">
                      No loans found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
