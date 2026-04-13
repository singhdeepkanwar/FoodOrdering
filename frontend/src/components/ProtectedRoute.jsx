import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  if (roles && !roles.includes(user.role)) {
    // Redirect to appropriate home based on role
    if (user.role === "kitchen_staff") return <Navigate to="/kitchen" replace />;
    if (user.role === "waiter") return <Navigate to="/waiter" replace />;
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
