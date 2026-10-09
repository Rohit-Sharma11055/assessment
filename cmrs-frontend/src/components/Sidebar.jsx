import {
  LayoutDashboard,
  Users,
  Wallet,
  ReceiptText,
  ArrowLeftRight,
  Landmark,
  ChartNoAxesCombined,
  Settings,
  ShieldCheck,
} from "lucide-react";

const navigation = [
  { label: "Overview", icon: LayoutDashboard, roles: ["all"] },
  {
    label: "Customers",
    icon: Users,
    roles: ["all"],
  },
  {
    label: "Loans",
    icon: Wallet,
    roles: ["all"],
  },
  {
    label: "Collections",
    icon: ReceiptText,
    roles: ["Collection Agent", "Administrator"],
  },
  {
    label: "Reconciliation",
    icon: ArrowLeftRight,
    roles: ["Collection Agent", "Branch Manager", "Administrator"],
  },
  {
    label: "Treasury",
    icon: Landmark,
    roles: ["Finance/Treasury", "Administrator"],
  },
  { label: "Reports", icon: ChartNoAxesCombined, roles: ["all"] },
];

export default function Sidebar({
  role,
  activePage,
  setActivePage,
  mobileMenu,
  setMobileMenu,
}) {
  const visibleNavigation = navigation.filter(
    (item) => item.roles.includes("all") || item.roles.includes(role)
  );

  const openPage = (page) => {
    setActivePage(page);
    setMobileMenu(false);
  };

  return (
    <>
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col
        border-r border-slate-200 bg-white transition-transform
        md:translate-x-0 ${
          mobileMenu ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-20 items-center gap-3 border-b border-slate-100 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-700 text-white">
            <Landmark size={23} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">CMRS</h1>
            <p className="text-xs text-slate-500">Cash management</p>
          </div>
        </div>

        <div className="px-4 pt-7">
          <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
            Workspace
          </p>

          <nav className="space-y-1">
            {visibleNavigation.map(({ label, icon: Icon }) => (
              <button
                key={label}
                onClick={() => openPage(label)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  activePage === label
                    ? "bg-blue-700 text-white shadow-md shadow-blue-900/10"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                <Icon size={19} />
                {label}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-auto p-4">
          <div className="rounded-2xl bg-slate-900 p-4 text-white">
            <div className="mb-3 flex items-center gap-2 text-blue-300">
              <ShieldCheck size={19} />
              <span className="text-sm font-semibold">
                Secure workspace
              </span>
            </div>
            <p className="text-xs leading-5 text-slate-300">
              Role-based access and auditable financial workflows.
            </p>
          </div>

          <button
            onClick={() => openPage("Settings")}
            className={`mt-3 flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm ${
              activePage === "Settings"
                ? "bg-blue-700 text-white"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            <Settings size={19} />
            Settings
          </button>
        </div>
      </aside>

      {mobileMenu && (
        <button
          aria-label="Close navigation"
          onClick={() => setMobileMenu(false)}
          className="fixed inset-0 z-20 bg-slate-950/30 md:hidden"
        />
      )}
    </>
  );
}
