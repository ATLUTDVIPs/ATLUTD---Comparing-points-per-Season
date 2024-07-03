

##### *Points_Per_Season.py*


The purpose of this is to show a comparison between the current season, and previous seasons' point tallies.  This script will output an image based on the latest match day, and the full season.

Season to date
![](https://github.com/ATLUTDVIPs/ATLUTD---Comparing-points-per-Season/blob/0a23d40f3e63589eed64fcd117a5de309604b7a8/pics/Atlanta-Season%20to%20date.jpg)

Full Season Comparisons
![](https://github.com/ATLUTDVIPs/ATLUTD---Comparing-points-per-Season/blob/0a23d40f3e63589eed64fcd117a5de309604b7a8/pics/Atlanta-Entire_Season.jpg)



It is currently setup to run for Atlanta United, and has the ATLUTD VIPs logo.  But it can be changed for any MLS team in the data set.
Data is gathered from https://www.football-data.co.uk/, who freely publishes a .csv file of fixture dates.


I wanted to set and retain the year colors.  With the intent of making certain years stand out.
This is stored in a json file.

```
{
    "2012": "#313F49",
    "2013": "#AF2626",
    "2014": "#EDEB00",
    "2015": "#53ADEB",
    "2016": "#F36600",
    "2017": "#FF9900",
    "2018": "#DD0000",
    "2019": "#6A1FA1",
    "2020": "#6B6B6B",
    "2021": "#0077FF",
    "2022": "#6B6B6B",
    "2023": "#FFCCFF",
    "2024": "#AB9961"
}


```



*Variables*

```
C = Chart( "Atlanta" )
```
By changing the string passed in, the graphics can be displayed for any team in the downloaded data set.


```
# Logo
Logo_Path = os.path.join(os.path.dirname(__file__), r"data\pics", "ATLUTD_VIPs_180.png")
```
This is what I use for the branding.  I was originally displaying team names, but changed it to this as my work was copied.  I may revert back.

