document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('practice-form');
    const submitBtn = document.getElementById('practice-submit');
    const nextBtn = document.getElementById('nextBtn');
    const feedbackDiv = document.getElementById('feedback');
    const answerInput = document.querySelector('input[name="user-answer"]');

    let submitted = false; // reset on page load

    // Autofocus and reset input state
    if (answerInput) {
        answerInput.focus();
        answerInput.readOnly = false;
    }

    submitBtn.disabled = false;
    nextBtn.disabled = true;
    feedbackDiv.style.display = 'none';

    // Submit handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();

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

            // Lock form
            answerInput.readOnly = true;
            submitBtn.disabled = true;

            // Enable next
            nextBtn.disabled = false;
            submitted = true;
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
        });
    });

    // Enter key behavior
    document.addEventListener('keydown', function(e) {
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
