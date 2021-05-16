###  Automatic recall miner for Excelsior shard.
###  Uses TheWarDoctor95's repository's (https://github.com/TheWarDoctor95/razor-enhanced)
###
###  Needs:  Shovel, resource bag, runebooks, metal workers keys
###  You'll need to enter the serials for the resource bag, the runebooks, your forge runebook, and the forge itself
###  You may need to adjust warehouse script location if you use a different name
###

# Parametri
from Scripts.glossary.items.ores import ores
from Scripts.glossary.colors import colors
from Scripts import config
import sys

# Variabili utente
RuneBookOre1 = 0x42047AEC           # Runebook for ore 1
RuneBookOre2 = 0x40B8A578           # Runebook for ore 2
## RuneBookOre3 = 0x00000000           # Runebook for ore 3
RuneBookForge = 0x42047AEC          # Runebook that has a forge nearby
forgerune = 16                      # What number is the rune with forge? First position is 1, last position is 16
ResourceBag = 0x40767E70            # Serial for the resource bag 
forge = 0x40730585                  # Serial of the forge at your rune
warehouseScript = 'warehouse.py'    # avm83's UOEX warehouser

# Variabili Sistema
runecounter = 1
gumpcount = 5
onloop = False
RecallPause = 3000 

def GetStarted( ):
    #
    # This function goes to the first rune in your first book
    # (It's separate from the "next spot" function because the counter works a bit differently the first time)
    #
    Gumps.ResetGump()
    Items.UseItem(RuneBookOre1)
    Gumps.WaitForGump(1431013363, 3000)
    Gumps.SendAction(1431013363, gumpcount )
    Misc.Pause(RecallPause)
    Misc.Pause(2000)
    Mine()
    
def RecallNextSpot( ):
    # 
    # When called, it recalls to the next rune on the list and advances the counter by 1
    # If you don't have exactly 2 runebooks, you can adjust here.
    #
    global runecounter
    global gumpcount
    gumpcount = gumpcount + 10
    if gumpcount > 155:
        gumpcount = 5
    runecounter = runecounter + 1
    Gumps.ResetGump()

#   For 1 runebook
#    if runecounter >= 17:
#        Smelt()

#   For 2 runebooks
    if runecounter >= 33:
        Smelt()

#   For 3 runebooks
#    if runecounter >= 49:
#        Smelt()

    Player.HeadMessage(77, "Moving to spot No. %i." % runecounter) 
    if runecounter <= 16:
        Items.UseItem(RuneBookOre1)
        Gumps.WaitForGump(1431013363, 3000)
        Gumps.SendAction(1431013363, gumpcount )
        Misc.Pause(RecallPause)
   
#   Comment out the next 5 lines if you only have one book (or if you have more than 2)
    if runecounter > 16:
        Items.UseItem(RuneBookOre2)
        Gumps.WaitForGump(1431013363, 3000)
        Gumps.SendAction(1431013363, gumpcount )
        Misc.Pause(RecallPause)

#   If you have 3 runebooks, use these lines instead
#    if runecounter > 16 and <= 32 :
#        Items.UseItem(RuneBookOre2)
#        Gumps.WaitForGump(1431013363, 3000)
#        Gumps.SendAction(1431013363, gumpcount )
#        Misc.Pause(RecallPause)
#    if runecounter > 32:
#        Items.UseItem(RuneBookOre3)
#        Gumps.WaitForGump(1431013363, 3000)
#        Gumps.SendAction(1431013363, gumpcount )
#        Misc.Pause(RecallPause)
    Misc.Pause(2000)
    Mine()
        
def Mount():
    Misc.Pause( 700 )
    mountSerial = Misc.ReadSharedValue( 'mount' )
    if mountSerial != None:
        mount = Mobiles.FindBySerial( Misc.ReadSharedValue( 'mount' ) )
        if mount != None:
            Mobiles.UseMobile( mount )
        
def Mine():
    global useMount
    
    mount = None
    mountSerial = None

    tileinfo = Statics.GetStaticsTileInfo(Player.Position.X, Player.Position.Y - 1, Player.Map)
    for tile in tileinfo:
        targetz = tile.StaticZ
        targetgfx = tile.StaticID
    # Misc.SendMessage('Target X: %i - Y: %i - Z: %i - gfx: %i' % (Player.Position.X, Player.Position.Y - 1, targetz, targetgfx), 77)
    
    if Player.Mount != None:
        # We need to dismount to be able to mine
        Mobiles.UseMobile( Player.Serial )
        Misc.Pause( 1000 )
    Journal.Clear()
    while ( not Journal.SearchByName( 'There is no metal here to mine.', 'System' ) and
            not Journal.SearchByName( 'Target cannot be seen.', 'System' ) and
            not Journal.SearchByName( 'You can\'t mine there.', 'System' ) ):
        if Player.Weight <= 400:
            shovel = FindItem( 0x0F39, Player.Backpack )
            if shovel == None:
                Player.HeadMessage(77, 'You\'re out of shovels!' )
                End()

            Items.UseItem( shovel )
            Target.WaitForTarget(10000, False)
            Target.TargetExecute(Player.Position.X, Player.Position.Y - 1 ,targetz, targetgfx)

            Misc.Pause( 500 )
            if Journal.SearchByType( 'Target cannot be seen.', 'Regular' ):
                Player.HeadMessage(77, 'Bad rune, moving on.' )
                Journal.Clear()
                break
        else:
            Misc.SendMessage('Overweight, moving ore.', 77)
            Organize()

        # Wait a little bit so that the while loop does not consume as much CPU
        Misc.Pause( 1000 )
    Player.HeadMessage(77, 'Out of ore.' )
    Misc.Pause(1000)
    RecallNextSpot()

def Organize():
    for ore in ores:
        oreStack = Items.FindByID( ores[ ore ].itemID, -1, Player.Backpack.Serial )
        while oreStack != None:
            Items.Move(oreStack, ResourceBag, 0)
            Misc.Pause( config.dragDelayMilliseconds )
            oreStack = Items.FindByID( ores[ ore ].itemID, -1, Player.Backpack.Serial )
    
def End():
    Player.HeadMessage(77, "Shutting down and thanks for all the fish")
    sys.Exit()
    
def Smelt():
    rune = 5
    count = forgerune
    while count > 1 :
        rune = rune+10
        count = count-1
    Player.HeadMessage(77, "Done! To the forge!")
    Gumps.ResetGump()
    Items.UseItem(RuneBookForge)
    Gumps.WaitForGump(1431013363, 3000)
    Gumps.SendAction(1431013363, rune )
    Misc.Pause(RecallPause)
    Misc.Pause(2000)
    
    for ore in ores:
        oreStack = Items.FindByID( ores[ ore ].itemID, -1, ResourceBag )
        while oreStack != None:
            Items.UseItem(oreStack)
            Target.WaitForTarget(10000, False)
            Target.TargetExecute(forge)
            oreStack = Items.FindByID( ores[ ore ].itemID, -1, Player.Backpack.Serial )
            Misc.Pause(1000)
    Misc.ScriptRun( warehouseScript )
    End()
    
    
Player.HeadMessage(77, 'It\'s digging time')     
GetStarted() 
#Smelt()

