[app]
title = Pong Quadra
package.name = pongquadra
package.domain = org.gabriel
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
version = 1.0
requirements = python3==3.11.6,pygame
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.accept_sdk_license = True
android.api = 33
android.minapi = 24
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1
