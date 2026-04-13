import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";
import DashboardHome from "./pages/dashboard/Home";
import MenuPage from "./pages/menu/MenuPage";
import TablesPage from "./pages/tables/TablesPage";
import OrdersPage from "./pages/orders/OrdersPage";
import AnalyticsPage from "./pages/analytics/AnalyticsPage";
import BillingPage from "./pages/billing/BillingPage";
import KitchenBoard from "./pages/kitchen/KitchenBoard";
import WaiterTables from "./pages/waiter/WaiterTables";
import WaiterTableDetail from "./pages/waiter/WaiterTableDetail";
import CustomerCheckin from "./pages/customer/Checkin";
import CustomerMenu from "./pages/customer/Menu";
import CustomerConfirmation from "./pages/customer/Confirmation";
import CustomerTrack from "./pages/customer/Track";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Auth */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Customer (public) */}
          <Route path="/t/:qrToken/checkin" element={<CustomerCheckin />} />
          <Route path="/t/:qrToken/menu" element={<CustomerMenu />} />
          <Route path="/t/:qrToken/confirmation/:orderId" element={<CustomerConfirmation />} />
          <Route path="/t/:qrToken/track/:orderId" element={<CustomerTrack />} />
          <Route path="/t/:qrToken" element={<Navigate to="menu" replace />} />

          {/* Kitchen (no sidebar layout) */}
          <Route
            path="/kitchen"
            element={
              <ProtectedRoute roles={["restaurant_admin", "kitchen_staff"]}>
                <KitchenBoard />
              </ProtectedRoute>
            }
          />

          {/* Waiter (no sidebar layout) */}
          <Route
            path="/waiter"
            element={
              <ProtectedRoute roles={["restaurant_admin", "waiter"]}>
                <WaiterTables />
              </ProtectedRoute>
            }
          />
          <Route
            path="/waiter/table/:id"
            element={
              <ProtectedRoute roles={["restaurant_admin", "waiter"]}>
                <WaiterTableDetail />
              </ProtectedRoute>
            }
          />

          {/* Admin dashboard */}
          <Route
            path="/"
            element={
              <ProtectedRoute roles={["restaurant_admin"]}>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardHome />} />
            <Route path="menu" element={<MenuPage />} />
            <Route path="tables" element={<TablesPage />} />
            <Route path="orders" element={<OrdersPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="billing" element={<BillingPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
