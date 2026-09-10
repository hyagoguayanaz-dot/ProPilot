[app]

# (str) Title of your application
title = Pro Pilot

# (str) Package name
package.name = propilot

# (str) Package domain (needed for full package name)
package.domain = org.guayanaz

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,data/*

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,md,ico
source.exclude_dirs = tests, bin, venv, .git, .buildozer, __pycache__

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_patterns = license,images/*,docs/*

# (str) Application versioning (method 1)
version = 2.0

# (str) Application versioning (method 2)
#version.regex = __version__ = ['"](.*)['"]
#version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.11.8,kivy==2.3.0,kivymd==2.0.0,Pillow

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/logo.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of sensor, sensorLandscape, portrait, sensorPortrait, landscape, sensor, fullSensor, etc.)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version of python used by the app
osx.python_version = 3

# Kivy version to use
osx.kivy_version = 1.9.1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB
#android.presplash_color = #FFFFFF

# (string) Presplash animation using Lottie format.
# see https://lottiefiles.com/ for examples and https://airbnb.design/lottie/
# for general documentation.
# Lottie files can be created using various tools, like Adobe After Effect or Synfig.
#android.presplash_lottie = %(source.dir)s/assets/lottie.json

# (str) Adaptive icon of the application (used if Android API level is 26+ at runtime)
#android.icon_adaptive_foreground.filename = %(source.dir)s/assets/icon_fg.png
#android.icon_adaptive_background.filename = %(source.dir)s/assets/icon_bg.png

# (list) Permissions
android.permissions = INTERNET

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the android/app directory)
#android.library_references =
#android.uses_libraries =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android logcat pid only ( -c is additional logcat params)
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args =

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#android.port =

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) ANT directory
#android.ant_path =

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)
#android.skip_update = False

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)
android.accept_sdk_license_agreements = True

# (str) If you need to have a backup copy of the previous .apk, override with custom value, empty means no backup
#android.apk_backup = %(source.dir)s/backup.apk

# (str) If you need to have particular Java SDK (htps://adoptium.net), override with custom value
#android.java_sdk_path =

# (str) Specify an alternate Android NDK version
#android.ndk = 19b

# (bool) Use --private-data-dir flag with adb. (Android's --private-data-dir option is used to specify
# where the app's private data is stored. The --private-data-dir is needed for Android 5.0+)
#android.private_data_dir = True

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#android.port =

# (str) If you want to use a specific branch of python-for-android, give its git URL here
#p4a.url =

# (str) If you want to use a specific fork of python-for-android, give its git URL here
#p4a.fork = kivy

# (str) Specific branch you want to use. If not specified, will use the bootstrap's default branch
#p4a.branch = master

# (str) SSL CA key if you want to use specific one
#p4a.ssl_ca_key =

# (list) python-for-android whitelist
#android.whitelist =

# (bool) If you want to enable Android copy libs
#android.copy_libs = False

# (str) If you want to specify a local python-for-android to use
#p4a.local_recipes =

# (list) --blacklist an android requirement, it will be ignored when searching for recipes
# example: you want to blacklist android's copy of sqlite3 so you use the python one.
#android.blacklist =

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)
#android.skip_update = False

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)

# (str) The Android arch to build for. Valid values are armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#android.port =

# (str) Extra P4A arguments e.g. '--enable-androidx --debug-allowed'
#p4a.extra_args =


#
# Python for android (p4a) specific
#

# (str) python-for-android URL to use for checkout
#p4a.url =

# (str) python-for-android fork to use in case you want to use a specific fork
#p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android specific commit to use (if specified, will override branch/fork)
#p4a.commit = HEAD

# (str) python-for-android git clone directory (if empty, will be automatically created)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (list) python-for-android whitelist - (if not specified, will use the default)
#android.whitelist =

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)
#android.skip_update = False

# (bool) If True, then skip trying to update the Android ant, sdk, platfrom
# tools (and all other dependant tools)

# (str) Bintray repository to use for downloading android packages
#android.bintray_uses_ssl = False

# (str) If you want to use specific version of python-for-android, specify it here
#p4a.bootstrap = sdl2

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
#ios.kivy_ios_url = https://github.com/kivy/kivy-ios
#ios.kivy_ios_branch = master

# Another platform dependency: ios-specific
#ios.platform.ios_dir =

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: security find-identity -p codesigning
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) The development team to use for iOS deployment
#ios.codesign.development_team.debug = <hexstring>

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(app_title)s

# (str) The development team to use for iOS deployment
#ios.codesign.development_team.release = <hexstring>


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
warn_on_root = 0

# (int) Display warning if buildozer is detected as running from android inside msi
#warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be translated into:
#
#[app:source.exclude_patterns]
#license
#data/audio/*.wav
#data/images/original/*
#


#    -----------------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a demo version of your application without
#    HD content. You could first change the title to add "(demo)" in the name
#    and extend the excluded directories to remove the HD content.
#
#[app@demo]
#title = My Application (demo)
#
#[app:source.exclude_patterns@demo]
#images/hd/*
#
#    Then, invoke the command line with the "demo" profile:
#
#buildozer --profile demo android debug
