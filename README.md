# gear-vr-controller-linux

This little mapper creates a mouse + web navigator device from Samsung Gear VR Controller.
My work was inspired by this project
https://github.com/jsyang/gearvr-controller-webbluetooth

# How To use?
1. $ pip3 install python-uinput pygatt gatt more-itertools --user
2. Change the bluetooth MAC address in the .py file to yours!!!
3. Pair Controller with (Linux) PC
4. Connect Controller
5. As root load uinput: # modprobe uinput
6. As root enable user access to uinput: # chmod 666 /dev/uinput
7. Run my program
8. Enjoy

To avoid steps 4 and 5:

As root do this once, a change YOURGROUP to the group of your user

echo 'KERNEL=="uinput", MODE="0660", GROUP="YOURGROUP", OPTIONS+="static_node=uinput"' > /etc/udev/rules.d/99-uinput.rules


# What's the usecase? a.k.a. Why?

I am sitting at my desk while holding my litte son while he sleeps, but I sill need do nerdy stuff like browsing the web. An air mouse is not that convenient, but this controller ... is a perfect match. 
It could be considered as the one hand equivalent of the Steam Controller.
BTW I hope sc-controller will intergate this controller in his project as well.

# ISSUES
Consider this project at this point as a Proof Of Concept.

# Plans for the future
I had the idea to implement the esp-GearVRController-Mouse-adapter, but I am stuck with it.
ESP32 https://www.espressif.com/en/products/hardware/esp32/overview was my best choice. Really good piece of hardware, but handling the 128bit uuid notification event stucks by waiting for a semaphore in the readValue() ...

NodeJS: as the original reverse engineering was done in Javascript and nodejs has mouse emulation libraries, this could work.

Android-GearVRController-Mouse-adapter:
https://github.com/rdady/BLE-HID-Peripheral-for-Android
An Android phone could pretend to be a BLE mouse / joystick.
Advantage is, no special hardware is needed and no special knowledge is needed for its programming, but installing an app.
I am working on this one, wait for it :)

