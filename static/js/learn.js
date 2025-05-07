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

  // Hide all interaction sections
  allInteractions.forEach(div => {
    div.style.display = "none";
  });

  // Show interaction section if it's a "you try" step
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

  // Clear feedback
  const feedback = document.getElementById("feedback");
  if (feedback) {
    feedback.textContent = "";
    feedback.classList.remove("text-success", "text-danger");
  }

  // Show/hide back button based on step
  const backBtn = document.getElementById("back-btn");
  if (backBtn) {
    backBtn.style.visibility = (step === 0) ? "hidden" : "visible";
    backBtn.style.pointerEvents = (step === 0) ? "none" : "auto";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const nextBtn = document.getElementById("next-btn");
  const backBtn = document.getElementById("back-btn");

  renderStep(currentStep);

  nextBtn.addEventListener("click", () => {
    if (currentStep < tutorialSteps.length - 1) {
      currentStep++;
      renderStep(currentStep);
    } else {
      window.location.href = `/complete_tutorial_and_redirect/${unitId}`;
    }
  });

  backBtn.addEventListener("click", () => {
    if (currentStep > 0) {
      currentStep--;
      renderStep(currentStep);
    }
  });

  // Optional: focus next on load
  nextBtn.focus();

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") {
      if (currentStep < tutorialSteps.length - 1) {
        currentStep++;
        renderStep(currentStep);
      } else {
        window.location.href = `/practice/${unitId}/easy`;
      }
    } else if (e.key === "ArrowLeft") {
      if (currentStep > 0) {
        currentStep--;
        renderStep(currentStep);
      }
    }
  });
  
});
