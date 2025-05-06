document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('quiz-form');
  const submitBtn = document.getElementById('quizsubmit');
  const nextBtn = document.getElementById('nextBtn');
  const feedbackDiv = document.getElementById('feedback');
  const answerInput = document.getElementById('user-answer');

  let submitted = false;

  // Autofocus input when page loads
  if (answerInput) {
      answerInput.focus();
  }

  form.addEventListener('submit', function (e) {
      e.preventDefault();

      const formData = new FormData(form);

      fetch('/submit_answer', {
          method: 'POST',
          body: formData
      })
      .then(response => response.json())
      .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
                return;
            }
          feedbackDiv.style.display = 'block';
          feedbackDiv.classList.remove('alert-success', 'alert-warning');
          if (data.correct) {
              feedbackDiv.classList.add('alert-success');
              feedbackDiv.textContent = data.message;
          } else {
              feedbackDiv.classList.add('alert-warning');
              feedbackDiv.textContent = data.message;
          }

          // Disable submit button and input field
          submitBtn.disabled = true;
          answerInput.disabled = true;

          // Enable next button
          nextBtn.disabled = false;
          submitted = true;
      })
      .catch(error => {
          console.error('Error submitting answer:', error);
      });
  });

  document.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
          e.preventDefault();
          if (!submitted) {
              submitBtn.click();
          } else {
              nextBtn.click();
          }
      }
  });
});
