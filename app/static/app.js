// Calls the API and shows what it read from storage.
const status = document.getElementById("status");

try {
  const response = await fetch("/api/status");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const body = await response.json();
  status.textContent = `Storage: ${body.storage}, schema ${body.schema_version}`;
} catch (error) {
  status.textContent = `Storage error: ${error.message}`;
}
