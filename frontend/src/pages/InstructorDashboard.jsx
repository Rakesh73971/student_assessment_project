import { useState, useEffect } from "react";
import { apiClient } from "../api/client";
import { formatApiErrorDetail } from "../utils/formatApiError";
import { Plus, Check, Save, Users } from "lucide-react";

const InstructorDashboard = () => {
  const [testData, setTestData] = useState({
    title: "",
    description: "",
    subject: "",
    duration_minutes: 60,
    passing_score: 70,
    test_type: "practice",
    cohort_id: "",
    publish: false,
  });

  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: "",
    question_type: "SHORT_ANSWER",
    correct_answer: "",
    points: 10,
  });

  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [cohorts, setCohorts] = useState([]);
  const [cohortForm, setCohortForm] = useState({
    name: "",
    description: "",
  });

  const loadCohorts = async () => {
    try {
      const res = await apiClient.get("/api/v1/cohorts");
      setCohorts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("Failed to load cohorts", err);
      setCohorts([]);
    }
  };

  const handleAddQuestion = () => {
    if (!currentQuestion.question_text || !currentQuestion.correct_answer) {
      return;
    }

    setQuestions((previousQuestions) => [
      ...previousQuestions,
      { ...currentQuestion, order: previousQuestions.length + 1 },
    ]);
    setCurrentQuestion({
      question_text: "",
      question_type: "SHORT_ANSWER",
      correct_answer: "",
      points: 10,
    });
  };

  const handleCreateTest = async () => {
    try {
      setLoading(true);
      setStatusMessage("");

      if (!testData.title || questions.length === 0) {
        setStatusMessage("Title and at least one question are required.");
        return;
      }

      const payload = {
        title: testData.title,
        description: testData.description,
        subject: testData.subject,
        duration_minutes: Number(testData.duration_minutes),
        passing_score: Number(testData.passing_score),
        test_type: testData.test_type.toLowerCase(),
        cohort_id: testData.cohort_id ? Number(testData.cohort_id) : null,

        questions: questions.map((q) => ({
          question_text: q.question_text,
          question_type: q.question_type.toLowerCase(),
          correct_answer: q.correct_answer,
          explanation: "",
          points: q.points || 1,
          order: q.order || 1,
          options: Array.isArray(q.options) ? q.options : null,
        })),
      };

      const res = await apiClient.post("/api/v1/tests/", payload);

      // If instructor chose to publish immediately, update the test
      if (testData.publish && res?.data?.id) {
        try {
          await apiClient.put(`/api/v1/tests/${res.data.id}`, {
            is_published: true,
          });
        } catch (err) {
          console.warn("Failed to publish test immediately", err);
        }
      }

      setStatusMessage("Test created successfully.");

      setTestData({
        title: "",
        description: "",
        subject: "",
        duration_minutes: 60,
        passing_score: 70,
        test_type: "practice",
        cohort_id: "",
        publish: false,
      });

      setQuestions([]);
    } catch (error) {
      console.error(error);
      setStatusMessage(
        formatApiErrorDetail(error.response?.data?.detail) ||
          error.friendlyMessage ||
          error.message ||
          "Failed to create test.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCohort = async () => {
    if (!cohortForm.name.trim()) {
      setStatusMessage("Cohort name is required.");
      return;
    }

    try {
      setLoading(true);
      setStatusMessage("");

      const res = await apiClient.post("/api/v1/cohorts/", {
        name: cohortForm.name.trim(),
        description: cohortForm.description.trim() || null,
      });

      setCohortForm({ name: "", description: "" });
      setTestData((current) => ({
        ...current,
        cohort_id: res.data?.id ? String(res.data.id) : current.cohort_id,
      }));
      await loadCohorts();
      setStatusMessage("Cohort created successfully.");
    } catch (error) {
      console.error(error);
      setStatusMessage(
        formatApiErrorDetail(error.response?.data?.detail) ||
          error.friendlyMessage ||
          error.message ||
          "Failed to create cohort.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadInitialCohorts = async () => {
      await loadCohorts();
    };

    loadInitialCohorts();
  }, []);

  return (
    <div className="animate-fade-in" style={{ padding: "2rem 0" }}>
      <header style={{ marginBottom: "2rem" }}>
        <h1
          style={{
            marginBottom: "0.5rem",
            background: "linear-gradient(to right, #fff, #a1a1aa)",
            WebkitBackgroundClip: "text",
            color: "transparent",
          }}
        >
          Instructor Dashboard
        </h1>
        <p>Manage tests and monitor student performance.</p>
      </header>

      {statusMessage && (
        <div
          className="glass-panel"
          style={{ padding: "1rem 1.25rem", marginBottom: "1.5rem" }}
        >
          {statusMessage}
        </div>
      )}

      <div className="grid-1-1">
          {/* Test Details Form */}
          <div className="glass-panel" style={{ padding: "2rem" }}>
            <h3
              style={{
                marginBottom: "1.5rem",
                borderBottom: "1px solid var(--border-light)",
                paddingBottom: "0.75rem",
              }}
            >
              Create Cohort
            </h3>

            <div className="form-group">
              <label className="form-label">Cohort Name</label>
              <input
                type="text"
                className="form-input"
                value={cohortForm.name}
                onChange={(e) =>
                  setCohortForm({ ...cohortForm, name: e.target.value })
                }
                placeholder="e.g. Beta Batch A"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Cohort Description</label>
              <textarea
                className="form-input"
                rows="2"
                value={cohortForm.description}
                onChange={(e) =>
                  setCohortForm({
                    ...cohortForm,
                    description: e.target.value,
                  })
                }
                placeholder="Optional notes about this group"
              ></textarea>
            </div>

            <button
              className="btn btn-secondary"
              style={{ width: "100%", marginBottom: "2rem" }}
              onClick={handleCreateCohort}
              disabled={loading || !cohortForm.name.trim()}
            >
              <Users size={16} /> Create Cohort
            </button>

            <h3
              style={{
                marginBottom: "1.5rem",
                borderBottom: "1px solid var(--border-light)",
                paddingBottom: "0.75rem",
              }}
            >
              Test Details
            </h3>

            <div className="form-group">
              <label className="form-label">Test Title</label>
              <input
                type="text"
                className="form-input"
                value={testData.title}
                onChange={(e) =>
                  setTestData({ ...testData, title: e.target.value })
                }
                placeholder="e.g. Midterm Python Assessment"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Subject</label>
              <input
                type="text"
                className="form-input"
                value={testData.subject}
                onChange={(e) =>
                  setTestData({ ...testData, subject: e.target.value })
                }
                placeholder="e.g. Computer Science"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-input"
                rows="3"
                value={testData.description}
                onChange={(e) =>
                  setTestData({ ...testData, description: e.target.value })
                }
                placeholder="Test description..."
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">Assign to Cohort</label>
              <select
                className="form-input"
                value={testData.cohort_id}
                onChange={(e) =>
                  setTestData({ ...testData, cohort_id: e.target.value })
                }
              >
                <option value="">(None)</option>
                {cohorts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name} {c.students_count ? `(${c.students_count})` : ""}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid-1-1">
              <div className="form-group">
                <label className="form-label">Duration (mins)</label>
                <input
                  type="number"
                  className="form-input"
                  value={testData.duration_minutes}
                  onChange={(e) =>
                    setTestData({
                      ...testData,
                      duration_minutes: e.target.value,
                    })
                  }
                />
              </div>
              <div className="form-group">
                <label className="form-label">Passing Score (%)</label>
                <input
                  type="number"
                  className="form-input"
                  value={testData.passing_score}
                  onChange={(e) =>
                    setTestData({ ...testData, passing_score: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="form-group" style={{ marginTop: "0.75rem" }}>
              <label className="form-label">
                <input
                  type="checkbox"
                  checked={testData.publish}
                  onChange={(e) =>
                    setTestData({ ...testData, publish: e.target.checked })
                  }
                />{" "}
                Publish immediately
              </label>
            </div>
          </div>

          {/* Question Builder */}
          <div>
            <div
              className="glass-panel"
              style={{ padding: "2rem", marginBottom: "2rem" }}
            >
              <h3
                style={{
                  marginBottom: "1.5rem",
                  borderBottom: "1px solid var(--border-light)",
                  paddingBottom: "0.75rem",
                }}
              >
                Add Question
              </h3>

              <div className="form-group">
                <label className="form-label">Question Text</label>
                <textarea
                  className="form-input"
                  rows="2"
                  value={currentQuestion.question_text}
                  onChange={(e) =>
                    setCurrentQuestion({
                      ...currentQuestion,
                      question_text: e.target.value,
                    })
                  }
                  placeholder="What is a closure in JavaScript?"
                ></textarea>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Correct / Model Answer (for AI evaluation)
                </label>
                <textarea
                  className="form-input"
                  rows="3"
                  value={currentQuestion.correct_answer}
                  onChange={(e) =>
                    setCurrentQuestion({
                      ...currentQuestion,
                      correct_answer: e.target.value,
                    })
                  }
                  placeholder="A closure is..."
                ></textarea>
              </div>

              <button
                className="btn btn-secondary"
                style={{ width: "100%" }}
                onClick={handleAddQuestion}
              >
                <Plus size={16} /> Add to Test
              </button>
            </div>

            {/* Questions List & Submit */}
            <div className="glass-panel" style={{ padding: "2rem" }}>
              <h3 style={{ marginBottom: "1.5rem" }}>Test Summary</h3>
              <p
                style={{
                  marginBottom: "1rem",
                  color: "var(--text-secondary)",
                  fontSize: "0.875rem",
                }}
              >
                {questions.length} questions added.
              </p>

              {questions.map((q, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "0.75rem",
                    background: "rgba(255,255,255,0.02)",
                    borderRadius: "var(--radius-md)",
                    marginBottom: "0.5rem",
                    fontSize: "0.875rem",
                  }}
                >
                  <strong>Q{idx + 1}:</strong> {q.question_text}
                </div>
              ))}

              <button
                className={`btn btn-primary`}
                style={{ width: "100%", marginTop: "1.5rem" }}
                onClick={handleCreateTest}
                disabled={loading || questions.length === 0 || !testData.title}
              >
                {loading ? (
                  "Saving..."
                ) : (
                  <>
                    {statusMessage === "Test created successfully." ? (
                      <Check size={18} />
                    ) : (
                      <Save size={18} />
                    )}{" "}
                    Save and Publish Test
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
    </div>
  );
};

export default InstructorDashboard;
