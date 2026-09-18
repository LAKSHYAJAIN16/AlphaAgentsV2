/**
 * Electron main process.
 *
 * Spawns the Python backend (backend/api.py, a FastAPI app) automatically on
 * startup so the user never runs a Python command by hand — this is the
 * whole point of the desktop app. The renderer talks to it over plain HTTP
 * on localhost; no IPC bridge is needed since it's just a same-machine
 * network call.
 */
const { app, BrowserWindow } = require("electron");
const path = require("node:path");
const { spawn } = require("node:child_process");

const BACKEND_PORT = 8765;
const REPO_ROOT = path.join(__dirname, "..", ".."); // frontend/electron -> frontend -> repo root

let backendProcess = null;
let mainWindow = null;

function startBackend() {
  const pythonBin = process.platform === "win32" ? "python" : "python3";
  backendProcess = spawn(
    pythonBin,
    ["-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1", "--port", String(BACKEND_PORT)],
    { cwd: REPO_ROOT, stdio: "inherit" }
  );
  backendProcess.on("error", (err) => {
    console.error("Failed to start Python backend (is `python` on PATH?):", err);
  });
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 880,
    minWidth: 980,
    minHeight: 640,
    backgroundColor: "#0a0b0d",
    autoHideMenuBar: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const devServerUrl = process.env.VITE_DEV_SERVER_URL;
  if (devServerUrl) {
    mainWindow.loadURL(devServerUrl);
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "dist", "index.html"));
  }
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
});

app.on("window-all-closed", () => {
  stopBackend();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", stopBackend);
