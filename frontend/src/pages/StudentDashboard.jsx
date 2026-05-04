import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/useAuth";
import { apiClient } from "../api/client";
import { formatApiErrorDetail } from "../utils/formatApiError";
import { Play, CheckCircle, Award, ChevronRight } from "lucide-react";

const StudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [scores, setScores] = useState([]);
  const [testId, setTestId] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const scoresRes = await apiClient.get("/api/v1/tests/scores/my");
        setScores(Array.isArray(scoresRes.data) ? scoresRes.data : []);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleStartTest = async (testId) => {
    try {
      setErrorMessage("");
      const res = await apiClient.post("/api/v1/tests/sessions/start", {
        test_id: testId,
      });
      navigate(`/student/test/${res.data.session_id}?testId=${testId}`);
    } catch (error) {
      setErrorMessage(
        formatApiErrorDetail(error.response?.data?.detail) ||
          error.friendlyMessage ||
          error.message ||
          "Failed to start test.",
      );
    }
  };

  const averageScore =
    scores.length > 0
      ? Math.round(
          scores.reduce((total, score) => total + (score.score ?? 0), 0) /
            scores.length,
        )
      : null;

  if (loading) {
    return (
      <div className="flex-center" style={{ minHeight: "50vh" }}>
        Loading dashboard...
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ padding: "2rem 0" }}>
      <header style={{ marginBottom: "3rem" }}>
        <h1
          style={{
            marginBottom: "0.5rem",
            background: "linear-gradient(to right, #fff, #a1a1aa)",
            WebkitBackgroundClip: "text",
            color: "transparent",
          }}
        >
          Welcome, {user?.full_name || user?.email}
        </h1>
        <p>Ready to continue your learning journey?</p>
      </header>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "2rem",
          marginBottom: "4rem",
        }}
      >
        {/* Quick Stats */}
        <div
          className="glass-panel"
          style={{
            padding: "1.5rem",
            display: "flex",
            alignItems: "center",
            gap: "1.5rem",
          }}
        >
          <div
            style={{
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              background: "rgba(99, 102, 241, 0.1)",
              border: "1px solid rgba(99, 102, 241, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--accent-primary)",
            }}
          >
            <Award size={28} />
          </div>
          <div>
            <p style={{ fontSize: "0.875rem", marginBottom: "0.25rem" }}>
              Completed Tests
            </p>
            <h2 style={{ fontSize: "1.75rem", margin: 0 }}>{scores.length}</h2>
          </div>
        </div>

        <div
          className="glass-panel"
          style={{
            padding: "1.5rem",
            display: "flex",
            alignItems: "center",
            gap: "1.5rem",
          }}
        >
          <div
            style={{
              width: "60px",
              height: "60px",
              borderRadius: "50%",
              background: "rgba(16, 185, 129, 0.1)",
              border: "1px solid rgba(16, 185, 129, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--success)",
            }}
          >
            <CheckCircle size={28} />
          </div>
          <div>
            <p style={{ fontSize: "0.875rem", marginBottom: "0.25rem" }}>
              Average Score
            </p>
            <h2 style={{ fontSize: "1.75rem", margin: 0 }}>
              {averageScore != null ? `${averageScore}%` : "N/A"}
            </h2>
          </div>
        </div>
      </div>

      <div className="two-col">
        <div>
          <div className="flex-between" style={{ marginBottom: "1.5rem" }}>
            <h3>Available Practice Tests</h3>
          </div>

          <div
            className="glass-panel"
            style={{ padding: "2rem", textAlign: "center" }}
          >
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "50%",
                background: "rgba(255,255,255,0.05)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 1rem",
                color: "var(--text-muted)",
              }}
            >
              <Play size={24} />
            </div>
            <h4 style={{ marginBottom: "0.5rem" }}>Join a Practice Session</h4>
            <p
              style={{
                marginBottom: "1.5rem",
                fontSize: "0.875rem",
                maxWidth: "300px",
                margin: "0 auto 1.5rem",
              }}
            >
              Enter a Test ID provided by your instructor to begin a practice
              session.
            </p>

            {errorMessage && (
              <p
                style={{
                  margin: "0 0 1rem",
                  color: "var(--danger)",
                  fontSize: "0.875rem",
                }}
              >
                {errorMessage}
              </p>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleStartTest(testId);
              }}
              style={{
                display: "flex",
                gap: "0.5rem",
                maxWidth: "300px",
                margin: "0 auto",
              }}
            >
              <input
                type="number"
                className="form-input"
                placeholder="Test ID (e.g. 1)"
                value={testId}
                onChange={(event) => setTestId(event.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary">
                Start
              </button>
            </form>
          </div>
        </div>

        <div>
          <h3 style={{ marginBottom: "1.5rem" }}>Recent Results</h3>

          <div
            style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
          >
            {scores.length === 0 ? (
              <div
                className="glass-panel"
                style={{
                  padding: "1.5rem",
                  textAlign: "center",
                  color: "var(--text-muted)",
                  fontSize: "0.875rem",
                }}
              >
                No tests completed yet.
              </div>
            ) : (
              scores.map((score, idx) => {
                const scoreValue = Math.round((score.score ?? 0) * 100) / 100;
                const passed = Boolean(score.is_passed);
                const resultPath = score.session_id
                  ? `/student/results/${score.session_id}`
                  : null;
                return (
                  <div
                    key={score.id ?? idx}
                    className="glass-panel glass-panel-hover"
                    style={{
                      padding: "1.25rem",
                      cursor: resultPath ? "pointer" : "default",
                    }}
                    onClick={() => resultPath && navigate(resultPath)}
                  >
                    <div
                      className="flex-between"
                      style={{ marginBottom: "0.5rem" }}
                    >
                      <span style={{ fontWeight: 500 }}>
                        Test #{score.test_id}
                      </span>
                      <span
                        className={`badge ${passed ? "badge-success" : "badge-danger"}`}
                      >
                        {passed ? "Passed" : "Failed"}
                      </span>
                    </div>

                    <div
                      className="flex-between"
                      style={{
                        color: "var(--text-secondary)",
                        fontSize: "0.875rem",
                      }}
                    >
                      <span>Score: {scoreValue}%</span>
                      <ChevronRight size={16} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;
