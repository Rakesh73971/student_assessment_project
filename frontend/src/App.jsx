import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { useAuth } from "./contexts/useAuth";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import StudentDashboard from "./pages/StudentDashboard";
import InstructorDashboard from "./pages/InstructorDashboard";
import InstructorTests from "./pages/InstructorTests";
import TestTaking from "./pages/TestTaking";
import TestResults from "./pages/TestResults";
import TestsList from "./pages/TestsList";
import { canAccessRole, getDefaultRouteForRole } from "./utils/auth";

const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) return null;

  if (!user) {
    return <Navigate to="/login" />;
  }

  if (requiredRole && !canAccessRole(user.role, requiredRole)) {
    return <Navigate to="/" />;
  }

  return children;
};

const AppRoutes = () => {
  const { user } = useAuth();

  return (
    <Routes>
      <Route element={<Layout />}>
        {/* Public Routes */}
        <Route
          path="/"
          element={
            user ? (
              <Navigate
                to={
                  getDefaultRouteForRole(user.role)
                }
              />
            ) : (
              <div
                className="flex-center animate-fade-in"
                style={{
                  minHeight: "70vh",
                  flexDirection: "column",
                  textAlign: "center",
                }}
              >
                <h1
                  style={{
                    fontSize: "3.5rem",
                    marginBottom: "1rem",
                    background:
                      "linear-gradient(to right, var(--accent-primary), var(--accent-tertiary))",
                    WebkitBackgroundClip: "text",
                    color: "transparent",
                  }}
                >
                  AI-Powered Student Assessment
                </h1>
                <p
                  style={{
                    fontSize: "1.25rem",
                    color: "var(--text-secondary)",
                    maxWidth: "600px",
                    marginBottom: "2rem",
                  }}
                >
                  Next-generation platform for interactive learning, practice
                  sessions, and automated intelligent feedback.
                </p>
                <div style={{ display: "flex", gap: "1rem" }}>
                  <Link
                    to="/register"
                    className="btn btn-primary"
                    style={{ padding: "0.875rem 2rem", fontSize: "1rem" }}
                  >
                    Get Started
                  </Link>
                  <Link
                    to="/login"
                    className="btn btn-secondary"
                    style={{ padding: "0.875rem 2rem", fontSize: "1rem" }}
                  >
                    Sign In
                  </Link>
                </div>
              </div>
            )
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Student Routes */}
        <Route
          path="/tests"
          element={
            <ProtectedRoute requiredRole="STUDENT">
              <TestsList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/dashboard"
          element={
            <ProtectedRoute requiredRole="STUDENT">
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/test/:sessionId"
          element={
            <ProtectedRoute requiredRole="STUDENT">
              <TestTaking />
            </ProtectedRoute>
          }
        />
        <Route
          path="/student/results/:sessionId"
          element={
            <ProtectedRoute requiredRole="STUDENT">
              <TestResults />
            </ProtectedRoute>
          }
        />

        {/* Instructor Routes */}
        <Route
          path="/instructor/dashboard"
          element={
            <ProtectedRoute requiredRole="INSTRUCTOR">
              <InstructorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/instructor/tests"
          element={
            <ProtectedRoute requiredRole="INSTRUCTOR">
              <InstructorTests />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
