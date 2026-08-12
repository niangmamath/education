document.addEventListener('DOMContentLoaded', async () => {
  const status = document.getElementById('status');
  const container = document.getElementById('h5p-container');

  try {
    const options = {
      h5pJsonPath: '/runtime/content',
      contentJsonPath: '/runtime/content/content',
      librariesPath: '/runtime/content',
      frameJs: '/runtime/player/frame.bundle.js',
      frameCss: '/runtime/player/styles/h5p.css',
      frame: true,
      copyright: true,
      export: false,
      embed: false,
      fullScreen: false,
      xAPIObjectIRI: 'https://studentconnect.local/h5p/truefalse-oslo-001',
    };

    await new H5PStandalone.H5P(container, options);
    status.textContent = 'Lecteur initialisé. Tester l’interaction et examiner la console.';
    status.dataset.state = 'ready';
  } catch (error) {
    console.error('H5P standalone initialization failed', error);
    status.textContent = `Échec : ${error instanceof Error ? error.message : String(error)}`;
    status.dataset.state = 'error';
  }
});
