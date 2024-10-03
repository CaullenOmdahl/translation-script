# run_all.ps1

# Enable script execution if not already enabled
# You might need to run PowerShell as Administrator to change execution policy
# Uncomment the following line if you encounter execution policy issues
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Define directories
$scriptsDir = "scripts"
$videosDir = "Videos to Transcode"
$outputDir = "Output"
$venvDir = "venv"

# Function to display error and exit
function Show-ErrorAndExit {
    param (
        [string]$Message
    )
    Write-Error $Message
    Read-Host -Prompt "Press Enter to exit"
    exit 1
}

# Step 1: Create Virtual Environment if it doesn't exist
if (-Not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Show-ErrorAndExit "Failed to create virtual environment."
    }
    Write-Host "Virtual environment created successfully."
} else {
    Write-Host "Virtual environment already exists."
}

# Step 2: Activate Virtual Environment
Write-Host "Activating virtual environment..."
try {
    & "$venvDir\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated."
} catch {
    Show-ErrorAndExit "Failed to activate virtual environment."
}

# Step 3: Check if setup_environment.py exists
if (-Not (Test-Path "$scriptsDir\setup_environment.py")) {
    Write-Host "setup_environment.py not found in $scriptsDir."
    Write-Host "Attempting to clone scripts from GitHub repository..."
    git clone https://github.com/CaullenOmdahl/translation-script.git $scriptsDir
    if ($LASTEXITCODE -ne 0) {
        Show-ErrorAndExit "Failed to clone scripts from GitHub. Please ensure Git is installed and the repository URL is correct."
    }
    Write-Host "Scripts cloned successfully."
} else {
    Write-Host "setup_environment.py found in $scriptsDir."
}

# Step 4: Run setup_environment.py
Write-Host "Running setup_environment.py to install dependencies and create directories..."
python "$scriptsDir\setup_environment.py"
if ($LASTEXITCODE -ne 0) {
    Show-ErrorAndExit "Environment setup failed. Exiting."
}
Write-Host "Environment setup completed."

# Step 5: List available videos
Write-Host "`nAvailable Videos in '$videosDir':"
$videos = Get-ChildItem -Path $videosDir -Filter *.mp4
if ($videos.Count -eq 0) {
    Show-ErrorAndExit "No video files found in '$videosDir'. Please add videos to transcode."
}
for ($i = 0; $i -lt $videos.Count; $i++) {
    Write-Host "$($i + 1): $($videos[$i].Name)"
}
Write-Host

# Step 6: Prompt user to select a video by number
$videoNumber = Read-Host "Enter the number of the video file to translate"

if (-Not ($videoNumber -match '^\d+$') -or $videoNumber -lt 1 -or $videoNumber -gt $videos.Count) {
    Show-ErrorAndExit "Invalid selection. Please run the script again and enter a valid number."
}

$selectedVideo = $videos[$videoNumber - 1].Name
Write-Host "You selected: $selectedVideo"

# Step 7: Prompt for source language
$sourceLang = Read-Host "Enter the source language code (e.g., vi)"

# Step 8: Prompt for target languages by number
# Define a list of common language codes
$commonLangs = @(
    "en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi", "bn", "pa", "ur"
)

Write-Host "`nAvailable Target Languages:"
for ($i = 0; $i -lt $commonLangs.Count; $i++) {
    Write-Host "$($i + 1): $($commonLangs[$i])"
}
Write-Host "Enter the numbers of the target languages separated by space (e.g., 1 3 5):"
$targetLangNumbers = Read-Host

# Parse target language numbers
$targetLangIndices = $targetLangNumbers -split '\s+' | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ }

# Validate target language numbers
$validIndices = $targetLangIndices | Where-Object { $_ -ge 1 -and $_ -le $commonLangs.Count }
if ($validIndices.Count -ne $targetLangIndices.Count) {
    Show-ErrorAndExit "One or more invalid target language numbers entered. Please run the script again and enter valid numbers."
}

# Get target language codes
$targetLangs = $validIndices | ForEach-Object { $commonLangs[$_ - 1] }

Write-Host "Selected Target Languages: $($targetLangs -join ', ')"

# Step 9: Prompt for model size
Write-Host "`nSelect the Whisper model size to use:"
$whisperModels = @("tiny", "base", "small", "medium", "large")
for ($i = 0; $i -lt $whisperModels.Count; $i++) {
    Write-Host "$($i + 1): $($whisperModels[$i])"
}
Write-Host "Press Enter to accept the default ('base')."

$modelSizeInput = Read-Host "Enter the number corresponding to the Whisper model size"

if ($modelSizeInput -match '^\d+$' -and $modelSizeInput -ge 1 -and $modelSizeInput -le $whisperModels.Count) {
    $modelSize = $whisperModels[$modelSizeInput - 1]
} elseif ($modelSizeInput -eq "") {
    $modelSize = "base"
} else {
    Show-ErrorAndExit "Invalid model size selection. Please run the script again."
}

Write-Host "Selected Whisper model size: $modelSize"

# Step 10: Copy video to output directory (before processing)
$videoName = [System.IO.Path]::GetFileNameWithoutExtension($selectedVideo)
$videoOutputDir = Join-Path $outputDir $videoName
if (-Not (Test-Path $videoOutputDir)) {
    New-Item -Path $videoOutputDir -ItemType Directory | Out-Null
    Write-Host "Created output directory at '$videoOutputDir'"
} else {
    Write-Host "Output directory already exists at '$videoOutputDir'"
}

Write-Host "Copying video to output directory..."
Copy-Item -Path (Join-Path $videosDir $selectedVideo) -Destination $videoOutputDir
if ($LASTEXITCODE -ne 0) {
    Show-ErrorAndExit "Failed to copy video file. Exiting."
}
Write-Host "Video copied successfully to '$videoOutputDir'."

# Initialize flag to determine processing success
$processingSuccess = $true

# Step 11: Iterate over target languages
foreach ($lang in $targetLangs) {
    Write-Host "`nProcessing target language: $lang"
    
    # Step 11a: Download and export model
    Write-Host "Downloading and exporting model for '$lang'..."
    python "$scriptsDir\download_export_model.py" "Helsinki-NLP/opus-mt-$sourceLang-$lang" "$videoOutputDir\models\opus-mt-$sourceLang-$lang" "text2text-generation"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to download/export model for '$lang'. Exiting."
        $processingSuccess = $false
        break
    }
    Write-Host "Model for '$lang' downloaded and exported successfully."
    
    # Step 11b: Load model
    Write-Host "Loading model for '$lang'..."
    python "$scriptsDir\load_model.py" "$videoOutputDir\models\opus-mt-$sourceLang-$lang"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to load model for '$lang'. Exiting."
        $processingSuccess = $false
        break
    }
    Write-Host "Model for '$lang' loaded successfully."
    
    # Step 11c: Transcribe audio (only once)
    if ($lang -eq $targetLangs[0]) {
        Write-Host "Transcribing audio from video..."
        python "$scriptsDir\transcribe_audio.py" "$videoOutputDir\$selectedVideo" "$sourceLang" "$videoOutputDir\cache\transcript_cache.json" --model-size "$modelSize"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Audio transcription failed. Exiting."
            $processingSuccess = $false
            break
        }
        Write-Host "Audio transcription completed successfully."
    }
    
    # Step 11d: Translate text
    Write-Host "Translating text to '$lang'..."
    python "$scriptsDir\translate_text.py" "$videoOutputDir\cache\transcript_cache.json" "$videoOutputDir\models\opus-mt-$sourceLang-$lang" "$lang" "$videoOutputDir\cache\translation_cache_$lang.json" n
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Text translation failed for '$lang'. Exiting."
        $processingSuccess = $false
        break
    }
    Write-Host "Text translation for '$lang' completed successfully."
    
    # Step 11e: Create subtitles
    Write-Host "Creating subtitles for '$lang'..."
    python "$scriptsDir\create_subtitles.py" "$videoOutputDir\cache\translation_cache_$lang.json" "$videoOutputDir\cache\transcript_cache.json" "$videoOutputDir"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Subtitle creation failed for '$lang'. Exiting."
        $processingSuccess = $false
        break
    }
    Write-Host "Subtitles for '$lang' created successfully."
    
    # Step 11f: Rename SRT files to match VLC naming convention
    Write-Host "Renaming subtitle files for VLC compatibility..."
    Rename-Item -Path "$videoOutputDir\subtitles.srt" -NewName "subtitles_$lang.srt" -ErrorAction SilentlyContinue
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to rename subtitle file for '$lang'. Exiting."
        $processingSuccess = $false
        break
    }
    Write-Host "Subtitle file renamed to 'subtitles_$lang.srt' successfully."
}

# Step 12: Move video file if processing was successful
if ($processingSuccess) {
    Write-Host "`nAll processing steps completed successfully. Deleting original video from '$videosDir'..."
    Remove-Item -Path (Join-Path $videosDir $selectedVideo) -Force
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to delete the original video file from '$videosDir'. Please delete it manually."
    } else {
        Write-Host "Original video file deleted from '$videosDir'."
    }
} else {
    Write-Host "`nProcessing failed. Video file remains in '$videosDir'."
}

Write-Host "`nAll subtitles have been generated and placed in '$videoOutputDir'."
Write-Host "Process completed successfully."
Read-Host -Prompt "Press Enter to exit"
