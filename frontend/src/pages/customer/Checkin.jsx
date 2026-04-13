import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { customerCheckin, getCustomerMenu } from "../../api";
import { useEffect } from "react";

export default function CustomerCheckin() {
  const { qrToken } = useParams();
  const navigate = useNavigate();
  const [restaurant, setRestaurant] = useState(null);
  const [table, setTable] = useState(null);
  const [form, setForm] = useState({ customer_name: "", customer_phone: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Check if already have a session
    const sid = localStorage.getItem(`session_${qrToken}`);
    if (sid) {
      navigate(`/t/${qrToken}/menu`, { replace: true });
      return;
    }
    getCustomerMenu(qrToken)
      .then(({ data }) => {
        setRestaurant(data.restaurant);
        setTable(data.table);
      })
      .catch(() => setError("Table not found or restaurant is closed."));
  }, [qrToken]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await customerCheckin(qrToken, form);
      localStorage.setItem(`session_${qrToken}`, data.session_id);
      navigate(`/t/${qrToken}/menu`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to check in.");
    } finally {
      setLoading(false);
    }
  };

  if (error && !restaurant) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl p-6 text-center max-w-sm shadow-sm">
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl p-8 w-full max-w-sm shadow-sm">
        {restaurant?.logo && (
          <img src={restaurant.logo} alt={restaurant.name} className="w-16 h-16 object-cover rounded-xl mb-3 mx-auto" />
        )}
        <h1 className="text-xl font-bold text-gray-800 text-center mb-1">
          {restaurant?.name || "Welcome"}
        </h1>
        {table && (
          <p className="text-sm text-gray-500 text-center mb-6">{table.name}</p>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
            <input
              required
              value={form.customer_name}
              onChange={(e) => setForm({ ...form, customer_name: e.target.value })}
              placeholder="e.g. Rahul"
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
            <input
              required
              type="tel"
              value={form.customer_phone}
              onChange={(e) => setForm({ ...form, customer_phone: e.target.value })}
              placeholder="10-digit mobile number"
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-2.5 rounded-lg text-sm transition-colors"
          >
            {loading ? "Please wait…" : "View Menu & Order"}
          </button>
        </form>

        <p className="text-xs text-gray-400 mt-4 text-center">
          Already ordered? Use the same phone number to reconnect.
        </p>
      </div>
    </div>
  );
}
