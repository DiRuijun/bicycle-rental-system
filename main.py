# -*- coding: utf-8 -*-

# Import library
import pandas as pd
import sys
import math
from datetime import datetime, timedelta
import os

class Bicycle:
    #Initialization with columns needed for inventory
    def __init__(self, biketype, sn=None, price = 0, priceUnit = None, status="In", contact=None, time_out=None, booked_hours=0, est_time_in=None):
        self.biketype = biketype
        self.sn = sn
        self.price = self.get_price()
        self.priceUnit = self.get_priceUnit()
        self.status = status
        self.contact = contact
        self.time_out = time_out
        self.booked_hours = booked_hours
        self.est_time_in = est_time_in

    #Get price for each bike type    
    def get_price(self):
        type_key = self.biketype.lower()
        price_dict = {"adult": 8,
                      "kid": 6,
                      "tandem": 16,
                      "family": 35,
                      "pgk": 13}
        return price_dict[type_key]
    
    #Get unit for the price of each bike type
    def get_priceUnit(self):
        type_key = self.biketype.lower()
        priceUnit_dict = {"adult": "per hour",
                      "kid": "per hour",
                      "tandem": "per hour",
                      "family": "per hour",
                      "pgk": "per 0.5 hour"}
        return priceUnit_dict[type_key]

class BicycleDA:
    #Initialization
    def __init__(self):
        #initializing and linking the csv database to protected __db
        self.__db = 'bicycle_db.csv'
        #naming the database table
        self.__tableName = "bicycles"
        #columns required in our inventory list
        self.__columns = ['Bike Type', 'Serial Number', 'Price', 'Price Unit', 'Status', 'Contact', 'Time Out', 'Booked Hours', 'Est Time In']
        #loading of database into dataframe
        try:
            df = pd.read_csv(self.__db)
        except FileNotFoundError:
            #Create file when can't find the file
            df = pd.DataFrame(columns=self.__columns)
            df.to_csv(self.__db, index=False)
    
    #Initialization of sales csv
    def initsales(self,todaydate):
        #sales csv
        #sale_list_filename = 'sales_list' + todaydate + '.csv'
        self.__sales = 'sales_list_' + todaydate + '.csv'
        #naming the sales tables
        self.__salestableName = 'sales'
        #columns for sales
        self.__salescolumns = ['Bike Type','Price','Price Unit','Contact','Time','Transaction Type','Amount']
        #loading of database into dataframe
        try:
            sales_df = pd.read_csv(self.__sales)
        except FileNotFoundError:
            #Reset bike inventory status when is a new day
            self.reset_inv()
            #Create file when can't find the file
            sales_df = pd.DataFrame(columns=self.__salescolumns)
            sales_df.to_csv(self.__sales, index=False)
    
    #To reset inventory status
    def reset_inv(self):
        df = pd.read_csv(self.__db) 
        df['Status']='In'
        df['Contact']=None
        df.to_csv(self.__db,index = False)
     
    #Display bike inventory    
    def displayBicycles(self):
        try:
            #Read csv
            df = pd.read_csv(self.__db)
            #Filter bike inventory
            selected_columns = ['Bike Type', 'Serial Number', 'Status','Contact']
            selected_df = df[selected_columns]
            with pd.option_context('display.float_format', '{:.0f}'.format):
                print(selected_df)
            
            # Display bikes with 'in' status
            in_df = df[df['Status'] == 'In'][['Bike Type','Serial Number','Status']]
            in_df_sum=in_df.groupby('Bike Type').size().reset_index(name='Count')                       
            print("\nInformation on Bicycles Available for Rent:")
            print(f"{'Bike Type':<5s}      {'Total Number Avaliable':>5s}")
            for index,row in in_df_sum.iterrows():
                bike_type = row['Bike Type']
                count = row['Count']
                print(f"{bike_type:<10s}  {count:>20d}")
            
            # Display bikes with 'out' status
            out_df = df[df['Status'] == 'Out'][['Serial Number', 'Contact', 'Time Out', 'Booked Hours', 'Est Time In']]
            # Convert all contact input to integer to prevent decimal values
            out_df['Contact'] = out_df['Contact'].apply(lambda x: int(x) if not pd.isna(x) else x)
            with pd.option_context('display.float_format', '{:.2f}'.format):
                print("\nInformation on Rented Bicycles Outside:")
                print(out_df)
        except pd.errors.EmptyDataError:
            print("No data available.")
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
        
    #Create new bike in inventory
    def insertNewBicycle(self, bicycle, bike_quantity):
        try:
            #Read csv
            df = pd.read_csv(self.__db)
            filtered_df = df[df['Bike Type'] == bicycle.biketype]
            for i in range(bike_quantity):  
                type_count = len(filtered_df)
                sn = f"{bicycle.biketype[0].upper()}{type_count + 1:03d}"
                new_row = {
                    'Bike Type': bicycle.biketype,
                    'Serial Number': sn,
                    'Price': bicycle.price,
                    'Price Unit': bicycle.priceUnit,
                    'Status': bicycle.status,
                    'Contact': bicycle.contact,
                    'Time Out': bicycle.time_out,
                    'Booked Hours': bicycle.booked_hours,
                    'Est Time In': bicycle.est_time_in
                }
                new_row = pd.DataFrame(new_row, index=[0])
                df = pd.concat([df,new_row],ignore_index = True)
                filtered_df = df[df['Bike Type'] == bicycle.biketype] 
            #save to bike csv
            df.sort_values(by=['Serial Number'],inplace = True,ignore_index=True)
            df.to_csv(self.__db, index=False)
            print("------- Bicycle added successfully. -------")
        except Exception as e:
            print("Error:", e)
            sys.exit(1)
            
    #To return available bike count
    def get_inv(self,renttype):
        df = pd.read_csv(self.__db)
        available_df = df[(df.Status == 'In') & (df['Bike Type'] == renttype)]
        return(available_df['Serial Number'].count())
    
    #To return specific bike SN status
    def get_sn(self,sn):
        df = pd.read_csv(self.__db)
        available_df = df[(df.Status == 'Out') & (df['Serial Number'] == sn)]
        return(available_df['Status'].count())
    
    #To return the rate for specific bike type
    def get_rate_for_bike_type(self, bike_type):
        bicycle = Bicycle(bike_type)
        # Call the get_price method in Bicycle class to get the rate for the specified bike type
        rate = bicycle.get_price()
        return rate
    
    #Bike rental function
    def rentalfee(self,renttype,duration,curr_time,contact,rent_quantity,todaydate):
        try:
            #Read csv
            df = pd.read_csv(self.__db)
            sales_df = pd.read_csv(self.__sales)
            #Filter df to available & bike type required
            available_df = df[(df.Status == 'In') & (df['Bike Type'] == renttype)]
            #counting of bikes in store for specific type
            avail_count = 0
            for row in available_df.itertuples():
                avail_count+=1
            #Initial variable
            totalprice = 0
            #Check if there are bikes left and the rental quantity is not more than bikes in store
            if available_df.empty == False and avail_count>=rent_quantity:
                print("\nThe rented bike serial number is/are:")
                for i in range (rent_quantity):
                    #To get the first row of filtered bike inventory
                    SN = available_df.loc[available_df.index[i],'Serial Number']
                    df.loc[df['Serial Number']==SN,"Status"] = "Out"
                    df.loc[df['Serial Number']==SN,"Time Out"] = curr_time
                    df.loc[df['Serial Number']==SN,"Contact"] = contact
                    rate = BicycleDA.get_rate_for_bike_type(self, renttype)
                    #Calculate the estimate return time                  
                        
                    if renttype in ['adult', 'kid', 'tandem', 'family']:
                        #round up to next hour
                        round_duration = math.ceil(duration)
                        df.loc[df['Serial Number'] == SN, "Booked Hours"] = int(duration)
                        #saving current time as datetime
                        curr_datetime = datetime.strptime(datetime.strptime(todaydate, '%Y%m%d').strftime('%Y%m%d') + ' ' + curr_time.strftime('%H:%M:%S'),'%Y%m%d %H:%M:%S')
                        time_in = curr_datetime + timedelta(minutes=60 * round_duration)
                        #calculating the overall price based on rental duration
                        pricesum = rate * round_duration
                    elif renttype == "pgk":
                        #round up nearest 30mins
                        round_duration = math.ceil(duration*2)
                        df.loc[df['Serial Number'] == SN, "Booked Hours"] = duration
                        #saving current time as datetime
                        curr_datetime = datetime.strptime(datetime.strptime(todaydate, '%Y%m%d').strftime('%Y%m%d') + ' ' + curr_time.strftime('%H:%M:%S'),'%Y%m%d %H:%M:%S')
                        time_in = curr_datetime + timedelta(minutes=60 * (round_duration/2))
                        #calculating the overall price based on rental duration
                        pricesum = rate * round_duration
                        #the round_duration for pgk is for 30mins block, but should be presented in hours format
                        round_duration = round_duration/2
                    totalprice += pricesum
                    df.loc[df['Serial Number'] == SN, "Est Time In"] = time_in

                    #Update bike inventory status in csv
                    df.to_csv(self.__db,index = False)
                    #Create sales transaction row to save in sales_list csv
                    new_sales = {
                        'Bike Type': df.loc[df['Serial Number']==SN,"Bike Type"],
                        'Serial Number': SN,
                        'Price': df.loc[df['Serial Number']==SN,"Price"],
                        'Price Unit': df.loc[df['Serial Number']==SN,"Price Unit"],
                        'Time':df.loc[df['Serial Number']==SN,"Time Out"],
                        'Transaction Type':"Rental",
                        'Amount':pricesum,
                        'Contact':df.loc[df['Serial Number']==SN,"Contact"]}
                    new_sales = pd.DataFrame(new_sales)
                    #Update sales_list csv
                    sales_df = pd.concat([sales_df,new_sales],ignore_index=True)
                    sales_df.to_csv(self.__sales,index = False)
                    print(SN)
                #Print total amount
                print(f"\nPlease pay ${totalprice} for booking {rent_quantity} {renttype} for {round_duration} hours.")
                
            
            else:
                print(f"We do not have sufficient {renttype} bicycles available.")
                print("Would you like to choose another type to rent? ")
        except Exception as e:
            print("Error:",e)
            sys.exit(1)
    
    #Return bike function            
    def returnbike(self,sn,curr_time,todaydate):
        try:
            #Read csv
            df = pd.read_csv(self.__db)
            sales_df = pd.read_csv(self.__sales)
            #Filter df to rented status and bike serial number
            return_df = df[(df.Status == 'Out') & (df['Serial Number'] == sn)]
            return_type = df.loc[df['Serial Number']==sn,"Bike Type"].iloc[0]
            if return_df.empty == False:
                #To get the first row of filtered bike inventory
                SN = return_df.loc[return_df.index[0],'Serial Number']
                #Calculate exceed duration and convert to hours
                time_in = pd.to_datetime(df.loc[df['Serial Number']==SN,"Est Time In"], format='%Y%m%d %H:%M:%S')
                time_in_str = time_in.iloc[0].strftime('%Y-%m-%d %H:%M')
                #time_in = datetime.strptime(time_in,'%Y%m%d %H:%M:%S')
                curr_datetime = datetime.strptime(datetime.strptime(todaydate, '%Y%m%d').strftime('%Y%m%d') + ' ' + curr_time.strftime('%H:%M:%S'),'%Y%m%d %H:%M:%S')
                #curr_time = pd.to_datetime(curr_time, format='%Y%m%d %H:%M:%S')
                exceed_duration = curr_datetime - time_in
                print(f"\nEstimate return time: {time_in_str}")
                if return_type in ['adult', 'kid', 'tandem', 'family']:
                    exceed_duration = (exceed_duration.dt.total_seconds()/3600).apply(math.ceil).astype(int).iloc[0]
                    print(f"\nThe excess charges is in terms of hourly block. \nThe rounded time difference is {exceed_duration} hours")
                elif return_type == "pgk":
                    exceed_duration = (exceed_duration.dt.total_seconds()/1800).apply(math.ceil).astype(int).iloc[0]
                    exceed_duration_hrs = exceed_duration*0.5
                    print(f"\nThe excess charges is in terms of half hourly block. \nThe rounded time difference is {exceed_duration_hrs} hours.")
                
                #Calculate extra charges
                rate = BicycleDA.get_rate_for_bike_type(self, return_type)
                pricesum = int(rate)*int(exceed_duration)
                curr_time = curr_time.strftime('%H:%M:%S')     
                #Add sales csv trans when there is excess charges
                if exceed_duration>0:
                    if return_type in ['adult', 'kid', 'tandem', 'family']:
                        print(f"Please pay S${pricesum} for a exceed duration of {exceed_duration} hours")
                    elif return_type == "pgk":
                        print(f"Please pay S${pricesum} for a exceed duration of {exceed_duration_hrs} hours")
                    new_sales = {
                        'Bike Type': df.loc[df['Serial Number']==SN,"Bike Type"],
                        'Serial Number': SN,
                        'Price': df.loc[df['Serial Number']==SN,"Price"],
                        'Price Unit': df.loc[df['Serial Number']==SN,"Price Unit"],
                        'Time':curr_time,
                        'Transaction Type':"Excess Hour Charges",
                        'Amount':pricesum,
                        'Contact':df.loc[df['Serial Number']==SN,"Contact"]}
                    new_sales = pd.DataFrame(new_sales)
                    sales_df = pd.concat([sales_df,new_sales],ignore_index=True)
                    sales_df.to_csv(self.__sales,index = False)
                else:
                    print(f"There is no excess charges. The bike {SN} is returned to shop. Thank you.")
                #Reset status
                df.loc[df['Serial Number']==SN,"Status"] = "In"
                df.loc[df['Serial Number']==SN,"Time Out"] = None
                df.loc[df['Serial Number']==SN,"Booked Hours"] = 0
                df.loc[df['Serial Number']==SN,"Est Time In"] = None
                df.loc[df['Serial Number']==SN,"Contact"] = None
                #Update bike csv
                df.to_csv(self.__db,index = False)
            else:
                print("The bike serial number is wrong. Please double check.")
                print("We will return to Main Menu ")
        except Exception as e:
            print("Error:",e)
            sys.exit(1)   
            
    #To generate output sales report as txt file  
    def sales_report_output(self,todaydate):
            file_name = f"SALES_REPORT_{todaydate}.txt"
            file_count = 1
            while os.path.exists(file_name):
                file_name = f"SALES_REPORT_{todaydate}_{file_count}.txt"
                file_count += 1                
            with open(file_name, "w") as file:
                original_stdout = sys.stdout
                sys.stdout = file
                self.salesreport(todaydate)
                sys.stdout = original_stdout
    
    #To generate sales analysis                 
    def salesreport(self, todaydate):
        try:
            # Read csv
            sales_df = pd.read_csv(self.__sales)
            print(f"SALES REPORT     Date: {todaydate}\n")
            
            # I. Total Revenue
            print("I. Total Revenue")
            total_revenue = sales_df["Amount"].sum()
            print(f"The total revenue: ${total_revenue}\n")
            # Revenue by bike type
            bike_types = ["adult", "kid", "tandem", "family", "pgk"]
            revenue_by_types = []
            for bike_type in bike_types:
                revenue_by_type = sales_df[sales_df["Bike Type"] == bike_type]["Amount"].sum()
                revenue_by_types.append(revenue_by_type)
            revenue_proportions = []
            if total_revenue != 0:
                revenue_proportions = [revenue_by_type / total_revenue for revenue_by_type in revenue_by_types]
            else:
                revenue_proportions = [0] * len(revenue_by_types)
            # Table
            max_length = max(len(bike_type) for bike_type in bike_types)
            print("Bike Type\tRevenue\tProportion")
            print("-----------------------------------")
            for i, bike_type in enumerate(bike_types):
                padding = " " * (len("bike_type") - len(bike_type))
                print(f"{bike_type}{padding}\t${revenue_by_types[i]:6.2f}\t{revenue_proportions[i]:06.2%}")
            print("-----------------------------------\n")            
            # Bar chart
            sorted_data = sorted(zip(bike_types, revenue_proportions), key=lambda x: x[1], reverse=True)
            print("Revenue Ranking\n")
            for bike_type, revenue_proportion in sorted_data:
                scaled_amount = int(revenue_proportion * 40)
                bar = "#" * scaled_amount
                space = " " * (max_length - len(bike_type))
                print(f"{bike_type}{space}\t | {bar}  {revenue_proportion:.2%}\n")
                #print(f"{bike_type}{space} | {bar}  {revenue_proportion:.2%}\n")    
            print("\n")
            
            # II. Popularity
            print("II. Popularity")
            total_number = sales_df.shape[0]
            print(f"The total number of bicycles rented: {total_number}\n")
            # Number by bike type
            number_by_types = []
            for bike_type in bike_types:
                number_by_type = sales_df[sales_df["Bike Type"] == bike_type].shape[0]
                number_by_types.append(number_by_type)
            number_proportions = []
            if total_number != 0:
                number_proportions = [number_by_type / total_number for number_by_type in number_by_types]
            else:
                number_proportions = [0] * len(number_by_types)
            # Table
            print("Bike Type\tNumber\tProportion")
            print("-----------------------------------")
            for i, bike_type in enumerate(bike_types):
                padding = " " * (len("bike_type") - len(bike_type))
                padding_2 = " " * (len("Number") - len(str(number_by_type)))
                print(f"{bike_type}{padding}\t{number_by_types[i]}{padding_2}\t{number_proportions[i]:06.2%}")
            print("-----------------------------------\n") 
            # Bar chart
            sorted_number = sorted(zip(bike_types, number_proportions), key=lambda x: x[1], reverse=True)            
            print("Popularity Ranking\n")    
            for bike_type, number_proportion in sorted_number:
                scaled_amount = int(number_proportion * 40)
                bar = "#" * scaled_amount
                space = " " * (max_length - len(bike_type))
                print(f"{bike_type}{space}\t | {bar}  {number_proportion:.2%}\n")
            print("\n")
            
            # III. Hourly Revenue
            print("III. Hourly revenue")                 
            sales_df["Time"] = pd.to_datetime(sales_df["Time"])
            hourly_revenue = sales_df.groupby(sales_df["Time"].dt.hour)["Amount"].sum()
            # Top 3 Hours of Revenue
            if not hourly_revenue.empty:
                top_hours = hourly_revenue.nlargest(3)
                print("Top 3 Hours of Revenue:\n")
                for hour, h_revenue in top_hours.items():
                    print(f"Hour {hour:02}:00 - {hour+1:02}:00: ${h_revenue:.2f}")  
                print("\n")
            else:
                print("Hourly revenue data is empty.\n")
            # Hourly Revenue Plot
            print("Hourly Revenue Plot")
            max_revenue = hourly_revenue.max()
            for hour in range(24):
                hourly_revenue_amount = hourly_revenue.get(hour, 0)
                if hourly_revenue_amount > 0: 
                    scaled_amount = int(hourly_revenue_amount / max_revenue * 40)
                    line = f"{hour:02}:00 - {hour+1:02}:00 | {'*' * scaled_amount} ${hourly_revenue_amount:.2f}"
                    print(line)
            print("\n")
        except Exception as e:
            print("Error:",e)
            sys.exit(1)

#Set a custom exception to be raised when it is necessary to exit the application
class ExitException(Exception):
    pass

class BicycleController:
    def __init__(self):
        print('\n===========================================')
        print('              Welcome to \n    Bicycle Rental Management System!')
        print('============================================')
    
    # Set a function that checks if user input is "exit" every time, in order to allow the user to exit the system anywhere
    def exit_check(self,prompt):
        user_input=input(prompt)
        if user_input.lower()=='exit':
            print("System terminated. Thank you!")
            raise ExitException()
        return user_input
        
    #Main Menu
    def main(self):
        #adding a datetime input to log the current time of logging in
        while True:
            todaydate_input = self.exit_check("Please key in today date: (yyyyMMdd) ")
            try:
                todaydate = datetime.strptime(todaydate_input,'%Y%m%d').strftime('%Y%m%d')
                break
            except ValueError:
                print("Please follow the yyyyMMdd format only!")
            except ExitException:
                sys.exit()
           
        
        #initializing the bicycle inventory object
        bicycle_da = BicycleDA() 
        bicycle_da.initsales(todaydate)
        
        #looping to allow the script to jump back to menu
        while True:
            #menu options
            print("\n===========================================")
            print("1. Display Bicycles")
            print("2. Add New Bicycle")
            print("3. Rental and Payment")
            print("4. Return Rental")
            print("5. Sales Report Today")
            print("X. Exit")
            print("===========================================")
            #getting user input to decide the options
            choice = input("Enter your choice: ")
            choice = choice.strip()
            
            if choice == '1':
                #Display Bicycles
                print("\n")
                bicycle_da.displayBicycles()
            elif choice == '2':
                #Add new bicycles
                while True:
                    try:
                        #Prompt Queestion
                        print("\n===========================================")
                        print("Available bike type: Adult, Kid, Tandem, Family & PGK")
                        print("===========================================")
                        biketype = self.exit_check("Enter Bicycle Type : ")
                        biketype = biketype.lower().strip()
                        #Error Handling
                        if biketype not in ["adult", "kid", "tandem", "family", "pgk"]:
                            print("Please key in correct type!")
                            continue
                        #Get total bike quantity to add
                        bike_quantity = int(self.exit_check("Enter No. of Bicycle to Add: "))
                        break  
                    except ExitException:
                        sys.exit()
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                #Trigger add bicycle module
                new_bicycle = Bicycle(biketype)
                bicycle_da.insertNewBicycle(new_bicycle,bike_quantity)    
                
            elif choice == '3':
                try:
                #Rental and payment
                    print("\n===========================================")
                    print("Available bike type: Adult, Kid, Tandem, Family & PGK")
                    print("===========================================")
                    renttype = self.exit_check("What Bicycle do you want to rent: ").strip()
                    bike_inv = bicycle_da.get_inv(renttype.lower().strip())
                    print(f"\nThere is/are {bike_inv} {renttype} bikes available ")
                except ExitException:
                    sys.exit()
                #Exit option when there is no available bike for rent.
                if bike_inv >0:
                    #Get total rental bike
                    rent_quantity = int(self.exit_check("Enter No. of Bicycle to Rent: ").strip())
                    print("\n===========================================")
                    #Get current timing
                    while True:
                       try:
                           curr_time = datetime.strptime(self.exit_check("What is the current timing? (HH:MM) "),'%H:%M').time()
                           break
                       except ExitException:
                           sys.exit()
                       except:
                           print("Please follow the HH:MM format only!")         
                    #Get rental duration
                    while True:
                        try:
                            print("Note that the rental is in terms of hourly block.")
                            duration = float(self.exit_check("How many hours do you want to rent it for: ").strip())
                            #Round off the duration
                            if renttype.lower().strip() == 'pgk':
                                duration = (math.ceil(duration*2))/2
                            else:
                                duration = math.ceil(duration)
                            print(f"The rental hours is {duration} hours.")
                            break
                        except ExitException:
                            sys.exit()
                        except:
                            print("Please key in hours only!")
                    #Show estimate return time for users and restrict rental if exceed next day
                    curr_datetime = datetime.combine(datetime.strptime(todaydate, "%Y%m%d"),curr_time)
                    est_time_in = curr_datetime + timedelta(minutes=60 * duration)
                    print(f"The estimate return timing is : {est_time_in}")
                    if est_time_in.day >curr_datetime.day:
                        print("The bike will return on next day. PLease reduce the hours and try again.")
                    else:
                        #Proceed if the est return time is before 2359.
                        while True:
                           try:
                               contact = self.exit_check("Please key in the contact number: ")
                               #Validate hp number before save
                               if contact.isdigit():
                                   contact = int(contact)
                                   #Assuming all SG handphone number starts with 8 or 9 and contains 8 digits
                                   # 80000000 - 99999999 can be used as contact number
                                   if 80000000<=contact < 100000000:
                                       print("\n===========================================")
                                       print("Confirmation: ")
                                       print(f"The contact number is : {contact}")
                                       break
                                   else:
                                       print("Please key in the correct contact number format! (8 digits starting with 8 or 9)")
                               else:
                                   print("Please key in the correct contact number format! (8 digits starting with 8 or 9)")
                           except ExitException:
                               sys.exit()
                           except:
                               print("Please key in the correct contact number format! (8 digits starting with 8 or 9)")
                        bicycle_da.rentalfee(renttype.lower(), duration,curr_time,contact,rent_quantity,todaydate)
                else:
                    print("Please select other type of bicycles.")
                    
            elif choice == '4':
                try:
                #Return rental
                    sn = self.exit_check("Key in the returned bike serial number: ")
                    bike_inv = bicycle_da.get_sn(sn.upper().strip())
                except ExitException:
                    sys.exit()
                if bike_inv>0:
                    #Get return time
                    while True:
                       try:
                           curr_time = datetime.strptime(self.exit_check("What is the current timing? (HH:MM) "),'%H:%M').time()
                           break
                       except ExitException:
                           sys.exit()
                       except:
                           print("Please follow the HH:MM format only!")
                    #Trigger return function
                    bicycle_da.returnbike(sn.upper().strip(),curr_time,todaydate)
                else:
                    print("The bike serial number is wrong. Please verify.")
     
            elif choice == '5':
                # Sales Report
                print("\n")
                bicycle_da.salesreport(todaydate)
                try:
                    # Output file
                    while True:
                        # Ask user if a separate .txt file with Sales report is required
                        output_choice = self.exit_check("Do you want to output the report to a text file? (yes/no): ")          
                        # Generate Sales report in .txt file
                        if output_choice.lower().strip() == "yes":                
                            bicycle_da.sales_report_output(todaydate)
                            print("Sales Report has been saved.")
                            break
                        # Does not generate Sales report in .txt file
                        elif output_choice.lower().strip() == "no":
                            print("Report not saved.")
                            break
                        # Exit to main menu
                        elif output_choice.lower().strip() == "x":
                            break               
                        else:
                            print("Invalid choice. Please try again.")
                except ExitException:
                    sys.exit()
                    
            
            elif choice.lower() == 'x':
                #Exit
                print("System terminated. Thank you!")
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    #calling of Controller through BicycleController class object
    Controller = BicycleController()
    Controller.main()
    