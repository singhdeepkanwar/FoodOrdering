import { useEffect, useState } from "react";
import { getAnalytics } from "../../api";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, Title, Tooltip, Legend,
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, Title, Tooltip, Legend
);

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getAnalytics()
      .then(({ data }) => setData(data))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load analytics."));
  }, []);

  if (error) {
    return (
      <div className="p-6">
        <h2 className="text-lg font-semibold mb-4">Analytics</h2>
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-6 text-center">
          <p className="text-orange-700 font-medium">{error}</p>
          <p className="text-sm text-orange-600 mt-1">Upgrade to the Pro plan to unlock analytics.</p>
        </div>
      </div>
    );
  }

  if (!data) return <div className="p-6 text-sm text-gray-400">Loading…</div>;

  const { revenue, top_items, peak_hours, summary } = data;

  const stats = [
    { label: "Total Revenue (30d)", value: `₹${summary.total_revenue.toFixed(2)}` },
    { label: "Orders Served", value: summary.total_orders },
    { label: "Avg Order Value", value: `₹${summary.avg_order_value}` },
  ];

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-lg font-semibold">Analytics</h2>

      <div className="grid grid-cols-3 gap-4">
        {stats.map(({ label, value }) => (
          <div key={label} className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-2xl font-bold text-gray-800">{value}</p>
            <p className="text-xs text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm p-4">
        <h3 className="font-semibold text-gray-700 mb-3 text-sm">Revenue — Last 30 Days</h3>
        <Line
          data={{
            labels: revenue.labels,
            datasets: [{
              label: "Revenue (₹)",
              data: revenue.data,
              borderColor: "#f97316",
              backgroundColor: "rgba(249,115,22,0.1)",
              tension: 0.3,
              fill: true,
            }],
          }}
          options={{ responsive: true, plugins: { legend: { display: false } } }}
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3 text-sm">Top 10 Items</h3>
          <Bar
            data={{
              labels: top_items.labels,
              datasets: [{
                label: "Qty Sold",
                data: top_items.data,
                backgroundColor: "#fb923c",
              }],
            }}
            options={{
              responsive: true,
              indexAxis: "y",
              plugins: { legend: { display: false } },
            }}
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm p-4">
          <h3 className="font-semibold text-gray-700 mb-3 text-sm">Peak Hours</h3>
          <Bar
            data={{
              labels: peak_hours.labels,
              datasets: [{
                label: "Orders",
                data: peak_hours.data,
                backgroundColor: "#fdba74",
              }],
            }}
            options={{ responsive: true, plugins: { legend: { display: false } } }}
          />
        </div>
      </div>
    </div>
  );
}
