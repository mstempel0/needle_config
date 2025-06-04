
document.getElementById('runScript').addEventListener('click', async () => {
  const file1 = document.getElementById('file1').value.trim();
  const file2 = document.getElementById('file2').value.trim();

  const a = parseFloat(document.getElementById('paramA').value);
  const b = parseFloat(document.getElementById('paramB').value);
  const c = parseFloat(document.getElementById('paramC').value);

  const output = document.getElementById('output');
  output.textContent = 'Running...';

  if (!file1 || !file2) {
    output.textContent = '❌ Please enter both file paths.';
    return;
  }

  try {
    const result = await window.electron.runPython(file1, file2, a, b, c);
    output.textContent = result;
  } catch (err) {
    output.textContent = `❌ Python error:\n${err}`;
  }
});

// Live update of slider values
['A', 'B', 'C'].forEach(id => {
  const slider = document.getElementById(`param${id}`);
  const label = document.getElementById(`param${id}Val`);
  slider.addEventListener('input', () => {
    label.textContent = parseFloat(slider.value).toFixed(1);
  });
});

// Display version info
const info = document.getElementById('info');
info.textContent = `This app is using Chrome (v${window.versions.chrome()}), Node.js (v${window.versions.node()}), and Electron (v${window.versions.electron()})`;
