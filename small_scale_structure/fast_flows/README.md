# Fast Tail Flows

This folder contains inputs for performing very high resolution simulations
with the goal of producing localized fast flows in the tail.

## Code Config
```
git clone git@github.com:SWMFsoftware/SWMF.git

./Config.pl -install=BATSRUS,RCM2,Ridley_serial -compiler=[YOUR CHOICE]
./Config.pl -v=GM/BATSRUS,IE/Ridley_serial,IM/RCM2
./Config.pl -o=IE:g=181,361
```