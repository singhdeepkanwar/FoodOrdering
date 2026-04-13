import { useEffect, useState } from "react";
import { getDashboard } from "../../api";
import { ClipboardList, QrCode, UtensilsCrossed, Clock } from "lucide-react";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-600",
  preparing: "bg-orange-100 text-orange-700",
  ready: "bg-green-100 text-green-700",
  served: "bg-gray-100 text-gray-500",
  cancelled: "bg-red-100 text-red-600",
};

export default function DashboardHome() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getDashboard().then(({ data }) => setData(data));
  }, []);

  if (!data) return <div className="p-6 text-sm text-gray-400">Loading…</div>;

  const stats = [
    { label: "Pending Orders", value: data.pending_orders, icon: Clock, color: "text-yellow-600" },
    { label: "Active Tables", value: data.total_tables, icon: QrCode, color: "text-blue-600" },
    { label: "Menu Items", value: data.total_items, icon: UtensilsCrossed, color: "text-green-600" },
  ];

  return (
    <div className="p-6">
      <h2 className="text-lg font-semibold mb-5">Dashboard</h2>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl p-4 shadow-sm flex items-center gap-4">
            <div className={`${color} bg-gray-50 p-3 rounded-lg`}>
              <Icon size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-800">{value}</p>
              <p className="text-xs text-gray-500">{label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm p-4">
        <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
          <ClipboardList size={16} /> Recent Orders
        </h3>
        {data.recent_orders.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-6">No orders yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b">
                <th className="text-left py-2">Order</th>
                <th className="text-left py-2">Table</th>
                <th className="text-left py-2">Customer</th>
                <th className="text-left py-2">Status</th>
                <th className="text-right py-2">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_orders.map((o) => (
                <tr key={o.id} className="border-b last:border-0">
                  <td className="py-2 font-medium">#{o.id}</td>
                  <td className="py-2 text-gray-600">{o.table_name}</td>
                  <td className="py-2 text-gray-600">{o.customer_name || "—"}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[o.status] || ""}`}>
                      {o.status}
                    </span>
                  </td>
                  <td className="py-2 text-right font-medium">₹{o.total_amount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
