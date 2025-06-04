document.getElementById('run-config').addEventListener('click', async () => {
  const file1 = document.getElementById('ppFile').value.trim();
  const file2 = document.getElementById('ORFile').value.trim();

  const a = parseFloat(document.getElementById('add_weight').value);
  const b = parseFloat(document.getElementById('remove_weight').value);
  const c = parseFloat(document.getElementById('reloc_weight').value);

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
