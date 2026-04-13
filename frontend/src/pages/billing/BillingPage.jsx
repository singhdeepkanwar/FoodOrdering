import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getBilling, changePlan } from "../../api";
import { CheckCircle } from "lucide-react";

const STATUS_COLORS = {
  trial: "bg-blue-100 text-blue-700",
  active: "bg-green-100 text-green-700",
  expired: "bg-red-100 text-red-600",
  cancelled: "bg-gray-100 text-gray-500",
};

export default function BillingPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState("");

  const load = () => getBilling().then(({ data }) => setData(data));
  useEffect(() => { load(); }, []);

  const handleChangePlan = async (planId) => {
    if (!confirm("Switch to this plan? An invoice will be created.")) return;
    setLoading(planId);
    try {
      await changePlan(planId);
      toast.success("Plan updated.");
      load();
    } catch { toast.error("Failed to change plan."); }
    finally { setLoading(""); }
  };

  if (!data) return <div className="p-6 text-sm text-gray-400">Loading…</div>;

  const { subscription, plans, invoices } = data;

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-lg font-semibold">Billing</h2>

      {/* Current subscription */}
      {subscription && (
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3">Current Subscription</h3>
          <div className="flex items-center gap-3">
            <span className="text-xl font-bold text-gray-800">{subscription.plan.name}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[subscription.status] || ""}`}>
              {subscription.status}
            </span>
          </div>
          {subscription.expires_at && (
            <p className="text-sm text-gray-500 mt-1">
              {subscription.status === "trial" ? "Trial ends" : "Renews"}{" "}
              {new Date(subscription.expires_at).toLocaleDateString("en-IN")}
            </p>
          )}
          <div className="mt-3 grid grid-cols-3 gap-3 text-sm">
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <p className="font-semibold">{subscription.plan.max_tables === -1 ? "∞" : subscription.plan.max_tables}</p>
              <p className="text-xs text-gray-500">Tables</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <p className="font-semibold">{subscription.plan.max_menu_items === -1 ? "∞" : subscription.plan.max_menu_items}</p>
              <p className="text-xs text-gray-500">Menu Items</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-2 text-center">
              <p className="font-semibold">{subscription.plan.has_analytics ? "Yes" : "No"}</p>
              <p className="text-xs text-gray-500">Analytics</p>
            </div>
          </div>
        </div>
      )}

      {/* Plans */}
      <div>
        <h3 className="font-semibold text-gray-700 mb-3">Available Plans</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const isCurrent = subscription?.plan?.id === plan.id;
            return (
              <div key={plan.id}
                className={`bg-white rounded-xl shadow-sm p-4 border-2 ${isCurrent ? "border-orange-400" : "border-transparent"}`}>
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-gray-800">{plan.name}</h4>
                  {isCurrent && <CheckCircle size={16} className="text-orange-500" />}
                </div>
                <p className="text-2xl font-bold text-gray-800 mb-1">
                  ₹{plan.price_monthly}
                  <span className="text-sm font-normal text-gray-500">/mo</span>
                </p>
                <ul className="text-xs text-gray-600 space-y-1 mb-4">
                  <li>{plan.max_tables === -1 ? "Unlimited" : plan.max_tables} tables</li>
                  <li>{plan.max_menu_items === -1 ? "Unlimited" : plan.max_menu_items} menu items</li>
                  <li>{plan.has_analytics ? "Analytics included" : "No analytics"}</li>
                </ul>
                {!isCurrent && (
                  <button
                    onClick={() => handleChangePlan(plan.id)}
                    disabled={loading === plan.id}
                    className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white text-sm font-semibold py-2 rounded-lg">
                    {loading === plan.id ? "…" : "Switch"}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Invoices */}
      {invoices.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3">Invoices</h3>
          <table className="w-full text-sm">
            <thead className="border-b">
              <tr>
                <th className="text-left py-2 text-xs text-gray-500">#</th>
                <th className="text-left py-2 text-xs text-gray-500">Date</th>
                <th className="text-left py-2 text-xs text-gray-500">Amount</th>
                <th className="text-left py-2 text-xs text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} className="border-b last:border-0">
                  <td className="py-2">#{inv.id}</td>
                  <td className="py-2 text-gray-600">
                    {new Date(inv.issued_at).toLocaleDateString("en-IN")}
                  </td>
                  <td className="py-2 font-medium">₹{inv.amount}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      inv.status === "paid" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
                    }`}>
                      {inv.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
