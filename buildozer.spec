[app]

# Application title
title = Guns and Boots

# Package name
package.name = gunsandboots
package.domain = com.gunsandboots

# Source code directory
source.dir = .
source.include_exts = py,png,jpg,jpeg,gif,json,txt

# Version information
version = 1.0.0
version.code = 1

# Requirements for Python and libraries
requirements = python3,pygame

# Android specific configuration
android.api = 33
android.minapi = 25
android.ndk = 25b
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Orientation
orientation = landscape

# Copy required libraries
copy-libs = 1

# P4A (Python for Android) requirements
p4a.requirements = python3,pygame
p4a.skip_update = False

# Gradle build configuration
android.gradle_dependencies = 
android.add_src = 

# Keystore configuration (optional - for production release)
# android.keystore = 1
# android.keystore_path = /path/to/keystore
# android.keystore_alias = my-key-alias
# android.keystore_passphrase = keystore-password

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
warn_on_root = 1

# Build directories for CI/CD environments
android.build_dir = .buildozer/android/platform/build

