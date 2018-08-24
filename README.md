# gear-vr-controller-linux

This little mapper creates a mouse + web navigator device from Samsung Gear VR Controller.
My work was inspired by this project
https://github.com/jsyang/gearvr-controller-webbluetooth

# How To use?
1. Change the bluetooth MAC address in the .py file to yours!!!
2. Pair Controller with (Linux) PC
3. Connect Controller
4. As root load uinput: # modprobe uinput
5. As root enable user access to uinput: # chmod 666 /dev/uinput
6. Run my program
7. Enjoy

To avoid steps 4 and 5:

As root do this once, a change YOURGROUP to the group of your user

echo 'KERNEL=="uinput", MODE="0660", GROUP="YOURGROUP", OPTIONS+="static_node=uinput"' > /etc/udev/rules.d/99-uinput.rules


# What's the usecase? a.k.a. Why?

I am sitting at my desk while holding my litte son while he sleeps, but I sill need do nerdy stuff like browsing the web. An air mouse is not that convenient, but this controller ... is a perfect match. 
It could be considered as the one hand equivalent of the Steam Controller.
BTW I hope sc-controller will intergate this controller in his project as well.

# ISSUES
Consider this project at this point as a Proof Of Concept.
