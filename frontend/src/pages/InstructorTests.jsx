import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { formatApiErrorDetail } from "../utils/formatApiError";

const InstructorTests = () => {
  const [tests, setTests] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get("/api/v1/tests/my");
        setTests(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error("Failed to load my tests", err);
        setTests([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const togglePublish = async (test) => {
    try {
      setErrorMessage("");
      const res = await apiClient.put(`/api/v1/tests/${test.id}`, {
        is_published: !test.is_published,
      });
      setTests((currentTests) =>
        currentTests.map((t) =>
          t.id === test.id ? { ...t, is_published: res.data.is_published } : t,
        ),
      );
    } catch (err) {
      setErrorMessage(
        formatApiErrorDetail(err.response?.data?.detail) ||
          err.friendlyMessage ||
          err.message ||
          "Failed to update publish status.",
      );
    }
  };

  if (loading) return <div className="flex-center">Loading your tests...</div>;

  return (
    <div style={{ padding: "2rem 0" }}>
      <h2>Your Tests</h2>
      <p style={{ color: "var(--text-secondary)" }}>
        Manage and publish tests you created.
      </p>
      {errorMessage && (
        <p style={{ color: "var(--danger)", marginTop: "0.75rem" }}>
          {errorMessage}
        </p>
      )}

      {tests.length === 0 ? (
        <div className="glass-panel" style={{ padding: "1.5rem" }}>
          You have not created any tests yet.
        </div>
      ) : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {tests.map((t) => (
            <div
              key={t.id}
              className="glass-panel"
              style={{
                padding: "1rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div>
                <div style={{ fontWeight: 700 }}>{t.title}</div>
                <div
                  style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}
                >
                  {t.subject} • {t.test_type}
                </div>
              </div>
              <div
                style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}
              >
                <button
                  className="btn btn-secondary"
                  onClick={() => togglePublish(t)}
                >
                  {t.is_published ? "Unpublish" : "Publish"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InstructorTests;
