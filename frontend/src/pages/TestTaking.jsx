import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { apiClient } from "../api/client";
import {
  CheckCircle,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

const TestTaking = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [test, setTest] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchTest = async () => {
      const testId = searchParams.get("testId");
      if (!testId) {
        
        setTest(null);
        setLoading(false);
        return;
      }

      try {
        const res = await apiClient.get(`/api/v1/tests/${testId}`);
        
        setTest(res.data);
      } catch (err) {
        console.error("Failed to load test details", err);
        setTest(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTest();
  }, [sessionId, searchParams]);

  const handleAnswerChange = (text) => {
    setAnswers({
      ...answers,
      [currentQuestionIndex]: text,
    });
  };

  const handleNext = () => {
    if (currentQuestionIndex < test.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitTest = async () => {
    try {
      setSubmitting(true);
      for (let idx = 0; idx < test.questions.length; idx++) {
        const answerText = answers[idx] ?? "";
        const questionId = test.questions[idx].id;
        await apiClient.post(
          `/api/v1/tests/sessions/${sessionId}/submit-response`,
          {
            question_id: questionId,
            answer_text: answerText,
          },
        );
      }

  
      const completeRes = await apiClient.post(
        `/api/v1/tests/sessions/${sessionId}/complete`,
      );

    
      navigate(`/student/results/${sessionId}`, {
        state: { result: completeRes.data },
      });
    } catch (error) {
      alert(
        "Failed to submit test: " +
          (error.response?.data?.detail || error.message),
      );
      setSubmitting(false);
    }
  };

  if (loading)
    return (
      <div className="flex-center" style={{ minHeight: "50vh" }}>
        Loading test...
      </div>
    );
  if (!test) return <div className="flex-center">Test not found.</div>;

  const currentQuestion = test.questions[currentQuestionIndex];

  return (
    <div
      className="animate-fade-in"
      style={{ padding: "2rem 0", maxWidth: "800px", margin: "0 auto" }}
    >
      <header className="flex-between" style={{ marginBottom: "2rem" }}>
        <h2>{test.title}</h2>
        <div className="badge badge-primary">
          Question {currentQuestionIndex + 1} of {test.questions.length}
        </div>
      </header>

      <div
        className="glass-panel"
        style={{ padding: "2.5rem", marginBottom: "2rem", minHeight: "300px" }}
      >
        <h3
          style={{
            marginBottom: "1.5rem",
            fontSize: "1.25rem",
            lineHeight: 1.6,
          }}
        >
          {currentQuestion.question_text}
        </h3>

        <div className="form-group">
          <textarea
            className="form-input"
            rows="6"
            placeholder="Type your answer here..."
            value={answers[currentQuestionIndex] || ""}
            onChange={(e) => handleAnswerChange(e.target.value)}
            style={{ fontSize: "1rem", padding: "1rem" }}
          ></textarea>
        </div>
      </div>

      <div className="flex-between">
        <button
          className="btn btn-secondary"
          onClick={handlePrev}
          disabled={currentQuestionIndex === 0}
        >
          <ChevronLeft size={18} /> Previous
        </button>

        {currentQuestionIndex === test.questions.length - 1 ? (
          <button
            className="btn btn-primary"
            onClick={handleSubmitTest}
            disabled={submitting}
          >
            {submitting ? (
              "Evaluating via AI..."
            ) : (
              <>
                <CheckCircle size={18} /> Submit Test
              </>
            )}
          </button>
        ) : (
          <button className="btn btn-primary" onClick={handleNext}>
            Next <ChevronRight size={18} />
          </button>
        )}
      </div>
    </div>
  );
};

export default TestTaking;
