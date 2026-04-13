import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getOrders, markPaid } from "../../api";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-600",
  preparing: "bg-orange-100 text-orange-700",
  ready: "bg-green-100 text-green-700",
  served: "bg-gray-100 text-gray-500",
  cancelled: "bg-red-100 text-red-600",
};

const STATUSES = ["", "pending", "confirmed", "preparing", "ready", "served", "cancelled"];
const PAYMENTS = ["", "unpaid", "paid"];

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [payFilter, setPayFilter] = useState("");

  const load = () =>
    getOrders({ status: statusFilter, payment: payFilter }).then(({ data }) =>
      setOrders(data)
    );

  useEffect(() => { load(); }, [statusFilter, payFilter]);

  const handleMarkPaid = async (id) => {
    try {
      await markPaid(id);
      toast.success("Marked as paid.");
      load();
    } catch { toast.error("Failed."); }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold">Orders</h2>
        <div className="flex gap-2">
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400">
            {STATUSES.map((s) => (
              <option key={s} value={s}>{s || "All statuses"}</option>
            ))}
          </select>
          <select value={payFilter} onChange={(e) => setPayFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400">
            {PAYMENTS.map((p) => (
              <option key={p} value={p}>{p || "All payments"}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-medium">Order</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-medium">Table</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-medium">Customer</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-medium">Status</th>
              <th className="text-left px-4 py-3 text-xs text-gray-500 font-medium">Payment</th>
              <th className="text-right px-4 py-3 text-xs text-gray-500 font-medium">Amount</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {orders.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-400">No orders found.</td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">#{o.id}</td>
                  <td className="px-4 py-3 text-gray-600">{o.table_name}</td>
                  <td className="px-4 py-3 text-gray-600">
                    <div>{o.customer_name || "—"}</div>
                    {o.session_phone && (
                      <div className="text-xs text-gray-400">{o.session_phone}</div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[o.status] || ""}`}>
                      {o.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      o.payment_status === "paid" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                    }`}>
                      {o.payment_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-medium">₹{o.total_amount}</td>
                  <td className="px-4 py-3">
                    {o.payment_status === "unpaid" && (
                      <button onClick={() => handleMarkPaid(o.id)}
                        className="text-xs bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded-lg whitespace-nowrap">
                        Mark Paid
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
