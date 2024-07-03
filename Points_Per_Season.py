# ATLUTD - Comparing points per Season


#---------------------------------------------------------------------------------------------------------------#
# Load Modules
# py -m pip install --upgrade package_name
#---------------------------------------------------------------------------------------------------------------#
# matplotlib mplsoccer==1.1.10
# matplotlib==3.7.1
import numpy as np
import pandas as pd
import requests                                                      # Retrieve data over the internet
import json                                                          # Interacts with json data
#from urllib.request import urlopen
#from highlight_text import fig_text
from mplsoccer import Bumpy, FontManager, add_image                  # Soccer specific charts and graphs
import os                                                            # used to interact with the file system
import matplotlib.pyplot as plt                                      # Save the Chart as a jpg
import sys
import itertools                                                     # used to provide iteration functions
import seaborn as sns                                                # Plotting Styles

from matplotlib.lines import Line2D                                  # Setup graph lines
import datetime                                                      # Work with dates
from matplotlib.offsetbox import OffsetImage, AnnotationBbox         # Display an Image
from PIL import Image                                                # Display an Image

from Logger import CustomLogger                                      # Standardized Logging

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
        self.Logger = CustomLogger( __file__, "Warning" )
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
        self.Logger.Log( f"{os.path.dirname(__file__)}\\data\\football-data.co.uk\\USA.csv", "Debug" )
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
            self.Logger.Log( f"An error has occured while reading the Color data: " + str( e ), "Error" )


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
                self.Logger.Log( row.Season, "Debug" )
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

        Chart = self.Generate_Chart( False )
        Chart.savefig( os.path.dirname(__file__) + r"\charts\\" + self.Team_Name + "-Entire_Season.jpg", dpi=300, bbox_inches='tight')


    #---------------------------------------------------------------------------------------------------------------#
    # Function: Chart_Season_to_Date
    # Chart the data up to the last played date ( as provided by the supplied data )
    #---------------------------------------------------------------------------------------------------------------#
    def Chart_Season_to_Date( self ):
        # Prepare for the Graph
        # Loading Fonts

        print() 
        self.Logger.Log( f"Chart_Season_to_Date" )

        self.Season_To_Date = self.Remove_Empty_Lists( self.Season_To_Date )
        #print( self.Season_To_Date )
        #print(json.dumps(self.Season_To_Date, indent=4))
        X_Axis = self.Get_x_axis( self.Season_To_Date )
        # Labels
        Match_Day = [ "Week " + str( Week ) for Week in range( 1, X_Axis ) ]
        #print( Match_Day )

        Chart = self.Generate_Chart( True )
        Chart.savefig( os.path.dirname(__file__) + r"\charts\\" + self.Team_Name + "-Season to date.jpg", dpi=300, bbox_inches='tight')

    #---------------------------------------------------------------------------------------------------------------#
    # Function: Get_x_axis
    # Goes through the supplied keys, returns the max lenth of the values.  This is the length of the the x-axis
    #---------------------------------------------------------------------------------------------------------------#
    def Get_x_axis( self, Data ):
        Season = 0
        X_Axis = 0
        self.Logger.Log( f"Trying to determine x axis", "Debug" )
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
        self.Logger.Log( f"Trying to determine y axis", "Debug" )
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
    def Generate_Chart( self, PartialSeason=False ):

        # Change the style of plot
        sns.set_theme(style="darkgrid")

        # Get the current year
        Current_Year = datetime.datetime.now().year

        # set figure size
        my_dpi=200
        plt.figure(figsize=(8, 4), facecolor='black', dpi=my_dpi)
        plt.gca().set_facecolor('black')

        Legend_Elements = []
        X_Values = 0
        Max_X = 0
        #print( self.Seasons )
        Current_Season_Games = len( self.Seasons[f"{Current_Year}"] )
        
        for Season, Values in self.Seasons.items():
            #print( Season )
            self.Logger.Log( f"{Season}", "Debug" )
            self.Logger.Log( f"{Values}", "Debug" )
            if ( PartialSeason ):
                X_Values = list( range( 1, Current_Season_Games + 1 ) )
                Values_to_plot = Values[:Current_Season_Games]  # Only take the values up until the number of games in the Current Season
            else:
                X_Values = list( range( 1, len(Values) + 1 ) )
                Values_to_plot = Values
            #print( f"Season: {Season}" )
            #print( f"Values: {Values}" )
            #print( f"Current_Season_Games: {Current_Season_Games}" )
            #print( f"Values_to_plot: {Values_to_plot}" )
                
            if ( Season == str( Current_Year ) ):
                plt.plot( X_Values, Values_to_plot, marker='', color=self.Colors[Season], linewidth=2, alpha=1 )
                Label = f'{Season}'
            else:
                plt.plot( X_Values, Values_to_plot, marker='', color=self.Colors[Season], linewidth=.75, alpha=0.4 )
                Label = f'{Season}'

            if ( PartialSeason ):
                Offset = .1
            else:
                Offset = .5
            Line_Label = f'{Season} - {Values_to_plot[-1]} points'
            plt.text( X_Values[-1] +  Offset, Values_to_plot[-1], Line_Label, ha='left', va='center', fontdict={'family': 'sans-serif', 'color': self.Colors[Season], 'weight': 'normal', 'size': 5})
            # Add the line and label to legend_elements
            Legend_Elements.append( Line2D([0], [0], color=self.Colors[Season], linewidth=2 if Season == str( Current_Year ) else .5, alpha=1 if Season == str( Current_Year ) else 0.6, label=Label) )
            if ( X_Values[-1] > Max_X ):
                Max_X = X_Values[-1]
            #if Season == str( Current_Year ):
            #    Current_Season_Games = len( Values )

        
        # Set the x-axis limits based on the data being plotted
        #plt.xlim( 1, len(X_Values) + 1 )
        plt.autoscale(enable=True, axis='x', tight=True)

        # Default Text Properties
        Text_Properties_Y_Axis         = { 'family': 'sans-serif', "color": '#FFFFFF', 'weight': 'normal', 'size': 6 }
        Text_Properties_X_Axis         = { 'family': 'sans-serif', "color": '#FFFFFF', 'weight': 'normal', 'ha': 'left', 'size': 6 }
        #Text_Properties_Title = { 'family': 'sans-serif', "color": color=self.Colors[Season], 'weight': 'normal', 'size': 8 }
        Text_Properties_Title        = { 'family': 'sans-serif', "color": '#FFFFFF', 'weight': 'normal', 'size': 14 }
        Text_Properties_Axis_Labels  = { 'family': 'sans-serif', "color": '#FFFFFF', 'weight': 'normal', 'size': 10 }

        # Legend
        Legend = plt.legend(handles=Legend_Elements, facecolor='black', loc='upper left', frameon=False, prop={'size': 5, 'family': 'sans-serif', 'weight': 'normal', 'style': 'italic' } )
        # Set legend text color to match the line color dynamically
        for line, text in zip(Legend.get_lines(), Legend.get_texts()):
            text.set_color(line.get_color())


        # X Axis
        plt.xlabel( 'Match Week', fontdict=Text_Properties_Axis_Labels )
        X_Ticks_Positions = list( range( 1, Max_X + 1, 1 ) )
        #X_Ticks_Positions = list( range(1, len(X_Values) + 1) )
        plt.xticks( X_Ticks_Positions, rotation=90, **Text_Properties_X_Axis )

        # Y Axis
        if ( PartialSeason ):
            plt.ylabel( "Number of Points Each Season through " + str( Current_Season_Games ) + " games", fontdict=Text_Properties_Axis_Labels )
            self.Logger.Log( f"Number of Points Each Season through {Current_Season_Games} games" )
            self.Logger.Log( f"#WeAreTheA #ATLUTD" )
            #print( Subtitle_y )
        else: 
            plt.ylabel( "Number of Points Each Season", fontdict=Text_Properties_Axis_Labels )
            self.Logger.Log( f"Number of Points Each Season" )
            self.Logger.Log( f"#WeAreTheA #ATLUTD" )
        
        
        
        #Max_Y = max(value for values in self.Seasons.values() for value in values)  # Determine the maximum value for the y-axis
        #Y_Ticks_Positions = list( range( 0, Max_Y + 5, 5 ) )
        if ( PartialSeason ):
            Max_Y = max( Values_to_plot )  # Determine the maximum value for the y-axis
            Y_Ticks_Positions = list( range( 0, Max_Y + 2, 5 ) )
        else:
            Max_Y = max(value for values in self.Seasons.values() for value in values)  # Determine the maximum value for the y-axis
            Y_Ticks_Positions = list( range( 0, Max_Y + 5, 5 ) )

        #plt.yticks( Y_Ticks_Positions, fontsize=6, color='white' )
        plt.yticks( Y_Ticks_Positions, **Text_Properties_Y_Axis )

        # Title
        if self.Team_Name == "Atlanta":
            #TITLE = "Atlanta United: Season by Season"
            TITLE = f"Season by Season: {self.Team_Name} United"
            #highlight_textprops = [{"color": '#8C0000'},{"color": '#AB9961'}]
            #highlight_textprops = { 'family': 'sans-serif', "color": '#8C0000', 'weight': 'normal', 'size': 10 }
        else:
            TITLE = "<" + self.Team_Name + ">" + ": Season by Season"
            TITLE = f"Season by Season: {self.Team_Name}"
            #highlight_textprops = { 'family': 'sans-serif', "color": '#FFFFFF', 'weight': 'normal', 'size': 10 }
        plt.title( TITLE, fontdict=Text_Properties_Title, loc='left' )


        # Plot
        # Remove grid lines
        plt.grid(False)
        # Turn off individual Axis spines
        Axis = plt.gca()
        Axis.spines['top'].set_visible(False)
        Axis.spines['right'].set_visible(False)
        Axis.spines['bottom'].set_visible(True)
        Axis.spines['left'].set_visible(True)
        Axis.spines['bottom'].set_linewidth(0.25)   # Adjust the linewidth as needed
        Axis.spines['left'].set_linewidth(0.25)     # Adjust the linewidth as needed


        # Logo
        Logo_Path = os.path.join(os.path.dirname(__file__), r"data\pics", "ATLUTD_VIPs_180.png")
        Logo_Image = Image.open(Logo_Path)
        ImageBox = OffsetImage(Logo_Image, zoom=0.15)  # Adjust the zoom factor as needed
        Image_Annotation = AnnotationBbox(ImageBox, (0.9, 0.08), frameon=False, xycoords='axes fraction', boxcoords="axes fraction")
        plt.gca().add_artist(Image_Annotation)

        #plt.tight_layout()
        #plt.show()
        #sys.exit()

        return plt



#---------------------------------------------------------------------------------------------------------------#
# Main Processing
#---------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':

    C = Chart( "Atlanta" )
    # Pass in the colors here, loading from file
    C.Load_Colors( os.path.dirname(__file__) + r"\data\Dictionaries\Dictionary_Colors_Seasons.json" )
    #C.Load_Colors( os.path.dirname(__file__) + r"\data\Dictionaries\Dictionary_Colors_Teams.json" )
    C.Load_Data()
    C.Generate_Internal_Data()

    C.Chart_Season()
    C.Chart_Season_to_Date()

    

