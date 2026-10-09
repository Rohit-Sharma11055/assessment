import { useEffect, useState } from "react";
import api from "./api/client";

import Login from "./pages/Login";
import Customers from "./pages/Customers";
import Loans from "./pages/Loans";
import Collections from "./pages/Collections";
import Reconciliation from "./pages/Reconciliation";
import Treasury from "./pages/Treasury";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";

import {
  Users,
  CreditCard,
  IndianRupee,
  Clock3,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Landmark,
  Plus,
  Download,
} from "lucide-react";

const allowedPages = {
  "Collection Agent": [
    "Overview",
    "Customers",
    "Loans",
    "Collections",
    "Reconciliation",
    "Reports",
    "Settings",
  ],
  "Branch Manager": [
    "Overview",
    "Customers",
    "Loans",
    "Reconciliation",
    "Reports",
    "Settings",
  ],
  "Finance/Treasury": [
    "Overview",
    "Customers",
    "Loans",
    "Treasury",
    "Reports",
    "Settings",
  ],
  Administrator: [
    "Overview",
    "Customers",
    "Loans",
    "Collections",
    "Reconciliation",
    "Treasury",
    "Reports",
    "Settings",
  ],
};

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [search, setSearch] = useState("");
  const [period, setPeriod] = useState("Today");
  const [showNotifications, setShowNotifications] = useState(false);

  const [authenticated, setAuthenticated] = useState(
    Boolean(sessionStorage.getItem("access_token"))
  );

  const [role, setRole] = useState(
    sessionStorage.getItem("user_role") || ""
  );

  const [userName, setUserName] = useState(
    sessionStorage.getItem("username") || ""
  );

  const [dashboardData, setDashboardData] = useState(null);
  const [recentReceipts, setRecentReceipts] = useState([]);

  const permittedPages = allowedPages[role] || [];

  useEffect(() => {
    if (!authenticated) return;

    api
      .get("reports/summary/")
      .then((response) => setDashboardData(response.data))
      .catch((error) => {
        console.error("Dashboard API error:", error.response?.data);
      });

    if (
      role === "Administrator" ||
      role === "Collection Agent"
    ) {
      api
        .get("repayments/receipts/")
        .then((response) => {
          setRecentReceipts(response.data.results || response.data);
        })
        .catch((error) => {
          console.error("Recent receipts error:", error.response?.data);
        });
    }
  }, [authenticated, role]);

  useEffect(() => {
    if (authenticated && !permittedPages.includes(activePage)) {
      setActivePage("Overview");
    }
  }, [activePage, role, authenticated]);

  const metrics = [
    {
      label: "Total Customers",
      value: dashboardData?.total_customers ?? "—",
      change: "Live database count",
      positive: true,
      icon: Users,
      color: "bg-blue-50 text-blue-700",
    },
    {
      label: "Active Loans",
      value: dashboardData?.active_loans ?? "—",
      change: `${dashboardData?.total_loans ?? 0} total loans`,
      positive: true,
      icon: CreditCard,
      color: "bg-violet-50 text-violet-700",
    },
    {
      label: "Total Collections",
      value: dashboardData
        ? `₹${Number(dashboardData.total_collected).toLocaleString("en-IN")}`
        : "—",
      change: `${dashboardData?.receipt_count ?? 0} receipts recorded`,
      positive: true,
      icon: IndianRupee,
      color: "bg-emerald-50 text-emerald-700",
    },
    {
      label: "Pending Reconciliations",
      value: dashboardData?.pending_reconciliations ?? "—",
      change: "Awaiting verification",
      positive: false,
      icon: Clock3,
      color: "bg-amber-50 text-amber-700",
    },
  ];

  const filteredCollections = recentReceipts
    .filter((receipt) => {
      const query = search.toLowerCase();

      return (
        (receipt.receipt_number || "").toLowerCase().includes(query) ||
        (receipt.customer_name || "").toLowerCase().includes(query) ||
        String(receipt.collected_by || "").toLowerCase().includes(query)
      );
    })
    .map((receipt) => ({
      receipt: receipt.receipt_number,
      customer: receipt.customer_name,
      agent: receipt.collected_by_username || receipt.collected_by || "—",
      amount: `₹${Number(receipt.amount).toLocaleString("en-IN")}`,
      status: receipt.status,
      color:
        receipt.status === "RECONCILED"
          ? "bg-emerald-50 text-emerald-700"
          : receipt.status === "SUBMITTED"
          ? "bg-amber-50 text-amber-700"
          : "bg-blue-50 text-blue-700",
    }));

  if (!authenticated) {
    return (
      <Login
        onLogin={() => {
          setRole(sessionStorage.getItem("user_role") || "");
          setAuthenticated(true);
        }}
      />
    );
  }

  const navigateTo = (page) => {
    if (permittedPages.includes(page)) {
      setActivePage(page);
      setMobileMenu(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Sidebar
        role={role}
        activePage={activePage}
        setActivePage={navigateTo}
        mobileMenu={mobileMenu}
        setMobileMenu={setMobileMenu}
      />

      <div className="min-h-screen md:ml-64">
        <Navbar
          activePage={activePage}
          mobileMenu={mobileMenu}
          setMobileMenu={setMobileMenu}
          search={search}
          setSearch={setSearch}
          showNotifications={showNotifications}
          setShowNotifications={setShowNotifications}
          setActivePage={navigateTo}
          role={role || "User"}
          userName={userName}
        />

        {activePage === "Customers" ? (
          <Customers />
        ) : activePage === "Loans" ? (
          <Loans />
        ) : activePage === "Collections" ? (
          <Collections />
        ) : activePage === "Reconciliation" ? (
          <Reconciliation />
        ) : activePage === "Treasury" ? (
          <Treasury />
        ) : activePage === "Reports" ? (
          <main className="p-8">
            <h3 className="text-xl font-bold">Reports</h3>
            <p className="mt-2 text-sm text-slate-500">
              Reporting dashboard.
            </p>
          </main>
        ) : activePage === "Settings" ? (
          <main className="p-8">
            <h3 className="text-xl font-bold">Settings</h3>
            <p className="mt-2 text-sm text-slate-500">
              Account and application settings.
            </p>
          </main>
        ) : (
          <main className="mx-auto max-w-[1600px] space-y-7 p-4 sm:p-8">
            <section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <h3 className="text-2xl font-bold tracking-tight">
                  Good morning, {role || "User"}
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  Here's what's happening with your cash operations.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <select
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                  className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium outline-none focus:border-blue-500"
                >
                  <option>Today</option>
                  <option>This week</option>
                  <option>This month</option>
                </select>

                {permittedPages.includes("Collections") && (
                  <button
                    onClick={() => navigateTo("Collections")}
                    className="flex items-center gap-2 rounded-xl bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-700/20 hover:bg-blue-800"
                  >
                    <Plus size={17} />
                    New collection
                  </button>
                )}
              </div>
            </section>

            <div className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
              Dashboard metrics are connected to live CMRS database records.
            </div>

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {metrics.map(
                ({ label, value, change, positive, icon: Icon, color }) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-sm font-medium text-slate-500">
                        {label}
                      </span>
                      <div className={`rounded-xl p-2.5 ${color}`}>
                        <Icon size={21} />
                      </div>
                    </div>

                    <p className="mt-5 text-2xl font-bold tracking-tight">
                      {value}
                    </p>

                    <div className="mt-2 flex items-center gap-1.5 text-xs">
                      {positive ? (
                        <ArrowUpRight
                          size={15}
                          className="text-emerald-600"
                        />
                      ) : (
                        <ArrowDownRight
                          size={15}
                          className="text-slate-500"
                        />
                      )}
                      <span
                        className={
                          positive
                            ? "font-semibold text-emerald-700"
                            : "text-slate-500"
                        }
                      >
                        {change}
                      </span>
                    </div>
                  </div>
                )
              )}
            </section>

            <section className="grid gap-6 xl:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-white p-6 xl:col-span-2">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h3 className="font-bold">Collection overview</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Illustrative daily collection performance
                    </p>
                  </div>

                  <button
                    onClick={() => navigateTo("Reports")}
                    className="text-sm font-semibold text-blue-700 hover:text-blue-900"
                  >
                    View reports
                  </button>
                </div>

                <div className="mt-8 grid grid-cols-2 gap-4">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-sm text-slate-500">
                      Expected collections
                    </p>
                    <p className="mt-2 text-xl font-bold">₹3,00,000</p>
                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full w-[83%] rounded-full bg-blue-600" />
                    </div>
                    <p className="mt-2 text-xs text-slate-500">
                      83% of target collected
                    </p>
                  </div>

                  <div className="rounded-xl bg-slate-50 p-4">
                    <p className="text-sm text-slate-500">
                      Outstanding amount
                    </p>
                    <p className="mt-2 text-xl font-bold">₹51,500</p>
                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full w-[17%] rounded-full bg-amber-500" />
                    </div>
                    <p className="mt-2 text-xs text-slate-500">
                      Remaining collection target
                    </p>
                  </div>
                </div>

                <div className="mt-8">
                  <div className="mb-4 flex items-center justify-between">
                    <h4 className="text-sm font-semibold">Cash lifecycle</h4>
                    <span className="text-xs text-slate-400">
                      Sample distribution
                    </span>
                  </div>

                  <div className="flex h-3 overflow-hidden rounded-full bg-slate-100">
                    <div className="w-[45%] bg-blue-600" />
                    <div className="w-[22%] bg-violet-500" />
                    <div className="w-[28%] bg-emerald-500" />
                    <div className="w-[5%] bg-amber-500" />
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
                    {[
                      ["Agent custody", "bg-blue-600", "₹32,500"],
                      ["Branch vault", "bg-violet-500", "₹76,000"],
                      ["Bank settled", "bg-emerald-500", "₹1,40,000"],
                      ["Discrepancies", "bg-amber-500", "₹500"],
                    ].map(([label, color, amount]) => (
                      <div key={label} className="flex items-start gap-2">
                        <span
                          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${color}`}
                        />
                        <div>
                          <p className="text-xs text-slate-500">{label}</p>
                          <p className="mt-1 font-semibold">{amount}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-6">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold">Needs attention</h3>
                  <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
                    {(dashboardData?.pending_reconciliations ?? 0) +
                      (dashboardData?.pending_deposits ?? 0)}{" "}
                    items
                  </span>
                </div>

                <div className="mt-5 space-y-4">
                  {permittedPages.includes("Reconciliation") && (
                    <div className="flex gap-3 rounded-xl border border-amber-100 bg-amber-50/60 p-3">
                      <Clock3
                        className="mt-0.5 shrink-0 text-amber-700"
                        size={19}
                      />
                      <div>
                        <p className="text-sm font-semibold">
                          Cash submissions pending
                        </p>
                        <p className="mt-1 text-xs leading-5 text-slate-600">
                          Review pending cash submissions.
                        </p>
                        <button
                          onClick={() => navigateTo("Reconciliation")}
                          className="mt-2 text-xs font-semibold text-blue-700"
                        >
                          Review batches →
                        </button>
                      </div>
                    </div>
                  )}

                  {permittedPages.includes("Treasury") && (
                    <div className="flex gap-3 rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                      <Landmark
                        className="mt-0.5 shrink-0 text-blue-700"
                        size={19}
                      />
                      <div>
                        <p className="text-sm font-semibold">
                          Deposits and settlements
                        </p>
                        <p className="mt-1 text-xs leading-5 text-slate-600">
                          Check pending bank settlements.
                        </p>
                        <button
                          onClick={() => navigateTo("Treasury")}
                          className="mt-2 text-xs font-semibold text-blue-700"
                        >
                          View treasury →
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-3 rounded-xl border border-red-100 bg-red-50/60 p-3">
                    <AlertTriangle
                      className="mt-0.5 shrink-0 text-red-700"
                      size={19}
                    />
                    <div>
                      <p className="text-sm font-semibold">
                        Financial monitoring
                      </p>
                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Review financial records and discrepancies within
                        your permitted workspace.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {(role === "Administrator" ||
              role === "Collection Agent") && (
              <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
                <div className="flex flex-col justify-between gap-3 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:px-6">
                  <div>
                    <h3 className="font-bold">Recent collections</h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Latest repayment receipts from the database
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <div className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 lg:hidden">
                      <input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search"
                        className="w-full min-w-0 text-sm outline-none"
                      />
                    </div>

                    <button
                      onClick={() => navigateTo("Collections")}
                      className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50"
                    >
                      <Download size={16} />
                      Collections
                    </button>
                  </div>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[700px] text-left text-sm">
                    <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                      <tr>
                        <th className="px-6 py-4 font-semibold">Receipt</th>
                        <th className="px-6 py-4 font-semibold">Customer</th>
                        <th className="px-6 py-4 font-semibold">Agent</th>
                        <th className="px-6 py-4 font-semibold">Amount</th>
                        <th className="px-6 py-4 font-semibold">Status</th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100">
                      {filteredCollections.map((item) => (
                        <tr
                          key={item.receipt}
                          className="transition hover:bg-slate-50"
                        >
                          <td className="px-6 py-4 font-semibold text-blue-700">
                            {item.receipt}
                          </td>
                          <td className="px-6 py-4 font-medium">
                            {item.customer}
                          </td>
                          <td className="px-6 py-4 text-slate-500">
                            {item.agent}
                          </td>
                          <td className="px-6 py-4 font-semibold">
                            {item.amount}
                          </td>
                          <td className="px-6 py-4">
                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${item.color}`}
                            >
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}

                      {filteredCollections.length === 0 && (
                        <tr>
                          <td
                            colSpan={5}
                            className="px-6 py-10 text-center text-slate-500"
                          >
                            No matching receipts.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

                <div className="border-t border-slate-100 px-6 py-4 text-xs text-slate-500">
                  Showing {filteredCollections.length} receipts · Period:{" "}
                  {period}
                </div>
              </section>
            )}

            <footer className="flex flex-col justify-between gap-2 pb-3 text-xs text-slate-400 sm:flex-row">
              <p>CMRS · Cash Management &amp; Reconciliation System</p>
              <p>Assessment prototype</p>
            </footer>
          </main>
        )}
      </div>
    </div>
  );
}

export default App;
