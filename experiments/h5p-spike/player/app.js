const XAPI_OBJECT_IRI = 'https://studentconnect.local/h5p/truefalse-oslo-001';

function cloneStatement(statement) {
  return JSON.parse(JSON.stringify(statement));
}

function statementSummary(statement) {
  const verbId = statement?.verb?.id ?? '';
  const verb = statement?.verb?.display?.['en-US']
    ?? statement?.verb?.display?.en
    ?? verbId.split('/').pop()
    ?? 'inconnu';
  const score = statement?.result?.score;
  const scoreText = score && Number.isFinite(score.raw) && Number.isFinite(score.max)
    ? `${score.raw}/${score.max}`
    : 'non fourni';
  return {
    verb,
    verbId,
    objectId: statement?.object?.id ?? 'non fourni',
    score: scoreText,
    success: statement?.result?.success ?? 'non fourni',
    completion: statement?.result?.completion ?? 'non fourni',
    timestamp: statement?.timestamp ?? 'non fourni',
  };
}

function downloadJson(statement) {
  const blob = new Blob(
    [`${JSON.stringify(statement, null, 2)}\n`],
    { type: 'application/json' },
  );
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'studentconnect-h5p-xapi-statement.json';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

document.addEventListener('DOMContentLoaded', async () => {
  const status = document.getElementById('status');
  const container = document.getElementById('h5p-container');
  const eventCount = document.getElementById('xapi-event-count');
  const eventStatus = document.getElementById('xapi-status');
  const summary = document.getElementById('xapi-summary');
  const output = document.getElementById('xapi-output');
  const downloadButton = document.getElementById('xapi-download');
  let lastStatement = null;
  let count = 0;

  downloadButton.addEventListener('click', () => {
    if (lastStatement) {
      downloadJson(lastStatement);
    }
  });

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
      xAPIObjectIRI: XAPI_OBJECT_IRI,
    };

    await new H5PStandalone.H5P(container, options);

    if (!globalThis.H5P?.externalDispatcher) {
      throw new Error('H5P.externalDispatcher est indisponible après initialisation.');
    }

    globalThis.H5P.externalDispatcher.on('xAPI', (event) => {
      const statement = event?.data?.statement;
      if (!statement) {
        console.warn('Événement xAPI sans statement', event);
        return;
      }

      lastStatement = cloneStatement(statement);
      count += 1;
      const details = statementSummary(lastStatement);
      eventCount.textContent = String(count);
      eventStatus.textContent = `Dernier verbe : ${details.verb}`;
      summary.textContent = [
        `Verbe : ${details.verb}`,
        `Objet : ${details.objectId}`,
        `Score : ${details.score}`,
        `Succès : ${details.success}`,
        `Complétion : ${details.completion}`,
        `Horodatage : ${details.timestamp}`,
      ].join(' | ');
      output.textContent = JSON.stringify(lastStatement, null, 2);
      downloadButton.disabled = false;
      console.log('StudentConnect xAPI statement', lastStatement);
    });

    status.textContent = 'Lecteur initialisé et écouteur xAPI actif.';
    status.dataset.state = 'ready';
    eventStatus.textContent = 'En attente d’une interaction réelle.';
  } catch (error) {
    console.error('H5P standalone initialization failed', error);
    status.textContent = `Échec : ${error instanceof Error ? error.message : String(error)}`;
    status.dataset.state = 'error';
    eventStatus.textContent = 'Écouteur xAPI indisponible.';
  }
});
