const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');

if (fileInput && fileList) {
  fileInput.addEventListener('change', function () {
    fileList.innerHTML = '';
    const files = Array.from(fileInput.files).filter(file => file.name.endsWith('.xml'));

    if (files.length === 0) {
      fileList.innerHTML = '<li>XMLファイルが選択されていません。</li>';
      return;
    }

    files.forEach(file => {
      const li = document.createElement('li');
      li.textContent = file.webkitRelativePath || file.name;
      fileList.appendChild(li);
    });
  });
}
