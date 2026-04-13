import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import { getKitchenOrders, advanceOrder, cancelOrder } from "../../api";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { LogOut } from "lucide-react";

const COLUMNS = [
  { key: "pending", label: "Pending", nextLabel: "Confirm", bg: "bg-yellow-50", header: "bg-yellow-100 text-yellow-800" },
  { key: "confirmed", label: "Confirmed", nextLabel: "Start Cooking", bg: "bg-blue-50", header: "bg-blue-100 text-blue-800" },
  { key: "preparing", label: "Preparing", nextLabel: "Mark Ready", bg: "bg-orange-50", header: "bg-orange-100 text-orange-800" },
  { key: "ready", label: "Ready", nextLabel: null, bg: "bg-green-50", header: "bg-green-100 text-green-800" },
];

function OrderCard({ order, onAdvance, onCancel }) {
  return (
    <div className="bg-white rounded-xl p-3 shadow-sm mb-2">
      <div className="flex justify-between items-start mb-2">
        <div>
          <span className="font-bold text-gray-800">#{order.id}</span>
          <span className="text-xs text-gray-500 ml-2">{order.table_name}</span>
        </div>
        <span className="text-xs text-gray-400">
          {new Date(order.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>
      <ul className="text-sm text-gray-700 space-y-0.5 mb-2">
        {order.items.map((item) => (
          <li key={item.id}>{item.quantity}× {item.menu_item_name}</li>
        ))}
      </ul>
      {order.special_instructions && (
        <p className="text-xs text-orange-700 bg-orange-50 rounded px-2 py-1 mb-2">
          {order.special_instructions}
        </p>
      )}
      <div className="flex gap-2">
        {onAdvance && (
          <button onClick={() => onAdvance(order.id)}
            className="flex-1 bg-orange-500 hover:bg-orange-600 text-white text-xs font-semibold py-1.5 rounded-lg">
            {COLUMNS.find((c) => c.key === order.status)?.nextLabel || "Advance"}
          </button>
        )}
        {order.status === "ready" && (
          <div className="flex-1 bg-green-100 text-green-700 text-xs font-semibold py-1.5 rounded-lg text-center">
            Ready for pickup ✓
          </div>
        )}
        <button onClick={() => onCancel(order.id)}
          className="text-xs px-2 py-1.5 border border-red-200 text-red-500 hover:bg-red-50 rounded-lg">
          Cancel
        </button>
      </div>
    </div>
  );
}

export default function KitchenBoard() {
  const [columns, setColumns] = useState({});
  const { logout } = useAuth();
  const navigate = useNavigate();

  const load = useCallback(() => {
    getKitchenOrders().then(({ data }) => setColumns(data.columns));
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [load]);

  const handleAdvance = async (id) => {
    try { await advanceOrder(id); load(); }
    catch { toast.error("Failed to advance order."); }
  };

  const handleCancel = async (id) => {
    if (!confirm("Cancel this order?")) return;
    try { await cancelOrder(id); load(); }
    catch { toast.error("Failed to cancel."); }
  };

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between sticky top-0 z-10">
        <h1 className="font-bold text-orange-600 text-lg">Kitchen Board</h1>
        <div className="flex items-center gap-4">
          <span className="text-xs text-gray-400">Auto-refreshes every 5s</span>
          <button onClick={handleLogout} className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600">
            <LogOut size={14} /> Logout
          </button>
        </div>
      </header>

      <div className="p-4 grid grid-cols-4 gap-4">
        {COLUMNS.map((col) => {
          const orders = columns[col.key] || [];
          return (
            <div key={col.key} className={`${col.bg} rounded-xl p-3`}>
              <div className={`${col.header} rounded-lg px-3 py-2 mb-3 flex justify-between items-center`}>
                <span className="font-semibold text-sm">{col.label}</span>
                <span className="text-xs font-bold">{orders.length}</span>
              </div>
              {orders.length === 0 ? (
                <p className="text-xs text-gray-400 text-center py-4">No orders</p>
              ) : (
                orders.map((o) => (
                  <OrderCard
                    key={o.id}
                    order={o}
                    onAdvance={col.nextLabel ? handleAdvance : null}
                    onCancel={handleCancel}
                  />
                ))
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
