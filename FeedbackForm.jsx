import React, { useState } from "react";
import axios from "axios";

export default function FeedbackForm() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    rating: 3,
    comments: ""
  });
  const [message, setMessage] = useState("");

  const handleChange = (e) => {
    setForm({...form, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/submit-feedback", form);
      setMessage(res.data.message);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Submission failed.");
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: "auto" }}>
      <h2>Excelrate Workshop Feedback</h2>
      <form onSubmit={handleSubmit}>
        <input
          name="name"
          placeholder="Full Name"
          value={form.name}
          onChange={handleChange}
          required
        /><br />
        <input
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        /><br />
        <label>Rating:</label>
        <input
          name="rating"
          type="number"
          min="1"
          max="5"
          value={form.rating}
          onChange={handleChange}
        /><br />
        <textarea
          name="comments"
          placeholder="Comments"
          value={form.comments}
          onChange={handleChange}
        /><br />
        <button type="submit">Submit</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}  on what extension i should save it
