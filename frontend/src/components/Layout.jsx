import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  LayoutDashboard,
  UtensilsCrossed,
  QrCode,
  ClipboardList,
  BarChart3,
  CreditCard,
  ChefHat,
  Users,
  LogOut,
} from "lucide-react";

const navItems = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/menu", icon: UtensilsCrossed, label: "Menu" },
  { to: "/tables", icon: QrCode, label: "Tables & QR" },
  { to: "/orders", icon: ClipboardList, label: "Orders" },
  { to: "/analytics", icon: BarChart3, label: "Analytics" },
  { to: "/billing", icon: CreditCard, label: "Billing" },
];

const staffLinks = [
  { to: "/kitchen", icon: ChefHat, label: "Kitchen Board" },
  { to: "/waiter", icon: Users, label: "Waiter View" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <aside className="w-64 bg-white shadow-md flex flex-col">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-orange-600">TableOrder</h1>
          {user?.restaurant && (
            <p className="text-xs text-gray-500 mt-1 truncate">
              {user.restaurant_name || `Restaurant #${user.restaurant}`}
            </p>
          )}
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-orange-100 text-orange-700"
                    : "text-gray-700 hover:bg-orange-50"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}

          <div className="border-t my-2" />

          {staffLinks.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className="flex items-center gap-2 px-3 py-2 rounded text-sm font-medium text-gray-500 hover:bg-orange-50 transition-colors"
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t">
          <p className="text-xs text-gray-500 mb-2 truncate">
            {user?.first_name || user?.username}
          </p>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-red-600 transition-colors"
          >
            <LogOut size={14} />
            Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
