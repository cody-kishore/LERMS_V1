[app]

# ─────────────────────────────────────────────────────────────────────────────
# App identity
# ─────────────────────────────────────────────────────────────────────────────
title = LERMS
package.name = lerms
package.domain = org.lerms

# Source directory (relative to this spec file)
source.dir = .

# Comma-separated list of source files to include
source.include_exts = py,png,jpg,kv,atlas,html,css,js

# Include the assets folder
source.include_patterns = assets/*

# Application version
version = 1.0.0

# Main entry point
source.main = main.py


# ─────────────────────────────────────────────────────────────────────────────
# Requirements
# ─────────────────────────────────────────────────────────────────────────────
# Add kivymd to requirements; Buildozer resolves kivy as a dependency of kivymd.
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow


# ─────────────────────────────────────────────────────────────────────────────
# Android-specific configuration
# ─────────────────────────────────────────────────────────────────────────────
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,ACCESS_WIFI_STATE,ACCESS_NETWORK_STATE

# Minimum and target SDK
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True

# Architecture — armeabi-v7a covers most Android devices
android.archs = armeabi-v7a, arm64-v8a

# Allow backup — set to False to keep user data private
android.allow_backup = False

# Orientation: portrait, landscape, or sensor
orientation = portrait

# Fullscreen: 0 = show status bar, 1 = fullscreen
fullscreen = 0

# App icon (place a 512x512 PNG at assets/icon.png)
# icon.filename = %(source.dir)s/assets/icon.png

# Presplash / loading screen
# presplash.filename = %(source.dir)s/assets/presplash.png
# presplash.color = #0D47A1


# ─────────────────────────────────────────────────────────────────────────────
# Build options
# ─────────────────────────────────────────────────────────────────────────────
[buildozer]

# Log level: 0 = error only, 1 = info, 2 = debug
log_level = 1

# Warn when building in debug mode
warn_on_root = 1

# Build output directory
# build_dir = ./.buildozer
# bin_dir   = ./bin
