# Waveshare ESP32 e-ink driver code

I recently bought a [Waveshare ESP32 e-ink driver
board](https://www.waveshare.com/wiki/E-Paper_ESP32_Driver_Board). Its usability is
terrible, but it works, and I want to make stuff with it, so I have to figure out what
the hell is going on with it.

Docs kinda-sorta exist, but they're inscrutable, so I found myself having to
reverse-engineer a lot of the stuff. Unfortunately, I wasn't able to convert the
driver software they provide to give a single endpoint that you can POST an image to,
and I have to resort to hundreds of POST in rapid succession, but if I can at least
figure out how to show some stuff, that's fine.

I made some changes to the software that Waveshare posts (in a zip, no less) on the link
above. The changes are detailed here:

* I added Tzapu's WiFiManager, so you don't have to hardcode WiFi credentials any more.

I also wrote some software for sending images to the display.

# LICENSE

I have no idea what the license is. The ESP32 code is all Waveshare's, with two or three
lines of mine, and there was no license in their zip file, so I assume all rights are
reserved by Waveshare themselves.
