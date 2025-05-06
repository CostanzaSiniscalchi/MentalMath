// practice.js

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('practice-form');
    const submitBtn = document.getElementById('practice-submit');
    const nextBtn = document.getElementById('nextBtn');
    const feedbackDiv = document.getElementById('feedback');
    const mcOptionsDiv = document.getElementById('mc-options');
    const textAnswerInput = document.getElementById('text-user-answer');
    const hiddenAnswerInput = document.getElementById('mc-user-answer');

    let submitted = false;

    function renderQuestionType() {
        if (window.questionData && window.questionData.type === 'mc') {
            // Hide text input, show multiple choice options
            document.getElementById('text-answer-block').style.display = 'none';
            mcOptionsDiv.style.display = 'flex';

            mcOptionsDiv.innerHTML = ''; // Clear previous options
            window.questionData.choices.forEach(choice => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-outline-primary mc-option';
                btn.textContent = choice;

                btn.addEventListener('click', () => {
                    document.querySelectorAll('.mc-option').forEach(b => b.classList.remove('selected'));
                    btn.classList.add('selected');
                    hiddenAnswerInput.value = choice;
                    submitBtn.disabled = false; // Enable submit only after selection
                });

                mcOptionsDiv.appendChild(btn);
            });

            hiddenAnswerInput.value = '';       // Reset previous selection
            submitBtn.disabled = true;          // Disable submit until user selects
        } else {
            // Show text input, hide multiple choice
            document.getElementById('text-answer-block').style.display = 'block';
            mcOptionsDiv.style.display = 'none';
            submitBtn.disabled = false; // Enable submit for free response
        }
    }

    renderQuestionType();

    // Autofocus input if available
    if (textAnswerInput) {
        textAnswerInput.focus();
        textAnswerInput.readOnly = false;
    }

    nextBtn.disabled = true;
    feedbackDiv.style.display = 'none';

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const isMC = window.questionData && window.questionData.type === 'mc';
        const answer = isMC ? hiddenAnswerInput.value : textAnswerInput.value;

        if (isMC && !answer) {
            feedbackDiv.style.display = 'block';
            feedbackDiv.classList.remove('alert-success');
            feedbackDiv.classList.add('alert-danger');
            feedbackDiv.textContent = 'Please select an answer before submitting.';
            return;
        }

        const formData = new FormData();
        formData.append('user-answer', answer);

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

                // Lock inputs
                if (textAnswerInput) textAnswerInput.readOnly = true;
                document.querySelectorAll('.mc-option').forEach(btn => btn.disabled = true);
                submitBtn.disabled = true;
                nextBtn.disabled = false;
                submitted = true;
            })
            .catch(error => {
                console.error('Error submitting answer:', error);
            });
    });

    // Enter key behavior
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
