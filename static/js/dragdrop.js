function setupDragAndDrop() {
  // Drag source
  document.querySelectorAll('.number').forEach(el => {
    el.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/plain', e.target.textContent);
    });
  });

  // Drop target
  const dropBoxes = document.querySelectorAll('[data-box]');
  dropBoxes.forEach(box => {
    box.addEventListener('dragover', e => e.preventDefault());

    box.addEventListener('drop', e => {
      e.preventDefault();
      const num = e.dataTransfer.getData('text/plain');
      box.textContent = num;
    });

    box.addEventListener('dblclick', () => {
      box.textContent = '';
    });
  });

  // Clear button
const clearBtn = document.getElementById('clear-btn');
if (clearBtn) {
  clearBtn.addEventListener('click', () => {
    // Only find drop-boxes at the time of the click
    const activeInteraction = document.querySelector('.question-interaction[style*="display: block"]');
    const dropBoxes = activeInteraction ? activeInteraction.querySelectorAll('[data-box]') : [];

    dropBoxes.forEach(box => {
      box.textContent = '';
      box.classList.remove('correct', 'incorrect');
    });

    const feedback = document.getElementById("feedback");
    if (feedback) {
      feedback.textContent = "";
      feedback.classList.remove("text-success", "text-danger");
    }
  });
}
  // Submit button
  const checkBtn = document.getElementById('check-btn');
  if (checkBtn) {
    checkBtn.addEventListener('click', checkAnswer);
  }
}

function checkAnswer() {
  const activeInteraction = document.querySelector('.question-interaction[style*="display: block"]');
  const dropBoxes = activeInteraction ? activeInteraction.querySelectorAll('[data-box]') : [];

  const stepData = tutorialSteps[currentStep];
  const correctAnswer = stepData["answer"];
  const userAnswer = Array.from(dropBoxes).map(box => box.textContent.trim());

  const feedback = document.getElementById("feedback");

  if (!correctAnswer || userAnswer.length !== correctAnswer.length) {
    feedback.textContent = "No answer to check for this step.";
    feedback.className = "text-danger fw-bold text-center";
    return;
  }

  // Clear previous highlights
  dropBoxes.forEach(box => {
    box.classList.remove('correct', 'incorrect');
  });

  let isCorrect = true;

  dropBoxes.forEach((box, idx) => {
    const userVal = box.textContent.trim();
    const correctVal = String(correctAnswer[idx]);

    if (userVal === correctVal) {
      box.classList.add('correct');
    } else {
      box.classList.add('incorrect');
      isCorrect = false;
    }
  });

  feedback.textContent = isCorrect ? "Correct!" : "Try again!";
  feedback.className = isCorrect ? "text-success fw-bold text-center" : "text-danger fw-bold text-center";
}

