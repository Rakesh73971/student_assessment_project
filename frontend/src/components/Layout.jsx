import { Outlet, Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import {
  User,
  LogOut,
  LayoutDashboard,
  GraduationCap,
  ClipboardList,
} from "lucide-react";
import {
  getDefaultRouteForRole,
  isInstructorRole,
  isStudentRole,
} from "../utils/auth";

const Layout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isStudent = isStudentRole(user?.role);
  const isInstructor = isInstructorRole(user?.role);

  const dashboardPath = getDefaultRouteForRole(user?.role);
  const testsPath = isStudent ? "/tests" : "/instructor/tests";
  const isActive = (path) => location.pathname.startsWith(path);

  return (
    <div className="page-wrapper">
      {/* HEADER - render only when user exists */}
      {user && (
        <header style={headerStyle} className="glass-panel">
          <div className="container flex-between" style={{ height: "100%" }}>
            {/* LOGO */}
            <Link
              to="/"
              className="flex-center"
              style={{
                gap: "0.5rem",
                color: "var(--text-primary)",
                fontWeight: 700,
                fontSize: "1.25rem",
              }}
            >
              <GraduationCap size={28} color="var(--accent-primary)" />
              <span>AssessAI</span>
            </Link>

            {/* NAVIGATION */}
            <nav className="flex-center" style={{ gap: "1.2rem" }}>
              {/* DASHBOARD */}
              <Link
                to={dashboardPath}
                style={{
                  ...navLinkStyle,
                  color: isActive(dashboardPath)
                    ? "var(--accent-primary)"
                    : "var(--text-secondary)",
                }}
              >
                <LayoutDashboard size={18} />
                Dashboard
              </Link>

              {(isStudent || isInstructor) && (
                <Link
                  to={testsPath}
                  style={{
                    ...navLinkStyle,
                    color: isActive(testsPath)
                      ? "var(--accent-primary)"
                      : "var(--text-secondary)",
                  }}
                >
                  <ClipboardList size={18} />
                  Tests
                </Link>
              )}

              {/* USER INFO */}
              <div
                className="flex-center"
                style={{
                  gap: "1rem",
                  marginLeft: "1rem",
                  paddingLeft: "1rem",
                  borderLeft: "1px solid var(--border-light)",
                }}
              >
                <span
                  className="flex-center"
                  style={{ gap: "0.5rem", fontSize: "0.875rem" }}
                >
                  <User size={16} color="var(--text-muted)" />
                  {user.full_name || user.email}
                </span>

                <button onClick={handleLogout} className="btn btn-secondary">
                  <LogOut size={16} />
                  Logout
                </button>
              </div>
            </nav>
          </div>
        </header>
      )}

      {/* PAGE CONTENT */}
      <main
        className="container animate-fade-in"
        style={{ paddingTop: user ? "6rem" : "2rem" }}
      >
        <Outlet />
      </main>
    </div>
  );
};

const headerStyle = {
  position: "fixed",
  top: "1rem",
  left: "50%",
  transform: "translateX(-50%)",
  width: "calc(100% - 2rem)",
  maxWidth: "1200px",
  height: "4rem",
  zIndex: 50,
};

const navLinkStyle = {
  display: "flex",
  alignItems: "center",
  gap: "0.5rem",
  fontWeight: 500,
  fontSize: "0.95rem",
  transition: "color 0.2s ease",
};

export default Layout;
