# tps-scrape
Script to search the TPS website for phone numbers based on Name, Location, and Age

Input comes from a file named Input.csv containing 5 columns of data:
Fname,Lname,City,AgeBot,AgeTop

Example line input would be:
John,Smith,Houston,50,52

Output is in the form 
Full Name (incl middle), First Name, Last Name, Age, Birth Month/Year, +Up To 10 phone numbers listed on profile

This script includes a captcha detector that requires manual input
