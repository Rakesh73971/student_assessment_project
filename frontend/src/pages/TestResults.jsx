import { useState, useEffect } from "react";
import { useParams, Link, useLocation } from "react-router-dom";
import { CheckCircle, XCircle, Award, ArrowLeft } from "lucide-react";
import { apiClient } from "../api/client";

const TestResults = () => {
  const { sessionId } = useParams();
  const location = useLocation();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadResult = async () => {
      if (location.state && location.state.result) {
        setResults(location.state.result);
        setLoading(false);
        return;
      }

      
      try {
        const res = await apiClient.get(`/api/v1/tests/sessions/${sessionId}`);
        
        const data = res.data;
        const passingScore = data.passing_score;
        const scoreVal = data.score;
        setResults({
          score: scoreVal != null ? Math.round(scoreVal) : null,
          passed:
            scoreVal != null && passingScore != null
              ? scoreVal >= passingScore
              : null,
          ai_feedback: data.ai_feedback,
          responses: data.responses || [],
          test_id: data.test_id,
          created_at: data.created_at,
        });
      } catch (err) {
        console.error("Failed to load session details", err);
        setResults({
          score: null,
          passed: false,
          ai_feedback: "Result not found or inaccessible.",
        });
      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [sessionId, location.state]);

  if (loading)
    return (
      <div className="flex-center" style={{ minHeight: "50vh" }}>
        Loading results...
      </div>
    );

  return (
    <div
      className="animate-fade-in"
      style={{ padding: "2rem 0", maxWidth: "800px", margin: "0 auto" }}
    >
      <Link
        to="/student/dashboard"
        className="btn btn-secondary"
        style={{ marginBottom: "2rem" }}
      >
        <ArrowLeft size={16} /> Back to Dashboard
      </Link>

      <div
        className="glass-panel"
        style={{ padding: "3rem", textAlign: "center", marginBottom: "2rem" }}
      >
        <div
          style={{
            width: "80px",
            height: "80px",
            borderRadius: "50%",
            background: results.passed
              ? "rgba(16, 185, 129, 0.1)"
              : "rgba(239, 68, 68, 0.1)",
            border: `2px solid ${results.passed ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)"}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 1.5rem",
            color: results.passed ? "var(--success)" : "var(--danger)",
          }}
        >
          {results.passed ? <Award size={40} /> : <XCircle size={40} />}
        </div>

        <h2 style={{ marginBottom: "0.5rem" }}>
          {results.passed ? "Congratulations!" : "Keep Practicing"}
        </h2>
        <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
          You have {results.passed ? "passed" : "failed"} the assessment.
        </p>

        <div
          style={{
            display: "inline-block",
            padding: "1.5rem 3rem",
            background: "rgba(0,0,0,0.2)",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border-light)",
          }}
        >
          <div
            style={{
              fontSize: "0.875rem",
              color: "var(--text-muted)",
              marginBottom: "0.5rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
              fontWeight: 600,
            }}
          >
            Final Score
          </div>
          <div
            style={{
              fontSize: "3rem",
              fontWeight: 700,
              lineHeight: 1,
              color: results.passed ? "var(--success)" : "var(--danger)",
            }}
          >
            {results.score}%
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "2.5rem" }}>
        <h3
          style={{
            marginBottom: "1.5rem",
            display: "flex",
            alignItems: "center",
            gap: "0.5rem",
          }}
        >
          <CheckCircle size={20} color="var(--accent-primary)" />
          AI Feedback & Analysis
        </h3>
        <div
          style={{
            lineHeight: 1.8,
            color: "var(--text-secondary)",
            fontSize: "1.05rem",
            background: "rgba(99, 102, 241, 0.05)",
            padding: "1.5rem",
            borderRadius: "var(--radius-md)",
            borderLeft: "4px solid var(--accent-primary)",
          }}
        >
          {results.ai_feedback}
        </div>
      </div>

      {results.responses && results.responses.length > 0 && (
        <div
          className="glass-panel"
          style={{ padding: "2rem", marginTop: "1rem" }}
        >
          <h3 style={{ marginBottom: "1rem" }}>Responses</h3>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {results.responses.map((r) => (
              <div
                key={r.id}
                style={{
                  padding: "0.75rem",
                  borderRadius: "8px",
                  background: "rgba(255,255,255,0.02)",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "0.5rem",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>
                    {r.question_text || `Question ${r.question_id}`}
                  </div>
                  <div
                    style={{
                      color: r.is_correct ? "var(--success)" : "var(--danger)",
                      fontWeight: 700,
                    }}
                  >
                    {r.is_correct ? "Correct" : "Incorrect"}
                  </div>
                </div>
                <div style={{ color: "var(--text-secondary)" }}>
                  <strong>Your answer:</strong> {r.answer_text}
                </div>
                {r.points_earned != null && (
                  <div
                    style={{
                      marginTop: "0.5rem",
                      color: "var(--text-secondary)",
                    }}
                  >
                    <strong>Points earned:</strong> {r.points_earned}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TestResults;
