function setupDragAndDrop() {
    document.querySelectorAll('.number').forEach(el => {
      el.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', e.target.textContent);
      });
    });
  
    const dropBoxes = document.querySelectorAll('[data-box]');
    dropBoxes.forEach(box => {
      box.addEventListener('dragover', (e) => e.preventDefault());
  
      box.addEventListener('drop', (e) => {
        e.preventDefault();
        const num = e.dataTransfer.getData('text/plain');
        box.textContent = num;
      });
  
      box.addEventListener('dblclick', () => {
        box.textContent = '';
      });
    });
  
    const clearBtn = document.getElementById('clear-btn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        dropBoxes.forEach(box => box.textContent = '');
      });
    }
  }
  