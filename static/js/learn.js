let currentStep = 0;

function renderStep(step) {
  const stepData = tutorialSteps[step];
  document.getElementById("instruction-text").innerText = stepData.text;
  document.getElementById("diagram-img").src = imgBaseUrl + stepData.img;
  document.getElementById("next-btn").innerText = stepData.button;
}

document.addEventListener("DOMContentLoaded", () => {
  renderStep(currentStep);

  document.getElementById("next-btn").addEventListener("click", () => {
    currentStep++;
    if (currentStep < tutorialSteps.length) {
      renderStep(currentStep);
    } else {
      window.location.href = `/practice/${unitId}/easy`; // or make difficulty dynamic
    }
  });
});

// auto hover the next button
window.addEventListener('DOMContentLoaded', (event) => {
  const nextBtn = document.getElementById('next-btn');
  if (nextBtn) {
      nextBtn.focus();
  }
});
