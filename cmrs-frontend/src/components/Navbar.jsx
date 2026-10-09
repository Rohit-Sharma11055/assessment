import {
  Menu,
  Search,
  Bell,
  ChevronDown,
} from "lucide-react";

export default function Navbar({
  activePage,
  mobileMenu,
  setMobileMenu,
  search,
  setSearch,
  showNotifications,
  setShowNotifications,
  setActivePage,
  role,
  userName,
}) {
  return (
    <header className="sticky top-0 z-10 flex h-20 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-8">
      <div className="flex items-center gap-3">
        <button
          onClick={() => setMobileMenu(!mobileMenu)}
          className="rounded-lg p-2 hover:bg-slate-100 md:hidden"
          aria-label="Toggle navigation"
        >
          <Menu size={21} />
        </button>

        <div>
          <p className="text-xs text-slate-500">
            Workspace / {activePage}
          </p>
          <h2 className="text-lg font-bold sm:text-xl">{activePage}</h2>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <div className="hidden items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 lg:flex">
          <Search size={17} className="text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search receipts..."
            className="w-36 bg-transparent text-sm outline-none placeholder:text-slate-400"
          />
        </div>

        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative rounded-xl border border-slate-200 p-2.5 hover:bg-slate-50"
            aria-label="Notifications"
          >
            <Bell size={19} />
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 w-64 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
              <p className="font-semibold">Notifications</p>
              <p className="mt-2 text-sm text-slate-500">
                Check your workspace for pending items.
              </p>

              {(role === "Branch Manager" ||
                role === "Administrator") && (
                <button
                  onClick={() => {
                    setActivePage("Reconciliation");
                    setShowNotifications(false);
                  }}
                  className="mt-3 text-sm font-semibold text-blue-700"
                >
                  Review submissions
                </button>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 rounded-xl p-1.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-800">
                {(userName || "User").slice(0, 2).toUpperCase()}
            </div>

            <div className="hidden text-left sm:block">
                <p className="text-sm font-semibold">{userName || "User"}</p>
                <p className="text-xs text-slate-500">{role || "Loading role..."}</p>
            </div>

            <ChevronDown size={16} className="hidden text-slate-400 sm:block" />
        </div>
      </div>
    </header>
  );
}
