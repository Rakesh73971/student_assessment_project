export function formatApiErrorDetail(detail) {
  if (detail == null) return null;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((e) =>
        e && typeof e === "object" && e.msg != null ? String(e.msg) : String(e),
      )
      .join(" ");
  }
  if (typeof detail === "object" && detail.msg != null) return String(detail.msg);
  return "Request failed";
}
