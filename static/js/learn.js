let currentStep = 0;

function renderStep(step) {
  const stepData = tutorialSteps[step];

  // Update instruction text and image
  document.getElementById("instruction-text").innerText = stepData.text;
  document.getElementById("diagram-img").src = imgBaseUrl + stepData.img;
  document.getElementById("next-btn").innerText = stepData.button;

  const interactionWrapper = document.getElementById("interaction-wrapper");
  const allInteractions = interactionWrapper.querySelectorAll(".question-interaction");
  const interactionControls = document.getElementById("interaction-controls");

  if (stepData.img === "you_try.png" && stepData.interaction_id) {
    const target = document.getElementById(stepData.interaction_id);
    if (target) {
      target.style.display = "block";
      setupDragAndDrop();
    }
    interactionControls.style.display = "block";
  } else {
    interactionControls.style.display = "none";
  }
  // Hide all interaction sections
  allInteractions.forEach(div => {
    div.style.display = "none";
  });

  // Show the interaction specified by stepData.interaction_id
  if (stepData.img === "you_try.png" && stepData.interaction_id) {
    const target = document.getElementById(stepData.interaction_id);
    if (target) {
      target.style.display = "block";
      setupDragAndDrop();
    }
  }

  // Clear previous feedback
  const feedback = document.getElementById("feedback");
  if (feedback) {
    feedback.textContent = "";
    feedback.classList.remove("text-success", "text-danger");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderStep(currentStep);

  document.getElementById("next-btn").addEventListener("click", () => {
    currentStep++;
    if (currentStep < tutorialSteps.length) {
      renderStep(currentStep);
    } else {
      window.location.href = `/complete_tutorial_and_redirect/${unitId}`;
    }
  });
});

// Auto-focus Next button
window.addEventListener("DOMContentLoaded", () => {
  const nextBtn = document.getElementById("next-btn");
  if (nextBtn) {
    nextBtn.focus();
  }
});

