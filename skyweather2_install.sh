# -------------------------------------------------------------------
# skyweather2_install.sh
#
# Install script for the SwitchDoc Labs SkyWeather2 system.
# Copyright 2021 sopwith@ismellsmoke.net
# License: Attribution-ShareAlike 4.0 International
#                 (CC BY-SA 4.0)
# https://creativecommons.org/licenses/by-sa/4.0/legalcode
#
# Latest supported SDL version: March 7, 2021 - Version 023
#
# Use this script at your own risk! No warranty of any kind provided.
#
# This is a Maker Community provided script. 
#    (Not affiliated with SwitchDoc Labs.)
# # 
# Contact information:
# http://www.ismellsmoke.net
# sopwith@ismellsmoke.net
#
# Version 1.0 - 2021-03-08
# -------------------------------------------------------------------
#! /bin/bash

# Script functions.
exit_error() {
    echo "====================================================================================="
    echo "--- This script did not complete successfully. Check error messages and edit script."
    echo "--- Error message: $1"
    echo "====================================================================================="
    exit 1
}

print_success() {
    echo "============================================="
    echo "|   Install script completed successfully.  |"
    echo "============================================="
    echo ""
    echo "Please reboot the Pi to enable the new settings."
    exit 0
}

echo "============================================="
echo "|        Installing required apps.          |"
echo "============================================="

cd /home/pi
for APP in $(cat apps.txt)
do
    echo ""
    echo "Installing $APP..."
    sudo apt install -y $APP
    if [ $? -ne 0 ]; then
        exit_error "--- Error installing $APP."
    else
        echo "+++ $APP successfully installed."
    fi
    echo ""
done

echo "============================================="
echo "|      Installing required modules.         |"
echo "============================================="

cd /home/pi
for MOD in $(cat modules.txt)
do
    echo ""
    echo "Installing $MOD..."
    sudo pip3 install $MOD
    if [ $? -ne 0 ]; then
        exit_error "--- Error installing $MOD."
    else
        echo "+++ $MOD successfully installed."
    fi
    echo ""
done

echo "============================================="
echo "|         Installing software.              |"
echo "============================================="
echo

echo "Installing rtl-sdr..."
cd /home/pi
if [ -d "rtl-sdr" ]; then
    sudo mv rtl_sdr/ /tmp
fi
git clone git://git.osmocom.org/rtl-sdr.git
if [ $? -ne 0 ]; then
    exit_error "--- Error cloning rtl-sdr.git."
fi
cd rtl-sdr
mkdir build
cd build/
cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON
if [ $? -ne 0 ]; then
    exit_error "--- Error creating make file for rtl-sdr."
fi
make
if [ $? -ne 0 ]; then
    exit_error "--- Error compiling make file for rtl-sdr."
fi
sudo make install
if [ $? -ne 0 ]; then
    exit_error "--- Error installing rtl-sdr."
fi
sudo ldconfig
echo
echo

echo "Installing rtl-433..."
cd /home/pi
if [ -d "rtl_433" ]; then
    sudo mv rtl_433/ /tmp
fi
git clone https://github.com/switchdoclabs/rtl_433.git
if [ $? -ne 0 ]; then
    exit_error "--- Error cloning rtl-433.git."
fi
cd rtl_433/
mkdir build
cd build/
cmake ..
if [ $? -ne 0 ]; then
    exit_error "--- Error creating make file for rtl-433."
fi
make
if [ $? -ne 0 ]; then
    exit_error "--- Error compiling make file for rtl-433."
fi
sudo make install
if [ $? -ne 0 ]; then
    exit_error "--- Error installing rtl-433."
fi
sudo ldconfig

echo
echo
echo "Installing SkyWeather2..."
cd /home/pi
if [ -d "SDL_Pi_Skyweather2" ]; then
    sudo mv SDL_Pi_Skyweather2/ /tmp
fi
git clone https://github.com/switchdoclabs/SDL_Pi_Skyweather2.git
if [ $? -ne 0 ]; then
    exit_error "--- Error cloning SDL_Pi_Skyweather2.git."
fi

cd /home/pi
sudo chown -R pi:pi .

echo
echo
print_success

