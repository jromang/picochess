General
=======
This folder is for the UCI-Engines. Place the engines in your corresponding plattform folder ("armv7l" or "x86_64")

The engines must be named after "char-max 6chars" for example "x-engnam". The first char decides the order
shown in the dgt display (the first 8 engines can also be activated with the queen). The last max 6 chars decides the
engine name inside the dgt-clock (for XL clocks these max 6chars - please keep this rule, even you have a DGT3000 clock).

If you update the engines list please run "./build-engines.py" after it to create a new engine cache file (engines.ini).


Personalities / Levels
======================
During the engine build (see above) the script will also build a level file for each engine (as long there isn't
such file already). These files are named after the engine with a ".lvl" at the end.

You can update them lateron by hand if you want but they should already be in good shape for standard engines (with level
support). If you do this please follow the standard level naming way with "Level@01" & "Elo@0123". The numbers must be
2chars or 4chars long and with this key-value-string (ending on "@") infront.
Actually, you can put any valid uci-command inside each section. The auto build just builds the old level support inside
this new system. So you can tweak each engine as you want (going towards personality engines). The startup parameters
(picochess.ini) are thereby used for all engines as standard (as long as they aren't overriden by each lvl file).


If you have a personality engine (like rodent_II) please use something similar to the "rodent2" folder.
I uploaded some personality_* files already. Please move them to the plattform-engine folder, and name them similar to
the engine like "m-rodent.lvl".
In case of rodent_II you must also make sure the engine is running in "SHOW_OPTIONS" mode.

If you have problems please don't hassitate to contact me over eMail or skype.

LocutusOfPenguin
