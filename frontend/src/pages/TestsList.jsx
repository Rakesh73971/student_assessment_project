import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { formatApiErrorDetail } from "../utils/formatApiError";
import { Play, ChevronRight } from "lucide-react";

const TestsList = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await apiClient.get("/api/v1/tests");
        setTests(Array.isArray(res.data) ? res.data : []);
      } catch (err) {
        console.error("Failed to load tests", err);
        setTests([]);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const handleStart = async (testId) => {
    try {
      setErrorMessage("");
      const res = await apiClient.post("/api/v1/tests/sessions/start", {
        test_id: testId,
      });
      navigate(`/student/test/${res.data.session_id}?testId=${testId}`);
    } catch (err) {
      setErrorMessage(
        formatApiErrorDetail(err.response?.data?.detail) ||
          err.friendlyMessage ||
          err.message ||
          "Failed to start session.",
      );
    }
  };

  if (loading)
    return (
      <div className="flex-center" style={{ minHeight: "40vh" }}>
        Loading tests...
      </div>
    );

  return (
    <div style={{ padding: "2rem 0" }}>
      <header style={{ marginBottom: "1.5rem" }}>
        <h2>Available Tests</h2>
        <p style={{ color: "var(--text-secondary)" }}>
          Practice tests and assessments available to you.
        </p>
        {errorMessage && (
          <p style={{ color: "var(--danger)", marginTop: "0.75rem" }}>
            {errorMessage}
          </p>
        )}
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "1rem",
        }}
      >
        {tests.length === 0 ? (
          <div className="glass-panel" style={{ padding: "1.5rem" }}>
            No tests found.
          </div>
        ) : (
          tests.map((t) => (
            <div
              key={t.id}
              className="glass-panel glass-panel-hover"
              style={{ padding: "1.25rem" }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <h3 style={{ margin: 0 }}>{t.title}</h3>
                  <div
                    style={{
                      color: "var(--text-secondary)",
                      fontSize: "0.9rem",
                    }}
                  >
                    {t.subject} • {t.test_type}
                  </div>
                </div>
                <div
                  style={{
                    display: "flex",
                    gap: "0.5rem",
                    alignItems: "center",
                  }}
                >
                  <button
                    className="btn btn-primary"
                    onClick={() => handleStart(t.id)}
                  >
                    <Play size={14} /> Start
                  </button>
                  <ChevronRight size={18} />
                </div>
              </div>
              <p style={{ marginTop: "0.75rem", color: "var(--text-muted)" }}>
                {t.description}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TestsList;
