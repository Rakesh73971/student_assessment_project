export const normalizeRole = (role) => (role || "").toUpperCase();

export const isStudentRole = (role) => normalizeRole(role) === "STUDENT";

export const isInstructorRole = (role) => {
  const normalizedRole = normalizeRole(role);
  return normalizedRole === "INSTRUCTOR" || normalizedRole === "ADMIN";
};

export const canAccessRole = (userRole, requiredRole) => {
  const normalizedUserRole = normalizeRole(userRole);
  const normalizedRequiredRole = normalizeRole(requiredRole);

  if (!normalizedRequiredRole) {
    return true;
  }

  return (
    normalizedUserRole === normalizedRequiredRole ||
    normalizedUserRole === "ADMIN"
  );
};

export const getDefaultRouteForRole = (role) =>
  isStudentRole(role) ? "/student/dashboard" : "/instructor/dashboard";
