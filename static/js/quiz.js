FormSubmitted = false;

  document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('quiz-form');

    form.addEventListener('submit', function (event) {
      event.preventDefault();

      const formData = new FormData(form);

      fetch('/submit_answer', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById('feedback').innerHTML = `
          <span class="alert alert-${data.correct}">
            ${data.message}
            ${data.correct}
          </span>
        `;

        feedbackBox = document.getElementById('feedback')
        const result = data // loaned code
        console.log(result)
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
    });
  });

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('quiz-form');
  const submitBtn = form.querySelector('button[type="submit"]');
  const inputField = form.querySelector('input[name="user-answer"]');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    submitFormElements(submitBtn, inputField)

    const formData = new FormData(form);

    fetch('/submit_answer', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
     /*
      document.getElementById('feedback').innerHTML = `
        <div class="alert alert-${data.status} mt-3">${data.message}</div>
      `;
        */
      document.getElementById('nextButton').focus();

    })
    .catch(err => {
      console.error('Error:', err);
      submitBtn.disabled = false;
      inputField.disabled = false;
    });
  });
});

$(document).ready(function () {
  // Your code here
    $('#nextButton').hide()
});

function submitFormElements(submitBtn, inputField) { // function to clear buttons and show correct feedback text
    // Disable form controls after first submission
    $('#nextButton').show();
    //submitBtn.style.visibility = 'hidden';
    submitBtn.disabled = true;
    //inputField.disabled = true;
}


