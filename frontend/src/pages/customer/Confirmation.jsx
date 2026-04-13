import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { trackOrder } from "../../api";
import { CheckCircle } from "lucide-react";

export default function CustomerConfirmation() {
  const { qrToken, orderId } = useParams();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    trackOrder(qrToken, orderId).then(({ data }) => setOrder(data));
  }, [qrToken, orderId]);

  if (!order) return null;

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-sm text-center">
        <CheckCircle size={48} className="text-green-500 mx-auto mb-3" />
        <h1 className="text-xl font-bold text-gray-800 mb-1">Order Placed!</h1>
        <p className="text-sm text-gray-500 mb-4">Your order #{order.id} has been sent to the kitchen.</p>

        <div className="bg-gray-50 rounded-xl p-3 mb-4 text-left">
          <ul className="text-sm text-gray-700 space-y-1">
            {order.items.map((item) => (
              <li key={item.id}>{item.quantity}× {item.menu_item_name}</li>
            ))}
          </ul>
          <div className="border-t mt-2 pt-2 flex justify-between font-semibold text-sm">
            <span>Total</span>
            <span>₹{order.total_amount}</span>
          </div>
        </div>

        <div className="flex gap-2">
          <Link to={`/t/${qrToken}/menu`}
            className="flex-1 bg-orange-500 hover:bg-orange-600 text-white text-sm font-semibold py-2.5 rounded-xl">
            Back to Menu
          </Link>
          <Link to={`/t/${qrToken}/track/${order.id}`}
            className="flex-1 border text-sm font-semibold py-2.5 rounded-xl hover:bg-gray-50">
            Track Order
          </Link>
        </div>
      </div>
    </div>
  );
}
