import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { trackOrder } from "../../api";

const STATUS_STEPS = ["pending", "confirmed", "preparing", "ready", "served"];

const STEP_LABELS = {
  pending: "Order Received",
  confirmed: "Confirmed",
  preparing: "Being Prepared",
  ready: "Ready for Pickup",
  served: "Served",
};

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-600",
  preparing: "bg-orange-100 text-orange-700",
  ready: "bg-green-100 text-green-700",
  served: "bg-gray-100 text-gray-500",
  cancelled: "bg-red-100 text-red-600",
};

export default function CustomerTrack() {
  const { qrToken, orderId } = useParams();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    const fetch = () => trackOrder(qrToken, orderId).then(({ data }) => setOrder(data));
    fetch();
    const interval = setInterval(fetch, 5000);
    return () => clearInterval(interval);
  }, [qrToken, orderId]);

  if (!order) return <div className="min-h-screen bg-gray-50 flex items-center justify-center text-sm text-gray-400">Loading…</div>;

  const currentStep = STATUS_STEPS.indexOf(order.status);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-sm">
        <h1 className="font-bold text-gray-800 text-lg mb-1">Order #{order.id}</h1>
        <p className="text-sm text-gray-500 mb-4">
          {new Date(order.created_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
        </p>

        {order.status === "cancelled" ? (
          <div className="bg-red-50 text-red-600 rounded-xl p-4 text-center font-medium mb-4">
            Order Cancelled
          </div>
        ) : (
          <div className="space-y-2 mb-4">
            {STATUS_STEPS.map((s, i) => (
              <div key={s} className={`flex items-center gap-3 ${i > currentStep ? "opacity-40" : ""}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  i < currentStep ? "bg-green-500 text-white" :
                  i === currentStep ? "bg-orange-500 text-white" :
                  "bg-gray-100 text-gray-400"
                }`}>
                  {i < currentStep ? "✓" : i + 1}
                </div>
                <span className={`text-sm ${i === currentStep ? "font-semibold text-gray-800" : "text-gray-500"}`}>
                  {STEP_LABELS[s]}
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="bg-gray-50 rounded-xl p-3 mb-4">
          <ul className="text-sm text-gray-700 space-y-1">
            {order.items.map((item) => (
              <li key={item.id}>{item.quantity}× {item.menu_item_name}</li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-gray-400 text-center mb-4">Refreshes every 5 seconds</p>

        <Link to={`/t/${qrToken}/menu`}
          className="block w-full bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold py-2.5 rounded-xl text-center">
          Back to Menu
        </Link>
      </div>
    </div>
  );
}
