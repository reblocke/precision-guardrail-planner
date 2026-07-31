# Privacy

## Data flow

Input is read by the page, sent through `postMessage` to a same-origin Web Worker, processed by
Python in Pyodide, and returned to the page for display/export. Inputs and results exist only in
page and worker memory until the page closes or the worker restarts.

The app has:

- no backend or database;
- no telemetry, analytics, or beacons;
- no local/session storage;
- no input values in URL queries or fragments;
- no cookies;
- no application logging of inputs or protected health information;
- no hidden persistence, upload, or sharing path.

Static requests fetch HTML, CSS, JavaScript, Plotly, Pyodide, and hashed local Python files. User
values are not included in request URLs, headers, or bodies. CDN operators can observe ordinary
network metadata such as IP address and requested static asset, but not values entered into this
app.

## Inputs and examples

Study/scenario parameters could be sensitive in context, so tests use synthetic values and
browser privacy checks search network traffic for distinctive entered values. The app does not
request person identifiers or patient-level rows.

## Exports

CSV and PNG files are created locally after an explicit button press. Clipboard writes occur only
after a copy button press. Browser/operating-system download and clipboard behavior determines
where those outputs go; the app does not upload or retain them.

Any future proposal for storage, server processing, analytics, sharing, or upload must stop for a
new documented review of data path, retention, access, security, and compliance.

Public issues and pull requests must not contain protected health information, patient-level data,
credentials, restricted material, sensitive input values, or unredacted local logs. Report a
privacy or security defect through the private process in [SECURITY.md](../SECURITY.md), using only
the smallest synthetic reproduction needed.
