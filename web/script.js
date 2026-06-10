let isRunning = false;

async function loadConfig() {
    let config = await eel.get_config()();
    document.getElementById('watch-path').innerText = config.watch;
    document.getElementById('target-path').innerText = config.target;
    
    isRunning = await eel.is_watcher_running()();
    updateUI();
}

async function selectFolder() {
    if (isRunning) {
        alert("Please stop the watcher before changing the target folder.");
        return;
    }
    let newFolder = await eel.select_target_folder()();
    if (newFolder) {
        document.getElementById('target-path').innerText = newFolder;
    }
}

async function toggleWatcher() {
    isRunning = await eel.toggle_watcher()();
    updateUI();
}

function exitApp() {
    eel.exit_app()();
    window.close();
}

function updateUI() {
    const btn = document.getElementById('toggle-btn');
    const dot = document.getElementById('status-dot');
    
    if (isRunning) {
        btn.innerText = "Stop Watcher";
        btn.classList.add("stop");
        dot.classList.add("active");
    } else {
        btn.innerText = "Start Watcher";
        btn.classList.remove("stop");
        dot.classList.remove("active");
    }
}

window.onload = loadConfig;
