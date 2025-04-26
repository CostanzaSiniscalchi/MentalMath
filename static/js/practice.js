document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('practice-form');
    const submitBtn = document.getElementById('practice-submit');
    const nextBtn = document.getElementById('nextBtn');
    const feedbackDiv = document.getElementById('feedback');
    const answerInput = document.querySelector('input[name="user-answer"]');
    let submitted = false;

    // Autofocus on the input when page loads
    if (answerInput) {
        answerInput.focus();
    }

    // When user submits an answer
    form.addEventListener('submit', function(e) {
        e.preventDefault();  // prevent normal form submission

        const formData = new FormData(form);

        fetch('/submit_practice_answer', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            feedbackDiv.style.display = 'block';
            feedbackDiv.classList.remove('alert-success', 'alert-danger');
            if (data.correct) {
                feedbackDiv.classList.add('alert-success');
                feedbackDiv.textContent = data.message;
            } else {
                feedbackDiv.classList.add('alert-danger');
                feedbackDiv.textContent = data.message;
            }

            // After submission, enable the Next button
            nextBtn.disabled = false;
            submitted = true;

            // Disable submit button so user can't double-submit
            submitBtn.disabled = true;

            // Clear the input box and refocus for the next typing
            if (answerInput) {
                answerInput.blur();  // small trick to reset field
                answerInput.focus();
            }
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
        });
    });

    // Handle Enter key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (!submitted) {
                // If not yet submitted, Enter triggers Submit
                submitBtn.click();
            } else {
                // If already submitted, Enter triggers Next
                nextBtn.click();
            }
        }
    });
});
