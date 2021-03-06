# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 19:46:08 2020

@author: jairp
"""

###############################################################################

### 1. Imports 

import re 
import psycopg2 
import pandas as pd
from configparser import ConfigParser

###############################################################################

### 2. Helper Functions 

def config(filename='database.ini', section='postgresql'): 
    """
    Provides configurations for database access
    """
    
    # create a parser 
    parser = ConfigParser() 
    # read config file 
    parser.read(filename) 
    
    # get section, default to postgresql 
    db = {} 
    if parser.has_section(section): 
        params = parser.items(section) # obtain parameters 
        for param in params: 
            db[param[0]] = param[1] # assign params to database 
    else:
        raise Exception("Section {0} not found in the {1} file".format(section, filename)) 
        
    # return the database object 
    return db 


def query_executer(stmt, verbose=True, insert=False): 
    """
    Helper function to help executing a general quer. 
    @params: 
        @ stmt: A SQL statement. Assumed to be correct and end by a semi-colon. 
        @ fetchall: If True, return all the statements 
    """ 
    conn = None # Set up connection
    try: 
        
        ## 1. Set up configurations
        params = config() # read connection parameters 
        conn = psycopg2.connect(**params)  # connect to the PostgreSQL server
        cur = conn.cursor() # create a cursor 
        
        ### 2. Execute query and fetch results 
        cur.execute(stmt) 
        output_df = pd.DataFrame()
        if not insert:
            query_colnames = [desc[0] for desc in cur.description] # fetched colnames
            query_result = cur.fetchall() # result is a list of tuples, the whole relation 
        
            ### 3. Construct dataframe if required
            output_df = pd.DataFrame(query_result, columns=query_colnames) 
            
        ### 4. Verbose: Output query and result 
        if verbose: 
            print("*****************************SQL*****************************")
            print(stmt) 
            if not insert:
                print("***************************OUTPUT****************************")
                print(output_df)
            print("*************************MESSAGES****************************") 
            print(cur.statusmessage)
        
        # close the communication with the PostgreSQL 
        conn.commit()
        cur.close()
        conn.close()
        
        return output_df

    except (Exception, psycopg2.DatabaseError) as error: 
        print(error) 
        print("error occurred\n")
        print("ARGS:{}\n".format(error.args))
        print("Error: ", error)
        print(error.__traceback__)
        print("Context: ", error.__context__)
        
    finally: 
        # verify connection is not empty 
        if conn is not None:  
            conn.close()

    # Return result


