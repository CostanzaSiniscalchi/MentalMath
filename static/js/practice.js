document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("practice-form");
    const feedbackBox = document.getElementById("feedback");
    const nextButton = document.getElementById("nextBtn");
  
    if (form) {
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
  
        const formData = new FormData(form);
        const response = await fetch("/submit_practice_answer", {
            method: "POST",
            body: formData
          });
  
        if (!response.ok) {
          feedbackBox.className = "alert alert-danger";
          feedbackBox.innerText = "Something went wrong. Try again.";
          feedbackBox.style.display = "block";
          return;
        }
  
        const result = await response.json();
        feedbackBox.className = result.correct
          ? "alert alert-success"
          : "alert alert-warning";
        feedbackBox.innerText = result.message;
        feedbackBox.style.display = "block";
  
        // Optionally disable the form so users can't re-submit
        form.querySelector("input[name='user-answer']").disabled = true;
        form.querySelector("button[type='submit']").disabled = true;
  
        // Enable "Next Question" button
        nextButton.disabled = false;
      });
    }
  });
  