# ATLUTD - Comparing points per Season


#---------------------------------------------------------------------------------------------------------------#
# Load Modules
#
#---------------------------------------------------------------------------------------------------------------#
import numpy as np
import pandas as pd
import requests                                                      # Retrieve data over the internet
import json                                                          # Interacts with json data
#from urllib.request import urlopen
from PIL import Image
from highlight_text import fig_text
from mplsoccer import Bumpy, FontManager, add_image                  # Soccer specific charts and graphs
import os                                                            # used to interact with the file system
import matplotlib.pyplot as plt                                      # Save the Chart as a jpg
import logging                                                       # Script logging
import sys
import itertools                                                     # used to provide iteration functions

#---------------------------------------------------------------------------------------------------------------#
# Class
#---------------------------------------------------------------------------------------------------------------#
class Chart():
    Colors = ""
    Team_Name = ""
    Data = ""
    Seasons = ""            # list of unique Years the team has played - note - records go back to 2012 currently
    Season_To_Date = {}     # Only the data for games based on the current season.  

    #---------------------------------------------------------------------------------------------------------------#
    # Function: __init__
    # Class Initialization
    #---------------------------------------------------------------------------------------------------------------#
    def __init__( self, Team ):
        self.Colors = ""
        self.Team_Name = Team

    #---------------------------------------------------------------------------------------------------------------#
    # Function: Load_Data
    # Loads the Data from the source, builds the data structures
    #---------------------------------------------------------------------------------------------------------------#
    def Load_Data( self ):
        #---------------------------------------------------------------------------------------------------------------#
        # Obtaining the data
        # data is coming from https://www.football-data.co.uk/usa.php
        # File location is at: https://www.football-data.co.uk/new/USA.csv
        #---------------------------------------------------------------------------------------------------------------#

        URL_Data = "https://www.football-data.co.uk/new/USA.csv"
        response = requests.get( URL_Data )
        #print(  os.path.dirname(__file__) + r"\data\football-data.co.uk\USA.csv" )
        open( os.path.dirname( __file__ ) + r"\data\football-data.co.uk\USA.csv", "wb" ).write( response.content )

        self.Data = pd.read_csv( os.path.dirname( __file__ ) + r"\data\football-data.co.uk\USA.csv" )

        # Outputting the data
        self.Data.head()

        # Create a list of unique Years
        self.Seasons = self.Data.Season.unique()
        #print( Seasons )

        # Make this into a Dictionary, each Season will have a list[0] of points associated
        self.Seasons = { str(Season) : [0] for Season in self.Seasons }
        #print( Seasons )

    #---------------------------------------------------------------------------------------------------------------#
    # Function: Load_Colors
    # Loads the provided json file and sets it as a file.  This will set it as the expected highlighting for the 
    # chart.  
    # Ex:
	#  {
    #   "2017": "#013474",
    #   "2018": "#6A1FA1"
    #  }
    #
    #---------------------------------------------------------------------------------------------------------------#
    def Load_Colors( self, File ):
        try:
            with open( File, "r", encoding="utf-8" ) as f:
                #self.Colors = json.load( f )
                self.Colors = json.loads( f.read() )

            #print( self.Colors )
        except Exception as e:
             print( "An error has occured while reading the Color data: " + str( e ) )

    #---------------------------------------------------------------------------------------------------------------#
    # Function: Generate_Internal_Data
    # Build the chart data for the Season as well as Season_To_Date
    #---------------------------------------------------------------------------------------------------------------#
    def Generate_Internal_Data( self ):
        # Loop through the data, adding into seach season.  Specifically for self.Team_Name
        for row in self.Data.itertuples():
            
            # will break this up later
            if ( self.Team_Name in row.Home ) or ( self.Team_Name in row.Away ):
                # Based on who won
                #print( row.Season )
                #print( Seasons[row.Season] )
                if ( row.Res == "H" ):
                        if ( self.Team_Name in row.Home ):
                            self.Seasons[str(row.Season)].append( self.Seasons[str(row.Season)][-1] +3 )  # Taking previous value, incrementing 3
                        if ( self.Team_Name in row.Away ):
                            self.Seasons[str(row.Season)].append( self.Seasons[str(row.Season)][-1] +0 )  # Taking previous value, incrementing 0
                if ( row.Res == "A" ):
                        if ( self.Team_Name in row.Home ):
                            self.Seasons[str(row.Season)].append( self.Seasons[str(row.Season)][-1] +0 )  # Taking previous value, incrementing 0
                        if ( self.Team_Name in row.Away ):
                            self.Seasons[str(row.Season)].append( self.Seasons[str(row.Season)][-1] +3 )  # Taking previous value, incrementing 3
                if ( row.Res == "D" ):
                        self.Seasons[str(row.Season)].append( self.Seasons[str(row.Season)][-1] +1 )      # Taking previous value, incrementing 1


        # Data Cleanup
        #  remove the first value from each season - it was only placed there to allow for calculations 
        # This also gives us a chance to capture the chart's y-axis
        TempCopy = self.Seasons.copy()
        for key, value in TempCopy.items():
            del self.Seasons[key][0]
            # Get the last entry of the current year, and see if it's the largest value
            #if ( len( TempCopy[key] )  ) > 0: 
                #print( self.Seasons[key] )
                #print( len( TempCopy[key] ) )
                #print( len( TempCopy[key] ) - 1 )
        
        List_Seasons = list( self.Seasons.keys() )
        List_Seasons.reverse() # Getting Current Season First
        Current_Season_Limit = len( self.Seasons[ List_Seasons[0] ] ) # Current Season's Dates - number of games

        # Iterate through each key/value pair in self.Seasons.  
        # If the length exceeds Current_Season_Limit, it creates a new key-value pair in self.Season_To_Date and copies appropriate data across
        self.Season_To_Date = {key: value if len(value) <= Current_Season_Limit else value[:Current_Season_Limit] for key, value in self.Seasons.items()}

        
        # Verifying the data cleanup has worked
        #print( "#---------------------------------------------------------------------------------------------------------------#")
        #print( self.Seasons )
        #print( "Season_To_Date" )
        #print( self.Season_To_Date )
        #print( "#---------------------------------------------------------------------------------------------------------------#")


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Chart_Season
    # Chart the Full Season
    #---------------------------------------------------------------------------------------------------------------#
    def Chart_Season( self ):
        # Prepare for the Graph
        # Loading Fonts

        print() 
        print( "Chart_Season" )
        self.Seasons = self.Remove_Empty_Lists( self.Seasons )
        #print( self.Seasons )

        Chart = self.Generate_Chart( self.Seasons, False )
        Chart.savefig( os.path.dirname(__file__) + r"\chart\\" + self.Team_Name + "-Entire_Season.jpg", dpi=300, bbox_inches='tight')


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Chart_Season_to_Date
    # Chart the data up to the last played date ( as provided by the supplied data )
    #---------------------------------------------------------------------------------------------------------------#
    def Chart_Season_to_Date( self ):
        # Prepare for the Graph
        # Loading Fonts

        print() 
        print( "Chart_Season_to_Date" )
        self.Season_To_Date = self.Remove_Empty_Lists( self.Season_To_Date )
        #print( self.Season_To_Date )
        #print(json.dumps(self.Season_To_Date, indent=4))
        X_Axis = self.Get_x_axis( self.Season_To_Date )
        # Labels
        Match_Day = [ "Week " + str( Week ) for Week in range( 1, X_Axis ) ]
        #print( Match_Day )

        Chart = self.Generate_Chart( self.Season_To_Date, True )
        Chart.savefig( os.path.dirname(__file__) + r"\chart\\" + self.Team_Name + "-Season to date.jpg", dpi=300, bbox_inches='tight')

    #---------------------------------------------------------------------------------------------------------------#
    # Function: Get_x_axis
    # Goes through the supplied keys, returns the max lenth of the values.  This is the length of the the x-axis
    #---------------------------------------------------------------------------------------------------------------#
    def Get_x_axis( self, Data ):
        Season = 0
        X_Axis = 0
        #print( "Trying to determine x axis" )
        for key, value in Data.items():

            if ( len( Data[key] )  ) > 0: 
                if ( len( Data[key] ) > X_Axis ):
                    Season = key
                    X_Axis = len( Data[key] )

        #print( "Found x axis: " + str( X_Axis ) + " from season: " + str( Season ) )

        return ( X_Axis + 1 )


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Get_y_axis
    # Goes through the supplied data, returns the value of the y-axis
    #---------------------------------------------------------------------------------------------------------------#
    def Get_y_axis( self, Data ):
        Season = 0
        Y_Axis = 0
        #print()
        #print( "Trying to determine y axis" )
        #print()

        for key, value in Data.items():
            # Get the last entry of the current year, and see if it's the largest value
            if ( len( Data[key] )  ) > 0: 
                
                if ( Data[key][len( Data[key] ) - 1] > Y_Axis ):
                    Season = key
                    Y_Axis = Data[key][len( Data[key] ) - 1]
            #print( "Y_Axis is temporarily: " + str( Y_Axis ) ) 

        #print( "Found y axis: " + str( Y_Axis ) + " from season: " + str( Season ) )
        return Y_Axis


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Remove_Empty_Lists
    # Bumpy cannot handle empty lists.  This removes empty lists.  Returns a list
    #---------------------------------------------------------------------------------------------------------------#
    def Remove_Empty_Lists( self, Data ):
        TempCopy = Data.copy()

        for key, value in Data.items():
            #print( Data[key] )
            if ( len( Data[key] ) == 0 ):
                    #print( "Deleting Empty Data[" + str(key) + "] " )
                    del TempCopy[key]
            #if not value:
                #del TempCopy[key]

        return TempCopy


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Generate_Chart
    # Builds a generic bumpy chart, returns the figure to the calling function
    #---------------------------------------------------------------------------------------------------------------#
    def Generate_Chart( self, Data, PartialSeason=False ):
        font_normal = FontManager("https://raw.githubusercontent.com/google/fonts/main/apache/roboto/Roboto%5Bwdth,wght%5D.ttf")
        font_bold = FontManager("https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/RobotoSlab%5Bwght%5D.ttf")

        # Chart descriptors
        bumpy = Bumpy(
            scatter_color="#282A2C",                         # scatter color
            line_color="#252525",                            # line color
            rotate_xticks=90,                                # rotate x-ticks by 90 degrees
            ticklabel_size=50,                               # ticklable font-size
            label_size=20,                                   # label font-size
            show_right=False,                                # show position on the rightside
            plot_labels=True,                                # plot the labels
            alignment_yvalue=0.4,                            # y label alignment
            alignment_xvalue=0.065,                          # x label alignment,
            scatter_size=15,                                 # size of the marker
            scatter_points='o'
            #scatter_primary='D',                            # marker to be used
            #scatter_points='D',                             # other markers
            #scatter_primary='o',                            # marker to be used for teams
        )
        Y_Axis = self.Get_y_axis( Data )
        X_Axis = self.Get_x_axis( Data )

        # Labels
        Readable_X_Axis = []
        for Week in range ( 1, X_Axis ):
            if ( Week == X_Axis + 1 ):
                Readable_X_Axis.append( "" )
            else:
                Readable_X_Axis.append( "Week " + str( Week ) )

        #Match_Day = [ "Week " + str( Week ) for Week in range( 1, X_Axis ) ]
        #print( Match_Day )


        #y_axis = [ " " + str( Week ) for Week in range( 1, y_Height ) ],
        # This is an attend to space out the y_axis - it was too busy
        Readable_Y_Axis = []
        for Week in range ( 1, Y_Axis + 1 ):
            #if ( ( Week % 5 == 0 ) or ( Week == 1 ) or ( Week == Y_Axis ) ):
            if ( ( Week % 5 == 0 ) or ( Week == 1 ) ):
                Readable_Y_Axis.append( " " + str( Week ) )
            else:
                Readable_Y_Axis.append( "" )

        # Verifying the y-axis
        #print ( Readable_Y_Axis )
 
        if ( PartialSeason ):
            Subtitle_y = "Number of Points Each Season through " + str( X_Axis - 1 ) + " games"
        else: 
            Subtitle_y = "Number of Points Each Season"

        # Plot bumpy chart with actual data
        fig, ax = bumpy.plot(
            x_list= Readable_X_Axis,                         # Along the graph, Chart's x-labels
            y_list= Readable_Y_Axis,                         # Along the graph, Chart's y-Labels
            values=Data,                                     # values having positions for each team
            secondary_alpha=.5,                              # alpha value for non-shaded lines/markers
            highlight_dict=self.Colors,                      # team to be highlighted with their colors
            figsize=( 16, 8 ),                               # size of the chart
            x_label='Match Week',                            # x-label
            y_label=Subtitle_y,                              # y-label
            ylim=( -0.1, Y_Axis ),                           # y-axis heighest point
            lw=1.0,                                          # linewidth of the connecting lines
            upside_down=True,                                # Start charting from the bottom
            fontproperties=font_normal.prop,                 # fontproperties for ticklables/labels
            #fontfamily="Liberation Serif"
        )

        # title and subtitle
        if self.Team_Name == "Atlanta":
            TITLE = "<Atlanta> <United>: Season by Season"
            highlight_textprops = [{"color": '#8C0000'},{"color": '#AB9961'}]
        else:
            TITLE = "<" + self.Team_Name + ">" + ": Season by Season"
            highlight_textprops = [{"color": '#FFFFFF'}] 
        #SUB_TITLE = "Season by Season"


        # add title
        #fig.text(0.09, 0.95, TITLE, size=29, color="#F2F2F2", fontproperties=font_bold.prop)

        # Placing the Chart Title
        fig_text(
            0.09, 
            0.95, 
            TITLE, 
            color="#F2F2F2",
            highlight_textprops=highlight_textprops,
            size=29, 
            fig=fig, 
            fontproperties=font_bold.prop
        )

        # Placing the Chart Sub Title
        #fig_text(
        #    0.09, 
        #    0.94, 
        #    SUB_TITLE, 
        #    color="#F2F2F2",
        #    #highlight_textprops=[{"color": '#8C0000'},{"color": '#AB9961'}],
        #    size=25, 
        #    fig=fig, 
        #    fontproperties=font_bold.prop
        #)

        # Add Team Labels to Right
        # Read through Dictionary_Team_Colors 
        Legend = "Seasons"
        Highlight_Label_Properties = []

        # Creating the Legend
        for id, color in self.Colors.items():
            if ( id in Data.keys() ):
                Legend += f"\n<{id}>"
                Highlight_Label_Properties.append({"color": color})


        # Placement of the Legend
        fig_text(
            0.1, 
            0.85, 
            Legend, 
            color="#FFFFFF",
            highlight_textprops=Highlight_Label_Properties,
            size=12, 
            fig=fig, 
            fontproperties=font_normal.prop
        )

        # Overlay an image on top of the chart (fig)
        Logo = add_image(
            Image.open( os.path.dirname(__file__) + r"\pics\ATLUTD_VIPs_180.png" ),
            fig,                                   # The figure being overlayed
            0.86,                                  # left coordinate of picture
            0.17,                                  # bottom coordinate of picture
            0.08,                                  # scale-width of image
            0.08                                   # scale-height of image
        )

        # if space is left in the plot use this
        plt.tight_layout( pad=0.5 )

        return fig

#---------------------------------------------------------------------------------------------------------------#
# Main Processing
#---------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    logging.basicConfig( format='%(asctime)s: %(levelname)s: %(funcName)s - Line %(lineno)d \n\t%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename=os.path.basename(__file__).split(".py")[0] + '.log', encoding='utf-8', filemode="w", level=logging.DEBUG )

    C = Chart( "Atlanta" )
    # Pass in the colors here, loading from file
    C.Load_Colors( os.path.dirname(__file__) + r"\data\Dictionary_Colors_Seasons.json" )
    #C.Load_Colors( os.path.dirname(__file__) + r"\data\Dictionary_Colors_Teams.json" )
    C.Load_Data()
    C.Generate_Internal_Data()

    C.Chart_Season()
    C.Chart_Season_to_Date()

